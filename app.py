"""
Confidence Coach - Backend API
Helps first-time TikTok creators overcome the "freeze" moment

Target Segment: 0-1K followers, high watch time, never posted or abandoned 3+ recordings
Core Insight: High motivation, low ability at the critical moment

Stack: Local Whisper (free) + Claude API (better conversational tone than GPT-4)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
from dotenv import load_dotenv
import os
import tempfile
import subprocess
import whisper
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Claude client
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Load Whisper model (runs locally - no API needed)
print("Loading Whisper model (this may take a minute first time)...")
whisper_model = whisper.load_model("base")
print("Whisper model loaded!")


# === CORE FUNCTIONS ===

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio using LOCAL Whisper with word-level timestamps.
    Returns transcript text and word timings for pause detection.

    Why local Whisper vs. API:
    - Free (no per-minute cost)
    - Privacy (audio never leaves server)
    - Works offline
    """
    # Convert to wav for better Whisper performance
    wav_path = audio_path.replace(".webm", ".wav")

    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", audio_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Audio conversion failed: {result.stderr}")

    # Transcribe with local Whisper
    result = whisper_model.transcribe(
        wav_path,
        word_timestamps=True,
        verbose=False
    )

    # Extract word-level data
    words = []
    for segment in result["segments"]:
        if "words" in segment:
            for word in segment["words"]:
                words.append({
                    "word": word["word"],
                    "start": word["start"],
                    "end": word["end"]
                })

    # Clean up wav file
    if os.path.exists(wav_path):
        os.remove(wav_path)

    return {
        "text": result["text"],
        "words": words
    }


def detect_pauses(words: list, threshold: float = 3.0) -> list:
    """
    Find gaps > threshold seconds between words.
    These are the "freeze" moments where creators need help.

    B=MAT Application:
    - The pause is the TRIGGER
    - The prompt reduces ABILITY barrier (mental effort)
    - Completion drives MOTIVATION for next attempt
    """
    pauses = []

    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i-1]["end"]

        if gap >= threshold:
            # Get context: last ~15 seconds before the pause
            context = get_context_before(words, i, seconds=15)

            pauses.append({
                "pause_start": round(words[i-1]["end"], 2),
                "pause_end": round(words[i]["start"], 2),
                "duration": round(gap, 2),
                "word_before": words[i-1]["word"],
                "word_after": words[i]["word"],
                "context_before": context
            })

    return pauses


def get_context_before(words: list, index: int, seconds: float = 15) -> str:
    """
    Extract transcript text from ~15 seconds before the pause.
    This context makes prompts SPECIFIC, not generic.

    Key insight: Generic prompts ("you got this!") don't help.
    Context-aware prompts ("what's an example of that?") do.
    """
    if index == 0:
        return ""

    pause_time = words[index]["start"]
    cutoff = pause_time - seconds

    context_words = []
    for w in words[:index]:
        if w["start"] >= cutoff:
            context_words.append(w["word"])

    return " ".join(context_words)


def generate_prompt(context: str, full_transcript: str = "") -> str:
    """
    Generate a continuation prompt using Claude.

    Why Claude vs. GPT-4:
    - Better conversational tone (more natural, less formal)
    - Faster response times
    - Lower cost per token

    Prompt Engineering Principles:
    1. Be SPECIFIC to their topic (not generic encouragement)
    2. Phrase as question or suggestion (actionable)
    3. Conversational tone (matches TikTok vibe)
    4. Under 15 words (quick to read while recording)
    """

    if not context or len(context.strip()) < 10:
        return "What's the main point you want to make?"

    message = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""You help TikTok creators who freeze while recording videos.

Given the last 15 seconds of what they said, generate ONE short prompt (under 15 words) to help them continue naturally.

Rules:
- Be specific to their topic, not generic
- Phrase as a question or gentle suggestion
- Conversational, friendly tone
- No motivational fluff like "you got this"
- No generic prompts like "tell us more"
- Reference something specific they mentioned

Creator was saying: "{context}"

They froze. Give them a specific prompt to continue (just the prompt, nothing else):"""
            }
        ]
    )

    return message.content[0].text.strip().strip('"')


def calculate_metrics(transcript: str, pauses: list, prompts_generated: int) -> dict:
    """
    Calculate metrics for the practice session.

    These tie to our growth loops:
    - Completion signals → feeds confidence flywheel
    - Pause patterns → data flywheel for ML improvement
    """
    word_count = len(transcript.split())
    pause_count = len(pauses)
    total_pause_time = sum(p["duration"] for p in pauses)

    # Fluency score: penalize long/frequent pauses
    # This becomes a gamification lever for habit formation
    if word_count > 0:
        fluency = max(0, 100 - (total_pause_time * 5) - (pause_count * 10))
    else:
        fluency = 0

    return {
        "word_count": word_count,
        "pause_count": pause_count,
        "total_pause_seconds": round(total_pause_time, 1),
        "prompts_generated": prompts_generated,
        "fluency_score": round(fluency)
    }


# === API ROUTES ===

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "confidence-coach"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.

    Flow:
    1. Receive audio recording
    2. Transcribe with LOCAL Whisper (word-level timestamps)
    3. Detect pauses > 3 seconds
    4. Generate context-aware prompts with CLAUDE for each pause
    5. Return results for side-by-side display

    Privacy Design:
    - Audio saved to temp file, deleted immediately after processing
    - Nothing stored permanently
    - Encrypted in transit (HTTPS)
    """
    start_time = time.time()

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Save to temp file (will be deleted)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        audio_path = tmp.name
        audio_file.save(audio_path)

    try:
        # Step 1: Transcribe with local Whisper
        print("Transcribing with local Whisper...")
        transcription = transcribe_audio(audio_path)

        # Step 2: Detect pauses
        pauses = detect_pauses(transcription["words"], threshold=3.0)

        # Step 3: Generate prompts with Claude for each pause
        print(f"Found {len(pauses)} pauses, generating prompts with Claude...")
        for pause in pauses:
            if pause["context_before"]:
                pause["ai_prompt"] = generate_prompt(
                    pause["context_before"],
                    transcription["text"]
                )
            else:
                pause["ai_prompt"] = "What's the main point you want to make?"

        # Step 4: Calculate stats (including duration)
        duration = transcription["words"][-1]["end"] if transcription["words"] else 0

        metrics = calculate_metrics(
            transcription["text"],
            pauses,
            len(pauses)
        )

        # Combine metrics with duration for frontend
        stats = {
            "duration": round(duration, 1),
            "word_count": metrics["word_count"],
            "pause_count": metrics["pause_count"]
        }

        processing_time = round(time.time() - start_time, 2)

        return jsonify({
            "success": True,
            "transcript": transcription["text"],
            "words": transcription["words"],
            "pauses": pauses,
            "stats": stats,
            "processing_time_seconds": processing_time
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # CRITICAL: Delete audio file immediately
        # Privacy commitment: nothing stored
        if os.path.exists(audio_path):
            os.remove(audio_path)


@app.route("/quick-prompt", methods=["POST"])
def quick_prompt():
    """
    Quick prompt generation from text only (no audio).
    Useful for testing prompt quality without full recording flow.
    Uses Claude API.
    """
    data = request.get_json()
    context = data.get("context", "")

    if not context:
        return jsonify({"error": "No context provided"}), 400

    prompt = generate_prompt(context)

    return jsonify({
        "success": True,
        "context": context,
        "prompt": prompt
    })


# === MAIN ===

if __name__ == "__main__":
    print("\n🎤 Confidence Coach API")
    print("=" * 40)
    print("Target: First-time creators (0-1K followers)")
    print("Problem: Freezing mid-recording")
    print("Solution: Context-aware continuation prompts")
    print("Stack: Local Whisper + Claude API")
    print("=" * 40)
    print("\nEndpoints:")
    print("  POST /analyze - Analyze recording, detect pauses, generate prompts")
    print("  POST /quick-prompt - Generate prompt from text context")
    print("  GET  /health - Health check")
    print("\nStarting server on http://localhost:5001")
    print("=" * 40 + "\n")

    # Use PORT from environment (for deployment) or 5001 for local
    port = int(os.getenv("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)

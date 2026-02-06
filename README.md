# 🎤 Confidence Coach

**AI-powered coaching for first-time TikTok creators who freeze mid-recording.**

🔗 **[Live Demo](https://tiktok-confidence-coach.vercel.app/)**

---

## The Problem

95% of TikTok users never post a single video. The blocker isn't motivation or ideas — it's freezing in the moment. Creators start strong, then 10 seconds in... silence. They delete and go back to scrolling.

## The Solution

Confidence Coach detects when creators freeze mid-recording and generates **context-aware AI prompts** to help them continue naturally. Not generic encouragement like "you got this!" — specific prompts based on what they were actually saying.

## How It Works

1. **Record** — Talk about your topic. Don't worry about pausing.
2. **Analyze** — Whisper API transcribes with word-level timestamps. Pauses over 3 seconds are flagged.
3. **Coach** — Claude reads the 15 seconds before each pause and generates a specific continuation prompt.

## Tech Stack

- **Frontend:** HTML/CSS/JS hosted on Vercel
- **Backend:** Flask API hosted on Railway (Dockerized)
- **Transcription:** OpenAI Whisper API (word-level timestamps for pause detection)
- **Coaching:** Claude API (context-aware prompt generation)

## Architecture

```
Recording → Whisper API → Word Timestamps → Pause Detection (>3s gaps)
                                                    ↓
                                        15s context window → Claude API → Coaching Prompt
```

## Success Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **FaT** (First Action Taken) | First prompt acted upon in first session | Activation signal |
| **NaT** (N Actions Taken) | 3+ videos completed in first week | Habit formation |
| **NSM** (North Star) | First-time creator posts per week | 2x completion rate |

## Roadmap

- ✅ **Practice Mode** — Post-recording analysis (live now)
- 🔜 **Real-Time Coaching** — Prompts appear as you pause, sub-2s latency
- 💡 **Niche Discovery** — Suggest topics from watch history
- 💡 **Camera Presence Feedback** — Eye contact, framing, energy analysis
- 💡 **Content Structure AI** — Hook → story → CTA pre-flight checklist

## Privacy

- Audio is sent encrypted to OpenAI's Whisper API and immediately discarded
- Only 15 seconds of text transcript is sent to Claude — no audio, no video
- Nothing is stored. No database, no logs, no history.

---

Built by [Sidharth Sundaram](https://www.linkedin.com/in/sidharthsundaram/) for TikTok AI PM Internship OA · Not affiliated with TikTok Inc. · Powered by Whisper API + Claude API

# Prana Guru - Product Requirements Document

## Original Problem Statement
Build "Prana Guru" - a full-featured spiritual companion mobile app with:
- AI Guru "Prana" with deep Vedic knowledge
- Voice support in 10+ Indian regional languages (Bhashini API)
- Kundali (birth chart) generation with in-house calculations
- Compatibility matching (Ashtakoota 36-point system)
- Numerology analysis
- Guided meditation sessions
- Festival calendar and daily Panchang

## User Personas
1. **Spiritual Seekers** - Looking for guidance based on Indian wisdom traditions
2. **Astrology Enthusiasts** - Wanting Kundali, compatibility, and daily horoscope
3. **Meditation Practitioners** - Seeking guided sessions for peace
4. **Non-typists/Elder Users** - Need voice-first interface in regional languages

## Tech Stack
- **Web App**: React + Tailwind CSS + FastAPI + MongoDB
- **Mobile App**: React Native (iOS & Android)
- **AI**: Gemini 3 Flash via Emergent LLM Key
- **Voice**: OpenAI Whisper (STT) + OpenAI TTS (using Emergent LLM Key)
- **Astrology**: In-house Vedic calculations

## What's Been Implemented (Feb 2026)

### Backend APIs (100% Working)
- User management with spiritual alignment
- AI Chat with Gemini 3 Flash
- Kundali generation (Lagna, Moon sign, Nakshatra, Houses)
- Numerology (Psychic, Destiny, Name numbers)
- Compatibility matching (8-point Ashtakoota)
- Daily horoscope by Moon sign
- Meditation sessions with mood-based recommendations
- Festival calendar (2026) with daily Panchang
- Voice APIs (demo mode without Bhashini key)

### Web App
- WhatsApp-style chat interface
- Onboarding with spiritual alignment
- Admin dashboard with conversation logs

### React Native Mobile App (Code Ready)
Location: `/app/mobile/PranaGuru/`

Screens implemented:
- Welcome & Onboarding screens
- Chat screen with text/voice toggle
- Kundali generation screen
- Compatibility matching screen
- Numerology screen
- Meditation screen with timer
- Calendar/Panchang screen
- Settings with language selection

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| POST /api/chat | AI chat with Prana |
| POST /api/astrology/kundali | Generate birth chart |
| POST /api/astrology/numerology | Numerology analysis |
| POST /api/astrology/compatibility | 8-point matching |
| GET /api/astrology/daily/{rashi} | Daily horoscope |
| GET /api/meditation/sessions | Meditation list |
| GET /api/calendar/festivals | Festival calendar |
| GET /api/calendar/today | Today's Panchang |
| POST /api/voice/stt | Speech-to-text |
| POST /api/voice/tts | Text-to-speech |

## Voice Support
Languages: English, Hindi, Tamil, Telugu, Marathi, Bengali, Kannada, Gujarati, Punjabi, Malayalam

Note: Full voice functionality requires Bhashini API credentials

## Next Tasks
1. **Bhashini Integration**: Add API credentials for full voice support
2. **Mobile Build**: Build APK/IPA for testing on devices
3. **More Scriptures**: Expand from 10 to 50+ curated verses
4. **Proactive Guru**: Calendar integration for personalized reminders
5. **Audio Meditations**: Add actual guided meditation audio files

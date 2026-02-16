# Pocket Guru - Product Requirements Document

## Original Problem Statement
Build "Pocket Guru" - a spiritual guidance AI assistant with a WhatsApp-style chat interface. The bot has a persona of a spiritual guru named "Prana" with deep understanding of Vedic literature, spiritual books, and teachings of Indian religious figures. Customizable according to the user's spiritual alignment (Jnana/Bhakti/Karma/Universal).

## User Personas
1. **Spiritual Seekers** - Looking for guidance based on Indian wisdom traditions
2. **Stressed Professionals** - Seeking peace and moral support
3. **Students of Scriptures** - Wanting to learn from Vedic literature
4. **Universal Spiritualists** - Open to wisdom from all traditions

## Core Requirements (Static)
- WhatsApp-style chat interface
- AI Guru "Prana" with deep Vedic knowledge
- 4 Spiritual alignment paths (Jnana, Bhakti, Karma, Universal)
- Curated scripture database with RAG
- Admin dashboard for conversation logs
- Responsive mobile-first design

## What's Been Implemented (Feb 2026)

### Backend (FastAPI + MongoDB)
- User profile management with spiritual alignment
- Chat endpoint with Gemini 3 Flash AI integration
- Conversation history persistence
- Scripture database (10 curated entries from Gita, Upanishads, Yoga Sutras)
- RAG-style scripture matching based on message themes
- Admin endpoints for stats and conversation logs

### Frontend (React + Tailwind CSS)
- Welcome page with WhatsApp-inspired gradient theme
- 3-step onboarding wizard (Path → Deity → Goal)
- WhatsApp-style chat interface with:
  - Guru avatar and typing indicator
  - User/Guru message bubbles
  - Shloka cards for scripture quotes
  - Quick prompt suggestions
- Conversation sidebar (desktop) / Sheet (mobile)
- Admin dashboard with:
  - Stats cards (users, conversations, alignment breakdown)
  - Conversation logs table with filtering
  - Conversation detail view dialog

### Design System
- Fonts: Cormorant Garamond (headings), Lato (body), Martel (Sanskrit)
- Colors: WhatsApp green (#128C7E, #075E54, #25D366) + Saffron accent
- WhatsApp-style chat bubbles and background pattern

## Prioritized Backlog

### P0 (Critical)
- ✅ Core chat functionality
- ✅ Onboarding flow
- ✅ Admin dashboard

### P1 (High Priority)
- [ ] Add more scriptures (50+ entries)
- [ ] Crisis detection and safety protocol implementation
- [ ] Conversation export feature

### P2 (Medium Priority)
- [ ] WhatsApp Business API integration (AISensy)
- [ ] Vector embeddings for better RAG
- [ ] User settings page to update preferences
- [ ] Dark mode support

### P3 (Low Priority)
- [ ] Multi-language support (Hindi, Sanskrit)
- [ ] Daily wisdom notifications
- [ ] Meditation timer feature
- [ ] Community features

## Next Tasks
1. Expand scripture database with more curated content
2. Implement crisis detection keywords for safety protocol
3. Add AISensy WhatsApp integration when user provides API key
4. Vector embeddings for improved scripture matching

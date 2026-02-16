from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import httpx
import base64
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import astrology module
from astrology import (
    calculate_kundali, get_numerology, calculate_compatibility,
    get_daily_horoscope, get_rashi, get_nakshatra, RASHIS, NAKSHATRAS
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Bhashini API Configuration
BHASHINI_API_KEY = os.environ.get('BHASHINI_API_KEY', '')
BHASHINI_USER_ID = os.environ.get('BHASHINI_USER_ID', '')

# Create the main app without a prefix
app = FastAPI(title="Prana Guru API", description="Spiritual Companion & Vedic Astrology API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============== MODELS ==============

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alignment: str = Field(default="universal")  # jnana, bhakti, karma, universal
    preferred_deity: Optional[str] = None
    primary_goal: Optional[str] = None
    name: Optional[str] = None
    preferred_language: str = Field(default="en")  # en, hi, ta, te, mr, bn, kn
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    onboarding_complete: bool = False

class UserProfileCreate(BaseModel):
    alignment: str
    preferred_deity: Optional[str] = None
    primary_goal: Optional[str] = None
    name: Optional[str] = None
    preferred_language: str = "en"
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    birth_lat: Optional[float] = None
    birth_lon: Optional[float] = None

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role: str  # user or guru
    content: str
    shloka: Optional[dict] = None  # {sanskrit: str, translation: str, source: str}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "New Conversation"
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: Message
    guru_response: Message

# ============== SCRIPTURE DATA ==============

SCRIPTURES = [
    {
        "id": "gita-2-47",
        "source": "Bhagavad Gita 2.47",
        "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
        "translation": "You have the right to work only, but never to its fruits. Let not the fruits of action be your motive, nor let your attachment be to inaction.",
        "theme": ["karma", "action", "detachment", "duty"],
        "alignment": ["karma", "universal"]
    },
    {
        "id": "gita-6-5",
        "source": "Bhagavad Gita 6.5",
        "sanskrit": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
        "translation": "One must elevate oneself by one's own mind, not degrade oneself. The mind is the friend of the conditioned soul, and his enemy as well.",
        "theme": ["self", "mind", "upliftment", "strength"],
        "alignment": ["jnana", "universal"]
    },
    {
        "id": "gita-9-22",
        "source": "Bhagavad Gita 9.22",
        "sanskrit": "अनन्याश्चिन्तयन्तो मां ये जनाः पर्युपासते।\nतेषां नित्याभियुक्तानां योगक्षेमं वहाम्यहम्॥",
        "translation": "To those who worship Me alone, thinking of no other, to those ever self-controlled, I secure what they lack and preserve what they have.",
        "theme": ["devotion", "surrender", "divine protection", "grace"],
        "alignment": ["bhakti", "universal"]
    },
    {
        "id": "gita-4-7",
        "source": "Bhagavad Gita 4.7",
        "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।\nअभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
        "translation": "Whenever there is a decline of righteousness and rise of unrighteousness, O Arjuna, then I manifest Myself.",
        "theme": ["dharma", "divine intervention", "protection"],
        "alignment": ["bhakti", "karma", "universal"]
    },
    {
        "id": "upanishad-isha-1",
        "source": "Isha Upanishad 1",
        "sanskrit": "ईशावास्यमिदं सर्वं यत्किञ्च जगत्यां जगत्।\nतेन त्यक्तेन भुञ्जीथा मा गृधः कस्यस्विद्धनम्॥",
        "translation": "All this, whatsoever exists in the universe, should be covered by the Lord. Protect yourself through detachment. Do not covet anybody's wealth.",
        "theme": ["detachment", "divine presence", "contentment"],
        "alignment": ["jnana", "universal"]
    },
    {
        "id": "yoga-sutra-1-2",
        "source": "Yoga Sutras 1.2",
        "sanskrit": "योगश्चित्तवृत्तिनिरोधः",
        "translation": "Yoga is the cessation of the modifications of the mind.",
        "theme": ["yoga", "mind control", "stillness", "meditation"],
        "alignment": ["jnana", "universal"]
    },
    {
        "id": "gita-2-14",
        "source": "Bhagavad Gita 2.14",
        "sanskrit": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
        "translation": "O son of Kunti, the contact between the senses and sense objects gives rise to fleeting perceptions of happiness and distress. They come and go like winter and summer. Learn to tolerate them without being disturbed.",
        "theme": ["equanimity", "tolerance", "impermanence", "strength"],
        "alignment": ["jnana", "karma", "universal"]
    },
    {
        "id": "gita-12-13",
        "source": "Bhagavad Gita 12.13-14",
        "sanskrit": "अद्वेष्टा सर्वभूतानां मैत्रः करुण एव च।\nनिर्ममो निरहङ्कारः समदुःखसुखः क्षमी॥",
        "translation": "One who is not envious but is a kind friend to all beings, who does not think himself a proprietor, who is free from false ego, equal in happiness and distress, and forgiving.",
        "theme": ["compassion", "kindness", "equanimity", "forgiveness"],
        "alignment": ["bhakti", "karma", "universal"]
    },
    {
        "id": "guru-granth-ang-1",
        "source": "Guru Granth Sahib, Japji Sahib",
        "sanskrit": "ਇਕ ਓਅੰਕਾਰ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ ਨਿਰਵੈਰੁ",
        "translation": "There is One God, Truth is His Name, He is the Creator, Fearless and without enmity.",
        "theme": ["oneness", "truth", "fearlessness"],
        "alignment": ["universal"]
    },
    {
        "id": "gita-18-66",
        "source": "Bhagavad Gita 18.66",
        "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।\nअहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
        "translation": "Abandon all varieties of dharma and simply surrender unto Me alone. I shall liberate you from all sinful reactions; do not fear.",
        "theme": ["surrender", "liberation", "grace", "faith"],
        "alignment": ["bhakti", "universal"]
    }
]

# ============== SYSTEM PROMPTS ==============

def get_system_prompt(user: dict) -> str:
    alignment = user.get('alignment', 'universal')
    deity = user.get('preferred_deity', 'the Divine')
    goal = user.get('primary_goal', 'spiritual growth')
    
    base_prompt = """You are "Prana," a warm and wise spiritual friend. You have deep knowledge of Vedic wisdom but speak like a caring elder, not a textbook.

CRITICAL STYLE RULES:
1. BE CONVERSATIONAL - Talk like a real person, not a lecture. Use "you" and "I" naturally.
2. KEEP IT SHORT - Max 2-3 sentences per response. This is a chat, not an essay.
3. ASK QUESTIONS - Engage them. "What's weighing on your heart?" or "Tell me more about that."
4. ONE INSIGHT AT A TIME - Don't overwhelm. Share one thought, let them respond.
5. NATURAL SANSKRIT - Only use Sanskrit terms if they flow naturally, always explain briefly.
6. BE WARM - Use gentle phrases like "I hear you", "That's natural", "Many feel this way"
7. AVOID - Long paragraphs, bullet points, formal language, preaching, generic advice

GOOD EXAMPLE:
User: "I feel stressed"
Prana: "I hear you. Stress often visits when we carry too much alone. What's the heaviest thing on your mind right now?"

BAD EXAMPLE (too long/preachy):
"Stress arises when the mind is overwhelmed. In the Bhagavad Gita, Lord Krishna teaches us about equanimity. Here are 5 ways to find peace: 1) Breathe deeply 2) Practice detachment..."

CRISIS PROTOCOL:
If the user expresses thoughts of self-harm, deep clinical depression, or violence:
- Gently say: "I care about you. What you're feeling sounds really heavy. Please talk to someone who can truly help - a counselor or helpline. You matter."

"""

    alignment_prompts = {
        "jnana": f"""ALIGNMENT: Jnana (Knowledge)
You speak like a thoughtful philosopher friend. Ask probing questions. "Have you considered..." "What do you think happens when..." Guide through inquiry, not answers. Reference Ramana Maharshi's "Who am I?" approach conversationally.""",
        
        "bhakti": f"""ALIGNMENT: Bhakti (Devotion) 
You speak like a loving devotee. Warm, heart-centered. Reference {deity} naturally as a loving presence. "You're never alone - {deity} walks with you." Use gentle, poetic phrases but stay conversational.""",
        
        "karma": f"""ALIGNMENT: Karma (Action)
You speak like a practical mentor. Focus on doing, not overthinking. "What's one small step you can take today?" "Focus on the action, not the outcome." Grounded, motivating, no-nonsense but kind.""",
        
        "universal": f"""ALIGNMENT: Universal
You draw from all wisdom traditions naturally. Speak of the Divine, the Universe, inner peace. Inclusive and open. "Every tradition tells us..." Keep it simple and universal."""
    }
    
    return base_prompt + alignment_prompts.get(alignment, alignment_prompts["universal"]) + f"\n\nTheir goal: {goal}. Keep this in mind but don't mention it explicitly."

def find_relevant_scripture(user_message: str, ai_response: str, alignment: str) -> Optional[dict]:
    """Find a relevant scripture based on AI response content and user alignment.
    Returns None if no strong match found - we don't want to force scriptures."""
    import random
    
    combined_text = (user_message + " " + ai_response).lower()
    
    # More specific keyword mapping with weights
    keywords_map = {
        # Stress/Anxiety related
        "stress": ["equanimity", "tolerance", "stillness"],
        "anxious": ["equanimity", "tolerance", "stillness"],
        "overwhelm": ["equanimity", "tolerance"],
        "worry": ["equanimity", "faith"],
        
        # Emotional states
        "lonely": ["divine presence", "devotion", "compassion"],
        "alone": ["divine presence", "oneness"],
        "sad": ["upliftment", "strength", "compassion"],
        "depress": ["upliftment", "strength"],
        "angry": ["forgiveness", "compassion", "equanimity"],
        "fear": ["fearlessness", "faith", "divine protection"],
        "scared": ["fearlessness", "faith"],
        
        # Life situations
        "confus": ["self", "dharma"],
        "lost": ["self", "dharma", "duty"],
        "purpose": ["dharma", "duty", "self"],
        "meaning": ["dharma", "self"],
        "work": ["action", "detachment"],
        "job": ["action", "duty", "detachment"],
        "career": ["duty", "action"],
        "lazy": ["action", "duty"],
        "motivat": ["action", "duty"],
        
        # Relationships
        "relationship": ["compassion", "kindness", "forgiveness"],
        "family": ["dharma", "compassion"],
        "friend": ["compassion", "kindness"],
        "forgive": ["forgiveness", "compassion"],
        
        # Spiritual themes
        "meditat": ["yoga", "mind control", "stillness"],
        "peace": ["stillness", "equanimity"],
        "calm": ["stillness", "equanimity"],
        "surrender": ["surrender", "faith", "grace"],
        "faith": ["faith", "surrender", "devotion"],
        "love": ["devotion", "compassion"],
        "grace": ["grace", "surrender", "divine protection"],
        
        # Detachment/letting go
        "let go": ["detachment", "surrender"],
        "attach": ["detachment", "contentment"],
        "outcome": ["detachment", "action"],
        "result": ["detachment", "action"],
        
        # Death/impermanence
        "death": ["impermanence", "liberation"],
        "imperma": ["impermanence", "tolerance"],
        "change": ["impermanence", "tolerance"],
        
        # Self/identity
        "who am i": ["self"],
        "identity": ["self"],
        "ego": ["self", "detachment"],
    }
    
    # Find matching themes
    relevant_themes = []
    for keyword, themes in keywords_map.items():
        if keyword in combined_text:
            relevant_themes.extend(themes)
    
    # If no themes found, don't return any scripture
    if not relevant_themes:
        return None
    
    # Score scriptures - need minimum threshold
    scored_scriptures = []
    for scripture in SCRIPTURES:
        score = 0
        matched_themes = []
        
        for theme in scripture.get("theme", []):
            if theme in relevant_themes:
                score += 2
                matched_themes.append(theme)
        
        # Alignment bonus
        if alignment in scripture.get("alignment", []):
            score += 1
        
        # Only include if score is meaningful (at least 2 theme matches)
        if score >= 4:
            scored_scriptures.append((score, scripture, matched_themes))
    
    # If no strong matches, return None
    if not scored_scriptures:
        return None
    
    # Sort by score
    scored_scriptures.sort(key=lambda x: x[0], reverse=True)
    
    # Get top matches (same score) and pick randomly to avoid repetition
    top_score = scored_scriptures[0][0]
    top_matches = [s for s in scored_scriptures if s[0] == top_score]
    
    selected = random.choice(top_matches)
    return selected[1]

# ============== API ROUTES ==============

@api_router.get("/")
async def root():
    return {"message": "Pocket Guru API - Namaste!"}

# User Profile Routes
@api_router.post("/users", response_model=UserProfile)
async def create_user(user_data: UserProfileCreate):
    user = UserProfile(
        alignment=user_data.alignment,
        preferred_deity=user_data.preferred_deity,
        primary_goal=user_data.primary_goal,
        name=user_data.name,
        onboarding_complete=True
    )
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    return user

@api_router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    return user

@api_router.put("/users/{user_id}", response_model=UserProfile)
async def update_user(user_id: str, user_data: UserProfileCreate):
    update_doc = user_data.model_dump(exclude_unset=True)
    update_doc['onboarding_complete'] = True
    result = await db.users.update_one({"id": user_id}, {"$set": update_doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return await get_user(user_id)

# Chat Routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Get or create user
    user = await db.users.find_one({"id": request.user_id}, {"_id": 0})
    if not user:
        # Create default user
        user = UserProfile(id=request.user_id).model_dump()
        user['created_at'] = user['created_at'].isoformat()
        await db.users.insert_one(user)
    
    # Get or create conversation
    if request.conversation_id:
        conv = await db.conversations.find_one({"id": request.conversation_id}, {"_id": 0})
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(user_id=request.user_id, title=request.message[:50] + "...").model_dump()
        conv['created_at'] = conv['created_at'].isoformat()
        conv['updated_at'] = conv['updated_at'].isoformat()
        await db.conversations.insert_one(conv)
    
    # Create user message
    user_msg = Message(
        user_id=request.user_id,
        role="user",
        content=request.message
    )
    user_msg_dict = user_msg.model_dump()
    user_msg_dict['timestamp'] = user_msg_dict['timestamp'].isoformat()
    
    # Build context for AI (no scripture injection - let AI respond naturally first)
    system_prompt = get_system_prompt(user)
    
    # Initialize Gemini chat
    chat_instance = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"prana-{request.user_id}-{conv['id']}",
        system_message=system_prompt
    ).with_model("gemini", "gemini-3-flash-preview")
    
    # Get conversation history for context
    recent_messages = conv.get('messages', [])[-6:]  # Last 6 messages for context
    history_context = ""
    if recent_messages:
        history_context = "\n\nRecent conversation:\n"
        for msg in recent_messages:
            role = "User" if msg['role'] == 'user' else "Prana"
            history_context += f"{role}: {msg['content']}\n"
    
    # Send message to AI
    full_prompt = request.message
    if history_context:
        full_prompt = f"{history_context}\n\nUser: {request.message}"
    
    user_message = UserMessage(text=full_prompt)
    
    try:
        response_text = await chat_instance.send_message(user_message)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        response_text = "Namaste. I am experiencing some difficulty at the moment. Please try again, and remember - in moments of pause, we find stillness."
    
    # NOW find relevant scripture based on BOTH user message and AI response
    scripture = find_relevant_scripture(
        request.message, 
        response_text, 
        user.get('alignment', 'universal')
    )
    
    # Create guru response message
    guru_msg = Message(
        user_id=request.user_id,
        role="guru",
        content=response_text,
        shloka=scripture  # Will be None if no strong match
    )
    guru_msg_dict = guru_msg.model_dump()
    guru_msg_dict['timestamp'] = guru_msg_dict['timestamp'].isoformat()
    
    # Update conversation
    await db.conversations.update_one(
        {"id": conv['id']},
        {
            "$push": {"messages": {"$each": [user_msg_dict, guru_msg_dict]}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return ChatResponse(
        conversation_id=conv['id'],
        message=user_msg,
        guru_response=guru_msg
    )

# Conversation Routes
@api_router.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str):
    conversations = await db.conversations.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    return conversations

@api_router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@api_router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    result = await db.conversations.delete_one({"id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}

# Admin Routes
@api_router.get("/admin/conversations")
async def get_all_conversations(limit: int = 50, skip: int = 0):
    conversations = await db.conversations.find(
        {}, 
        {"_id": 0}
    ).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Get user details for each conversation
    result = []
    for conv in conversations:
        user = await db.users.find_one({"id": conv['user_id']}, {"_id": 0})
        result.append({
            **conv,
            "user": user
        })
    
    return result

@api_router.get("/admin/stats")
async def get_admin_stats():
    total_users = await db.users.count_documents({})
    total_conversations = await db.conversations.count_documents({})
    
    # Count by alignment
    alignment_stats = {}
    for alignment in ["jnana", "bhakti", "karma", "universal"]:
        count = await db.users.count_documents({"alignment": alignment})
        alignment_stats[alignment] = count
    
    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "alignment_breakdown": alignment_stats
    }

# Scripture Routes
@api_router.get("/scriptures")
async def get_scriptures():
    return SCRIPTURES

@api_router.get("/scriptures/{scripture_id}")
async def get_scripture(scripture_id: str):
    for scripture in SCRIPTURES:
        if scripture['id'] == scripture_id:
            return scripture
    raise HTTPException(status_code=404, detail="Scripture not found")


# ============== ASTROLOGY ROUTES ==============

class KundaliRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    latitude: float
    longitude: float
    timezone_offset: float = 5.5  # IST default

class NumerologyRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD
    name: Optional[str] = None

class CompatibilityRequest(BaseModel):
    person1_birth_date: str
    person1_birth_time: str
    person1_lat: float
    person1_lon: float
    person2_birth_date: str
    person2_birth_time: str
    person2_lat: float
    person2_lon: float
    timezone_offset: float = 5.5


@api_router.post("/astrology/kundali")
async def generate_kundali(request: KundaliRequest):
    """Generate Kundali (Birth Chart)"""
    try:
        birth_dt = datetime.strptime(f"{request.birth_date} {request.birth_time}", "%Y-%m-%d %H:%M")
        kundali = calculate_kundali(
            birth_dt,
            request.latitude,
            request.longitude,
            request.timezone_offset
        )
        return kundali
    except Exception as e:
        logging.error(f"Kundali error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/astrology/numerology")
async def get_numerology_report(request: NumerologyRequest):
    """Get Numerology Analysis"""
    try:
        birth_dt = datetime.strptime(request.birth_date, "%Y-%m-%d")
        numerology = get_numerology(birth_dt, request.name or "")
        return numerology
    except Exception as e:
        logging.error(f"Numerology error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/astrology/compatibility")
async def check_compatibility(request: CompatibilityRequest):
    """Check compatibility (Kundali Matching)"""
    try:
        # Calculate moon positions for both
        birth1 = datetime.strptime(f"{request.person1_birth_date} {request.person1_birth_time}", "%Y-%m-%d %H:%M")
        birth2 = datetime.strptime(f"{request.person2_birth_date} {request.person2_birth_time}", "%Y-%m-%d %H:%M")
        
        kundali1 = calculate_kundali(birth1, request.person1_lat, request.person1_lon, request.timezone_offset)
        kundali2 = calculate_kundali(birth2, request.person2_lat, request.person2_lon, request.timezone_offset)
        
        moon1_deg = kundali1["moon"]["degree"]
        moon2_deg = kundali2["moon"]["degree"]
        
        compatibility = calculate_compatibility(moon1_deg, moon2_deg)
        
        return {
            "person1_kundali": kundali1,
            "person2_kundali": kundali2,
            "compatibility": compatibility
        }
    except Exception as e:
        logging.error(f"Compatibility error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/astrology/daily/{moon_rashi_index}")
async def get_daily_rashi(moon_rashi_index: int):
    """Get daily horoscope for a Moon sign"""
    if moon_rashi_index < 0 or moon_rashi_index > 11:
        raise HTTPException(status_code=400, detail="Invalid rashi index (0-11)")
    return get_daily_horoscope(moon_rashi_index)


@api_router.get("/astrology/rashis")
async def list_rashis():
    """List all Rashis"""
    return RASHIS


@api_router.get("/astrology/nakshatras")
async def list_nakshatras():
    """List all Nakshatras"""
    return NAKSHATRAS


# ============== VOICE/BHASHINI ROUTES ==============

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi", 
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "kn": "Kannada",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ml": "Malayalam"
}

class VoiceToTextRequest(BaseModel):
    audio_base64: str
    source_language: str = "hi"

class TextToVoiceRequest(BaseModel):
    text: str
    target_language: str = "hi"
    
class TranslateRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str = "hi"


@api_router.get("/voice/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return SUPPORTED_LANGUAGES


@api_router.post("/voice/stt")
async def speech_to_text(request: VoiceToTextRequest):
    """
    Convert speech to text using Bhashini API
    Note: Requires BHASHINI_API_KEY to be set
    """
    if not BHASHINI_API_KEY:
        # Fallback: return mock response for demo
        return {
            "text": "नमस्ते, मुझे आध्यात्मिक मार्गदर्शन चाहिए",
            "language": request.source_language,
            "note": "Demo mode - Bhashini API key not configured"
        }
    
    try:
        # Bhashini ASR Pipeline
        config_url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        
        config_payload = {
            "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": request.source_language}}}],
            "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
        }
        
        async with httpx.AsyncClient() as client:
            # Get pipeline config
            config_resp = await client.post(
                config_url,
                json=config_payload,
                headers={
                    "Content-Type": "application/json",
                    "userID": BHASHINI_USER_ID,
                    "ulcaApiKey": BHASHINI_API_KEY
                }
            )
            config_data = config_resp.json()
            
            # Call inference endpoint
            inference_url = config_data.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl")
            inference_key = config_data.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value")
            
            if inference_url:
                inference_payload = {
                    "pipelineTasks": [{"taskType": "asr", "config": {"language": {"sourceLanguage": request.source_language}}}],
                    "inputData": {"audio": [{"audioContent": request.audio_base64}]}
                }
                
                asr_resp = await client.post(
                    inference_url,
                    json=inference_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": inference_key
                    }
                )
                asr_data = asr_resp.json()
                
                text = asr_data.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("source", "")
                return {"text": text, "language": request.source_language}
        
        return {"error": "Failed to get pipeline config"}
    except Exception as e:
        logging.error(f"STT Error: {e}")
        return {"error": str(e), "text": "", "language": request.source_language}


@api_router.post("/voice/tts")
async def text_to_speech(request: TextToVoiceRequest):
    """
    Convert text to speech using Bhashini API
    Note: Requires BHASHINI_API_KEY to be set
    """
    if not BHASHINI_API_KEY:
        # Return info for demo mode
        return {
            "audio_base64": "",
            "text": request.text,
            "language": request.target_language,
            "note": "Demo mode - Bhashini API key not configured. Use browser TTS as fallback."
        }
    
    try:
        config_url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        
        config_payload = {
            "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": request.target_language}}}],
            "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
        }
        
        async with httpx.AsyncClient() as client:
            config_resp = await client.post(
                config_url,
                json=config_payload,
                headers={
                    "Content-Type": "application/json",
                    "userID": BHASHINI_USER_ID,
                    "ulcaApiKey": BHASHINI_API_KEY
                }
            )
            config_data = config_resp.json()
            
            inference_url = config_data.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl")
            inference_key = config_data.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value")
            
            if inference_url:
                tts_payload = {
                    "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": request.target_language}, "gender": "female"}}],
                    "inputData": {"input": [{"source": request.text}]}
                }
                
                tts_resp = await client.post(
                    inference_url,
                    json=tts_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": inference_key
                    }
                )
                tts_data = tts_resp.json()
                
                audio = tts_data.get("pipelineResponse", [{}])[0].get("audio", [{}])[0].get("audioContent", "")
                return {"audio_base64": audio, "text": request.text, "language": request.target_language}
        
        return {"error": "Failed to get pipeline config"}
    except Exception as e:
        logging.error(f"TTS Error: {e}")
        return {"error": str(e), "audio_base64": "", "language": request.target_language}


@api_router.post("/voice/translate")
async def translate_text(request: TranslateRequest):
    """Translate text between languages"""
    if not BHASHINI_API_KEY:
        return {
            "original": request.text,
            "translated": request.text,  # Return original in demo mode
            "source_language": request.source_language,
            "target_language": request.target_language,
            "note": "Demo mode - Bhashini API key not configured"
        }
    
    try:
        config_url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        
        config_payload = {
            "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": request.source_language, "targetLanguage": request.target_language}}}],
            "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"}
        }
        
        async with httpx.AsyncClient() as client:
            config_resp = await client.post(
                config_url,
                json=config_payload,
                headers={
                    "Content-Type": "application/json",
                    "userID": BHASHINI_USER_ID,
                    "ulcaApiKey": BHASHINI_API_KEY
                }
            )
            config_data = config_resp.json()
            
            inference_url = config_data.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl")
            inference_key = config_data.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {}).get("value")
            
            if inference_url:
                translate_payload = {
                    "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": request.source_language, "targetLanguage": request.target_language}}}],
                    "inputData": {"input": [{"source": request.text}]}
                }
                
                trans_resp = await client.post(
                    inference_url,
                    json=translate_payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": inference_key
                    }
                )
                trans_data = trans_resp.json()
                
                translated = trans_data.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("target", "")
                return {
                    "original": request.text,
                    "translated": translated,
                    "source_language": request.source_language,
                    "target_language": request.target_language
                }
        
        return {"error": "Failed to get pipeline config"}
    except Exception as e:
        logging.error(f"Translation Error: {e}")
        return {"error": str(e)}


# ============== MEDITATION ROUTES ==============

MEDITATION_SESSIONS = [
    {
        "id": "peace-5min",
        "name": "Shanti Dhyana",
        "name_hi": "शांति ध्यान",
        "duration_minutes": 5,
        "category": "peace",
        "description": "A short meditation for inner peace and calm",
        "suitable_for": ["stress", "anxiety", "beginners"]
    },
    {
        "id": "morning-10min",
        "name": "Pratah Dhyana",
        "name_hi": "प्रातः ध्यान",
        "duration_minutes": 10,
        "category": "morning",
        "description": "Start your day with clarity and intention",
        "suitable_for": ["morning", "energy", "focus"]
    },
    {
        "id": "sleep-15min",
        "name": "Nidra Dhyana",
        "name_hi": "निद्रा ध्यान",
        "duration_minutes": 15,
        "category": "sleep",
        "description": "Gentle meditation for restful sleep",
        "suitable_for": ["insomnia", "relaxation", "night"]
    },
    {
        "id": "breath-10min",
        "name": "Pranayama",
        "name_hi": "प्राणायाम",
        "duration_minutes": 10,
        "category": "breath",
        "description": "Breathing exercises for vital energy",
        "suitable_for": ["energy", "focus", "health"]
    },
    {
        "id": "gratitude-5min",
        "name": "Kritagyata Dhyana",
        "name_hi": "कृतज्ञता ध्यान",
        "duration_minutes": 5,
        "category": "gratitude",
        "description": "Cultivate gratitude and positivity",
        "suitable_for": ["depression", "negativity", "morning"]
    }
]

FESTIVALS_2026 = [
    {"date": "2026-01-14", "name": "Makar Sankranti", "name_hi": "मकर संक्रांति", "type": "major"},
    {"date": "2026-01-26", "name": "Basant Panchami", "name_hi": "बसंत पंचमी", "type": "festival"},
    {"date": "2026-02-26", "name": "Maha Shivaratri", "name_hi": "महा शिवरात्रि", "type": "major"},
    {"date": "2026-03-14", "name": "Holi", "name_hi": "होली", "type": "major"},
    {"date": "2026-03-30", "name": "Ugadi/Gudi Padwa", "name_hi": "उगादि/गुड़ी पड़वा", "type": "new_year"},
    {"date": "2026-04-02", "name": "Ram Navami", "name_hi": "राम नवमी", "type": "major"},
    {"date": "2026-04-14", "name": "Baisakhi", "name_hi": "बैसाखी", "type": "regional"},
    {"date": "2026-05-07", "name": "Buddha Purnima", "name_hi": "बुद्ध पूर्णिमा", "type": "major"},
    {"date": "2026-07-07", "name": "Guru Purnima", "name_hi": "गुरु पूर्णिमा", "type": "major"},
    {"date": "2026-08-11", "name": "Raksha Bandhan", "name_hi": "रक्षा बंधन", "type": "major"},
    {"date": "2026-08-19", "name": "Janmashtami", "name_hi": "जन्माष्टमी", "type": "major"},
    {"date": "2026-08-27", "name": "Ganesh Chaturthi", "name_hi": "गणेश चतुर्थी", "type": "major"},
    {"date": "2026-09-29", "name": "Navratri Begins", "name_hi": "नवरात्रि प्रारंभ", "type": "major"},
    {"date": "2026-10-08", "name": "Dussehra", "name_hi": "दशहरा", "type": "major"},
    {"date": "2026-10-20", "name": "Karwa Chauth", "name_hi": "करवा चौथ", "type": "festival"},
    {"date": "2026-10-29", "name": "Diwali", "name_hi": "दीवाली", "type": "major"},
    {"date": "2026-11-15", "name": "Guru Nanak Jayanti", "name_hi": "गुरु नानक जयंती", "type": "major"},
]


@api_router.get("/meditation/sessions")
async def get_meditation_sessions(category: Optional[str] = None):
    """Get available meditation sessions"""
    if category:
        return [s for s in MEDITATION_SESSIONS if s["category"] == category]
    return MEDITATION_SESSIONS


@api_router.get("/meditation/recommend/{mood}")
async def recommend_meditation(mood: str):
    """Recommend meditation based on mood"""
    mood_lower = mood.lower()
    recommendations = []
    
    for session in MEDITATION_SESSIONS:
        if any(mood_lower in tag for tag in session["suitable_for"]):
            recommendations.append(session)
    
    if not recommendations:
        # Default recommendation
        recommendations = [MEDITATION_SESSIONS[0]]
    
    return {"mood": mood, "recommendations": recommendations}


@api_router.get("/calendar/festivals")
async def get_festivals(month: Optional[int] = None):
    """Get upcoming festivals"""
    if month:
        return [f for f in FESTIVALS_2026 if int(f["date"].split("-")[1]) == month]
    return FESTIVALS_2026


@api_router.get("/calendar/today")
async def get_today_info():
    """Get today's spiritual info"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Check for festivals
    today_festivals = [f for f in FESTIVALS_2026 if f["date"] == today]
    
    # Tithi calculation (simplified)
    day_of_lunar_month = datetime.now().day % 15
    tithis = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
              "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
              "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"]
    
    return {
        "date": today,
        "tithi": tithis[day_of_lunar_month],
        "festivals": today_festivals,
        "auspicious_time": "06:00-08:00 (Brahma Muhurta)",
        "inauspicious_time": "12:00-13:30 (Rahu Kaal - varies by day)"
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

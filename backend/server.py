from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app without a prefix
app = FastAPI()

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    onboarding_complete: bool = False

class UserProfileCreate(BaseModel):
    alignment: str
    preferred_deity: Optional[str] = None
    primary_goal: Optional[str] = None
    name: Optional[str] = None

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

def find_relevant_scripture(message: str, alignment: str) -> Optional[dict]:
    """Find a relevant scripture based on message content and user alignment"""
    message_lower = message.lower()
    
    keywords_map = {
        "stress": ["detachment", "equanimity", "mind control"],
        "anxious": ["equanimity", "tolerance", "stillness"],
        "lonely": ["divine presence", "devotion", "compassion"],
        "sad": ["upliftment", "strength", "divine protection"],
        "angry": ["forgiveness", "compassion", "equanimity"],
        "confused": ["dharma", "duty", "self"],
        "purpose": ["dharma", "duty", "action"],
        "work": ["karma", "action", "duty", "detachment"],
        "fear": ["fearlessness", "faith", "divine protection"],
        "love": ["devotion", "compassion", "surrender"],
        "death": ["impermanence", "liberation", "self"],
        "meditat": ["yoga", "mind control", "stillness"],
        "peace": ["stillness", "equanimity", "contentment"],
        "relationship": ["compassion", "kindness", "forgiveness"],
        "career": ["karma", "action", "duty"],
        "money": ["contentment", "detachment"],
        "family": ["dharma", "compassion", "duty"]
    }
    
    relevant_themes = []
    for keyword, themes in keywords_map.items():
        if keyword in message_lower:
            relevant_themes.extend(themes)
    
    # Find scriptures matching themes and alignment
    scored_scriptures = []
    for scripture in SCRIPTURES:
        score = 0
        # Check theme match
        for theme in scripture.get("theme", []):
            if theme in relevant_themes:
                score += 2
        # Check alignment match
        if alignment in scripture.get("alignment", []) or "universal" in scripture.get("alignment", []):
            score += 1
        if score > 0:
            scored_scriptures.append((score, scripture))
    
    if scored_scriptures:
        scored_scriptures.sort(key=lambda x: x[0], reverse=True)
        return scored_scriptures[0][1]
    
    # Return a default scripture if no match
    for scripture in SCRIPTURES:
        if alignment in scripture.get("alignment", []) or "universal" in scripture.get("alignment", []):
            return scripture
    return SCRIPTURES[0]

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
    
    # Find relevant scripture
    scripture = find_relevant_scripture(request.message, user.get('alignment', 'universal'))
    
    # Build context for AI
    system_prompt = get_system_prompt(user)
    
    # Add scripture context
    scripture_context = ""
    if scripture:
        scripture_context = f"\n\nRELEVANT SCRIPTURE (use if appropriate):\nSource: {scripture['source']}\nSanskrit: {scripture['sanskrit']}\nTranslation: {scripture['translation']}"
    
    # Initialize Gemini chat
    chat_instance = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"prana-{request.user_id}-{conv['id']}",
        system_message=system_prompt + scripture_context
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
        response_text = "Namaste. I am experiencing some difficulty at the moment. Please try again, and remember - in moments of pause, we find stillness. 🙏"
    
    # Create guru response message
    guru_msg = Message(
        user_id=request.user_id,
        role="guru",
        content=response_text,
        shloka=scripture if scripture else None
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

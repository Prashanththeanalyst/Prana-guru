#!/usr/bin/env python3
"""
Backend API Testing for Pocket Guru
Tests all endpoints with various scenarios
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class PocketGuruAPITester:
    def __init__(self, base_url="https://vedic-companion-2.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.test_user_id = None
        self.test_conversation_id = None
        
    def log_test(self, name: str, passed: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
            
        self.test_results.append({
            "test": name,
            "passed": passed,
            "details": details,
            "response_data": response_data if passed else None
        })
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
            
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            response_json = {}
            
            try:
                response_json = response.json()
                if success:
                    print(f"   Response: {json.dumps(response_json, indent=2)}")
            except:
                if success:
                    print(f"   Response: {response.text}")
                    
            self.log_test(name, success, f"Expected {expected_status}, got {response.status_code}", response_json)
            return success, response_json

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"   Error: {error_msg}")
            self.log_test(name, False, error_msg)
            return False, {}

    def test_root_endpoint(self):
        """Test root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_create_user(self):
        """Test user creation"""
        user_data = {
            "alignment": "universal",
            "preferred_deity": "krishna",
            "primary_goal": "peace",
            "name": f"Test User {datetime.now().strftime('%H%M%S')}"
        }
        
        success, response = self.run_test(
            "Create User",
            "POST",
            "users",
            200,
            data=user_data
        )
        
        if success and 'id' in response:
            self.test_user_id = response['id']
            print(f"   Created user ID: {self.test_user_id}")
            
        return success

    def test_get_user(self):
        """Test getting user by ID"""
        if not self.test_user_id:
            self.log_test("Get User", False, "No test user ID available")
            return False
            
        success, response = self.run_test(
            "Get User",
            "GET",
            f"users/{self.test_user_id}",
            200
        )
        return success

    def test_get_scriptures(self):
        """Test getting scriptures"""
        success, response = self.run_test(
            "Get Scriptures",
            "GET",
            "scriptures",
            200
        )
        
        if success:
            scriptures = response if isinstance(response, list) else []
            print(f"   Found {len(scriptures)} scriptures")
            
        return success

    def test_get_single_scripture(self):
        """Test getting a single scripture"""
        success, response = self.run_test(
            "Get Single Scripture",
            "GET",
            "scriptures/gita-2-47",
            200
        )
        return success

    def test_chat_functionality(self):
        """Test chat functionality"""
        if not self.test_user_id:
            self.log_test("Chat Functionality", False, "No test user ID available")
            return False
            
        chat_data = {
            "user_id": self.test_user_id,
            "message": "Hello Prana, I need guidance on finding inner peace.",
            "conversation_id": None
        }
        
        success, response = self.run_test(
            "Chat - New Conversation",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success and 'conversation_id' in response:
            self.test_conversation_id = response['conversation_id']
            print(f"   Created conversation ID: {self.test_conversation_id}")
            
            # Verify response structure
            if 'guru_response' in response:
                guru_response = response['guru_response']
                if 'content' in guru_response:
                    print(f"   Guru response: {guru_response['content'][:100]}...")
                    
        return success

    def test_chat_continuation(self):
        """Test continuing chat in existing conversation"""
        if not self.test_user_id or not self.test_conversation_id:
            self.log_test("Chat Continuation", False, "Missing user ID or conversation ID")
            return False
            
        chat_data = {
            "user_id": self.test_user_id,
            "message": "Can you share a relevant scripture?",
            "conversation_id": self.test_conversation_id
        }
        
        success, response = self.run_test(
            "Chat - Continue Conversation",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        return success

    def test_get_user_conversations(self):
        """Test getting user conversations"""
        if not self.test_user_id:
            self.log_test("Get User Conversations", False, "No test user ID available")
            return False
            
        success, response = self.run_test(
            "Get User Conversations",
            "GET",
            f"conversations/{self.test_user_id}",
            200
        )
        
        if success:
            conversations = response if isinstance(response, list) else []
            print(f"   Found {len(conversations)} conversations")
            
        return success

    def test_get_single_conversation(self):
        """Test getting a single conversation"""
        if not self.test_conversation_id:
            self.log_test("Get Single Conversation", False, "No test conversation ID available")
            return False
            
        success, response = self.run_test(
            "Get Single Conversation",
            "GET",
            f"conversation/{self.test_conversation_id}",
            200
        )
        
        if success and 'messages' in response:
            messages = response['messages']
            print(f"   Found {len(messages)} messages in conversation")
            
        return success

    def test_admin_stats(self):
        """Test admin stats endpoint"""
        success, response = self.run_test(
            "Admin Stats",
            "GET",
            "admin/stats",
            200
        )
        
        if success:
            expected_keys = ['total_users', 'total_conversations', 'alignment_breakdown']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Admin Stats - Missing {key}", False, f"Response missing {key}")
                    return False
            print(f"   Total users: {response.get('total_users', 0)}")
            print(f"   Total conversations: {response.get('total_conversations', 0)}")
            
        return success

    def test_admin_conversations(self):
        """Test admin conversations endpoint"""
        success, response = self.run_test(
            "Admin Conversations",
            "GET",
            "admin/conversations?limit=10",
            200
        )
        
        if success:
            conversations = response if isinstance(response, list) else []
            print(f"   Found {len(conversations)} admin conversations")
            
        return success

    # ============== ASTROLOGY TESTS ==============
    
    def test_generate_kundali(self):
        """Test Kundali generation"""
        kundali_data = {
            "birth_date": "1995-07-15",
            "birth_time": "10:30",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
        
        success, response = self.run_test(
            "Generate Kundali",
            "POST",
            "astrology/kundali",
            200,
            data=kundali_data
        )
        
        if success:
            expected_keys = ['birth_details', 'lagna', 'sun', 'moon', 'houses', 'ayanamsa']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Kundali - Missing {key}", False, f"Response missing {key}")
                    return False
            print(f"   Generated Kundali for {response.get('birth_details', {}).get('date', 'N/A')}")
            
        return success
    
    def test_get_numerology(self):
        """Test numerology analysis"""
        numerology_data = {
            "birth_date": "1995-07-15",
            "name": "Test User"
        }
        
        success, response = self.run_test(
            "Get Numerology",
            "POST",
            "astrology/numerology",
            200,
            data=numerology_data
        )
        
        if success:
            expected_keys = ['psychic_number', 'destiny_number', 'name_number']
            for key in expected_keys:
                if key not in response:
                    print(f"   Warning: Missing {key} in numerology response")
            print(f"   Psychic Number: {response.get('psychic_number', {}).get('number', 'N/A')}")
            print(f"   Destiny Number: {response.get('destiny_number', {}).get('number', 'N/A')}")
            
        return success
    
    def test_check_compatibility(self):
        """Test compatibility matching"""
        compatibility_data = {
            "person1_birth_date": "1995-07-15",
            "person1_birth_time": "10:30",
            "person1_lat": 28.6139,
            "person1_lon": 77.2090,
            "person2_birth_date": "1996-03-20",
            "person2_birth_time": "14:45",
            "person2_lat": 19.0760,
            "person2_lon": 72.8777,
            "timezone_offset": 5.5
        }
        
        success, response = self.run_test(
            "Check Compatibility",
            "POST",
            "astrology/compatibility",
            200,
            data=compatibility_data
        )
        
        if success:
            expected_keys = ['person1_kundali', 'person2_kundali', 'compatibility']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Compatibility - Missing {key}", False, f"Response missing {key}")
                    return False
            compatibility_score = response.get('compatibility', {}).get('percentage', 0)
            print(f"   Compatibility Score: {compatibility_score}%")
            
        return success
    
    def test_get_daily_horoscope(self):
        """Test daily horoscope for Aries (index 0)"""
        success, response = self.run_test(
            "Get Daily Horoscope - Aries",
            "GET",
            "astrology/daily/0",
            200
        )
        
        if success:
            expected_keys = ['rashi', 'date', 'themes', 'lucky_numbers', 'lucky_colors']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Daily Horoscope - Missing {key}", False, f"Response missing {key}")
                    return False
            print(f"   Horoscope for {response.get('rashi', {}).get('name', 'N/A')} on {response.get('date', 'N/A')}")
            
        return success
    
    def test_get_rashis(self):
        """Test getting all rashis"""
        success, response = self.run_test(
            "Get All Rashis",
            "GET",
            "astrology/rashis",
            200
        )
        
        if success:
            rashis = response if isinstance(response, list) else []
            print(f"   Found {len(rashis)} rashis")
            if len(rashis) != 12:
                self.log_test("Rashis Count", False, f"Expected 12 rashis, got {len(rashis)}")
                return False
            
        return success
    
    def test_get_nakshatras(self):
        """Test getting all nakshatras"""
        success, response = self.run_test(
            "Get All Nakshatras",
            "GET",
            "astrology/nakshatras",
            200
        )
        
        if success:
            nakshatras = response if isinstance(response, list) else []
            print(f"   Found {len(nakshatras)} nakshatras")
            if len(nakshatras) != 27:
                self.log_test("Nakshatras Count", False, f"Expected 27 nakshatras, got {len(nakshatras)}")
                return False
            
        return success

    # ============== MEDITATION TESTS ==============
    
    def test_get_meditation_sessions(self):
        """Test getting meditation sessions"""
        success, response = self.run_test(
            "Get Meditation Sessions",
            "GET",
            "meditation/sessions",
            200
        )
        
        if success:
            sessions = response if isinstance(response, list) else []
            print(f"   Found {len(sessions)} meditation sessions")
            
        return success
    
    def test_recommend_meditation_for_stress(self):
        """Test meditation recommendation for stress"""
        success, response = self.run_test(
            "Recommend Meditation - Stress",
            "GET",
            "meditation/recommend/stress",
            200
        )
        
        if success:
            expected_keys = ['mood', 'recommendations']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Meditation Recommendation - Missing {key}", False, f"Response missing {key}")
                    return False
            recommendations = response.get('recommendations', [])
            print(f"   Found {len(recommendations)} recommendations for stress")
            
        return success

    # ============== CALENDAR TESTS ==============
    
    def test_get_all_festivals(self):
        """Test getting all festivals"""
        success, response = self.run_test(
            "Get All Festivals",
            "GET",
            "calendar/festivals",
            200
        )
        
        if success:
            festivals = response if isinstance(response, list) else []
            print(f"   Found {len(festivals)} festivals")
            
        return success
    
    def test_get_march_festivals(self):
        """Test getting March festivals"""
        success, response = self.run_test(
            "Get March Festivals",
            "GET",
            "calendar/festivals?month=3",
            200
        )
        
        if success:
            festivals = response if isinstance(response, list) else []
            print(f"   Found {len(festivals)} festivals in March")
            
        return success
    
    def test_get_today_panchang(self):
        """Test getting today's panchang info"""
        success, response = self.run_test(
            "Get Today's Panchang",
            "GET",
            "calendar/today",
            200
        )
        
        if success:
            expected_keys = ['date', 'tithi', 'festivals', 'auspicious_time', 'inauspicious_time']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Today's Panchang - Missing {key}", False, f"Response missing {key}")
                    return False
            print(f"   Today's tithi: {response.get('tithi', 'N/A')}")
            
        return success

    # ============== VOICE/OPENAI TTS TESTS ==============
    
    def test_get_supported_languages(self):
        """Test getting supported languages for voice"""
        success, response = self.run_test(
            "Get Supported Languages",
            "GET",
            "voice/languages",
            200
        )
        
        if success:
            languages = response if isinstance(response, dict) else {}
            print(f"   Found {len(languages)} supported languages")
            expected_languages = ['en', 'hi', 'ta', 'te', 'mr', 'bn', 'kn']
            for lang in expected_languages:
                if lang not in languages:
                    print(f"   Warning: Missing expected language {lang}")
            
        return success

    def test_get_available_voices(self):
        """Test getting available TTS voices"""
        success, response = self.run_test(
            "Get Available TTS Voices",
            "GET",
            "voice/voices",
            200
        )
        
        if success:
            voices = response if isinstance(response, dict) else {}
            print(f"   Found {len(voices)} available voices")
            # Check for sage voice specifically mentioned
            if 'sage' not in voices:
                self.log_test("Sage Voice Available", False, "Sage voice not found in available voices")
                return False
            else:
                print(f"   Sage voice: {voices['sage']}")
            
        return success

    def test_text_to_speech_standard(self):
        """Test standard TTS with sage voice"""
        tts_data = {
            "text": "Namaste, welcome to Prana Guru. May you find peace and wisdom in our conversation.",
            "voice": "sage",
            "speed": 0.9
        }
        
        success, response = self.run_test(
            "Text-to-Speech Standard (Sage Voice)",
            "POST",
            "voice/tts",
            200,
            data=tts_data
        )
        
        if success:
            expected_keys = ['audio_base64', 'text', 'voice', 'format', 'model']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"TTS Standard - Missing {key}", False, f"Response missing {key}")
                    return False
            
            # Check if audio_base64 is present and not empty
            if not response.get('audio_base64'):
                self.log_test("TTS Standard - Audio Generation", False, "No audio_base64 in response")
                return False
                
            print(f"   Generated audio for: {response.get('text', '')[:50]}...")
            print(f"   Voice: {response.get('voice', 'N/A')}")
            print(f"   Model: {response.get('model', 'N/A')}")
            print(f"   Format: {response.get('format', 'N/A')}")
            print(f"   Audio data length: {len(response.get('audio_base64', ''))}")
            
        return success

    def test_text_to_speech_hd(self):
        """Test HD quality TTS"""
        tts_data = {
            "text": "Om Shanti Shanti Shanti. May the divine light guide you on your spiritual journey.",
            "voice": "sage",
            "speed": 0.9
        }
        
        success, response = self.run_test(
            "Text-to-Speech HD Quality",
            "POST",
            "voice/tts/hd",
            200,
            data=tts_data
        )
        
        if success:
            expected_keys = ['audio_base64', 'text', 'voice', 'format', 'model']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"TTS HD - Missing {key}", False, f"Response missing {key}")
                    return False
            
            # Verify HD model
            if response.get('model') != 'tts-1-hd':
                self.log_test("TTS HD Model", False, f"Expected tts-1-hd, got {response.get('model')}")
                return False
                
            print(f"   Generated HD audio for: {response.get('text', '')[:50]}...")
            print(f"   HD Model: {response.get('model', 'N/A')}")
            print(f"   Audio data length: {len(response.get('audio_base64', ''))}")
            
        return success

    def test_translate_text(self):
        """Test text translation using Gemini"""
        translate_data = {
            "text": "Hello, how are you today?",
            "source_language": "en",
            "target_language": "hi"
        }
        
        success, response = self.run_test(
            "Translate Text (English to Hindi)",
            "POST",
            "voice/translate",
            200,
            data=translate_data
        )
        
        if success:
            expected_keys = ['original', 'translated', 'source_language', 'target_language']
            for key in expected_keys:
                if key not in response:
                    self.log_test(f"Translation - Missing {key}", False, f"Response missing {key}")
                    return False
            
            print(f"   Original: {response.get('original', '')}")
            print(f"   Translated: {response.get('translated', '')}")
            print(f"   Direction: {response.get('source_language')} → {response.get('target_language')}")
            
            # Check if translation is different from original (basic check)
            if response.get('original') == response.get('translated'):
                print(f"   Warning: Translation appears unchanged")
            
        return success

    def test_tts_error_handling(self):
        """Test TTS with overly long text (should handle gracefully)"""
        long_text = "A" * 5000  # Over the 4096 character limit
        
        tts_data = {
            "text": long_text,
            "voice": "sage",
            "speed": 0.9
        }
        
        # This should return a 400 error for too long text
        success, response = self.run_test(
            "TTS Error Handling (Long Text)",
            "POST",
            "voice/tts",
            400,  # Expecting error
            data=tts_data
        )
        
        return success

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Prana Guru (Updated) Backend API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence - Updated with new astrology, meditation, calendar and voice endpoints
        tests = [
            ("Basic Tests", [
                self.test_root_endpoint,
                self.test_get_scriptures,
                self.test_get_single_scripture,
            ]),
            ("User Management", [
                self.test_create_user,
                self.test_get_user,
            ]),
            ("Chat Functionality", [
                self.test_chat_functionality,
                self.test_chat_continuation,
                self.test_get_user_conversations,
                self.test_get_single_conversation,
            ]),
            ("Astrology Features", [
                self.test_generate_kundali,
                self.test_get_numerology,
                self.test_check_compatibility,
                self.test_get_daily_horoscope,
                self.test_get_rashis,
                self.test_get_nakshatras,
            ]),
            ("Meditation Features", [
                self.test_get_meditation_sessions,
                self.test_recommend_meditation_for_stress,
            ]),
            ("Calendar Features", [
                self.test_get_all_festivals,
                self.test_get_march_festivals,
                self.test_get_today_panchang,
            ]),
            ("Voice Features (OpenAI TTS/STT)", [
                self.test_get_supported_languages,
                self.test_get_available_voices,
                self.test_text_to_speech_standard,
                self.test_text_to_speech_hd,
                self.test_translate_text,
                self.test_tts_error_handling,
            ]),
            ("Admin Functions", [
                self.test_admin_stats,
                self.test_admin_conversations,
            ]),
        ]
        
        for category, test_functions in tests:
            print(f"\n🔸 {category}")
            print("-" * 30)
            for test_func in test_functions:
                try:
                    test_func()
                except Exception as e:
                    print(f"❌ {test_func.__name__} - Exception: {str(e)}")
                    self.tests_run += 1
                    
        self.print_summary()
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        print("=" * 60)

def main():
    """Main test function"""
    tester = PocketGuruAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
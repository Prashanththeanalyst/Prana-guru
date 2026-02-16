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

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Pocket Guru Backend API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
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
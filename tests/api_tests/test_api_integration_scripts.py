#!/usr/bin/env python3
"""
API integration test script

Test DeepSeek API basic connection, JSON response and various API call functionalities
"""

import os
import sys
import json
from pathlib import Path

# Add project root directory to system path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from event_extraction.repository.llm_client import LLMClient
from common.utils.enhanced_logger import EnhancedLogger

# Create logger
logger = EnhancedLogger("api_integration_test", log_level="DEBUG")

def test_basic_api_connection():
    """Test basic API connection"""
    print("="*80)
    print("1. Basic API Connection Test")
    print("="*80)
    
    # Get API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DeepSeek API key not found")
        return False
    
    print(f"✓ Found API key: {api_key[:10]}...")
    
    # Initialize client
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek",
        temperature=0.0
    )
    
    # Test simple call
    print("\nTesting simple text call...")
    system = "You are a helpful AI assistant."
    user = "Please provide a brief introduction to the novel 'A Record of a Mortal's Journey to Immortality'."
    
    response = client.call_llm(system, user)
    print(f"Response successful: {response['success']}")
    
    if response['success']:
        content = response['content']
        print(f"Response length: {len(content)} characters")
        print("Response content preview:")
        print(content[:200] + "..." if len(content) > 200 else content)
        return True
    else:
        print(f"Error message: {response.get('error', 'Unknown error')}")
        return False

def test_json_response():
    """Test JSON format response"""
    print("\n" + "="*80)
    print("2. JSON Response Test")
    print("="*80)
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek"
    )
    
    # Test JSON response
    system = "You are an AI assistant specialized in analyzing novel content. Please reply in JSON format."
    user = """Please analyze the basic information of Han Li, the protagonist of 'A Record of a Mortal's Journey to Immortality', and reply in JSON format:
{
  "name": "Character name",
  "origin": "Background origin",
  "cultivation_type": "Cultivation type",
  "main_characteristics": ["Trait 1", "Trait 2", "Trait 3"]
}"""
    
    response = client.call_with_json_response(system, user)
    print(f"Response successful: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\nJSON content:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # Verify JSON structure
        required_fields = ["name", "origin", "cultivation_type", "main_characteristics"]
        missing_fields = [field for field in required_fields if field not in json_content]
        
        if missing_fields:
            print(f"⚠️  Missing fields: {missing_fields}")
            return False
        else:
            print("✓ JSON structure complete")
            return True
    else:
        print(f"Error message: {response.get('error', 'Unknown error')}")
        if 'content' in response:
            print("Original response content:")
            print(response['content'])
        return False

def test_causal_analysis_api():
    """Test causal analysis API call"""
    print("\n" + "="*80)
    print("3. Causal Analysis API Test")
    print("="*80)
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek"
    )
    
    # Test causal analysis
    system = "You are an AI assistant specialized in analyzing causal relationships between events in 'A Record of a Mortal's Journey to Immortality'. Please reply in JSON format."
    user = """Please analyze whether there is a causal relationship between the following two events:

Event 1: {"event_id": "event_1", "description": "Han Li practices body tempering in the Spirit Cleansing Pool", "characters": ["Han Li"], "treasures": ["Spirit Cleansing Pool"], "location": "Seven Mysteries Sect", "result": "Han Li's physique was significantly enhanced"}

Event 2: {"event_id": "event_2", "description": "Han Li breaks through to the third layer of Qi Condensation", "characters": ["Han Li"], "treasures": [], "location": "Seven Mysteries Sect", "result": "Han Li's cultivation advanced to the third layer of Qi Condensation"}

Please reply in JSON format:
{
  "has_causal_relation": true or false,
  "direction": "event1->event2" or "event2->event1",
  "strength": "high", "medium" or "low",
  "reason": "Brief explanation of the causal relationship reasoning"
}"""
    
    response = client.call_with_json_response(system, user)
    print(f"Response successful: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\nCausal analysis result:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # Verify causal analysis result
        has_causal = json_content.get("has_causal_relation", False)
        if has_causal:
            direction = json_content.get("direction", "")
            strength = json_content.get("strength", "")
            reason = json_content.get("reason", "")
            
            print(f"\n✓ Found causal relationship: {direction}")
            print(f"  Strength: {strength}")
            print(f"  Reason: {reason}")
            return True
        else:
            print("\n- No causal relationship found")
            return True
    else:
        print(f"Error message: {response.get('error', 'Unknown error')}")
        return False

def main():
    """Run API integration tests"""
    print("DeepSeek API Integration Test Suite")
    print("="*80)
    
    tests = [
        ("Basic API Connection", test_basic_api_connection),
        ("JSON Response Format", test_json_response),
        ("Causal Analysis API", test_causal_analysis_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' encountered exception: {str(e)}")
            results.append((test_name, False))
    
    # Output test summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ Passed" if result else "❌ Failed"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API integration tests passed!")
    else:
        print("⚠️  Some tests failed, please check configuration and network connection")

if __name__ == "__main__":
    main()

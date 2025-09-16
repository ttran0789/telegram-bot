import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_webhook_simple():
    """Test the webhook with a simple 'Hello bot' message using environment variables"""
    
    # Use the test webhook URL instead of production
    webhook_url = "https://n8n.lotwizard.us/webhook-test/70422972-329f-471f-8602-7f91e2f94c11"
    
    if not webhook_url:
        print("ERROR: N8N_WEBHOOK_URL not found in environment variables")
        return False
    
    # Simple test message data
    test_data = {
        "type": "message",
        "message_id": 1,
        "text": "Hello bot",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "chat_id": 987654321,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"Testing webhook with message: 'Hello bot'")
    print(f"Webhook URL: {webhook_url}")
    print("-" * 50)
    
    try:
        response = requests.post(
            webhook_url, 
            json=test_data, 
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.content:
            try:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                # Check if there's a reply in the response
                if isinstance(response_json, dict) and 'reply' in response_json:
                    print(f"Bot would reply: '{response_json['reply']}'")
                
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
        else:
            print("Empty response (webhook received but no response)")
        
        success = response.status_code < 400
        print(f"\n{'SUCCESS' if success else 'FAILED'}: Webhook test completed")
        return success
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR sending request: {e}")
        return False

if __name__ == '__main__':
    success = test_webhook_simple()
    exit(0 if success else 1)
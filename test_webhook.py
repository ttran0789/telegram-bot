import requests
import json
from datetime import datetime


def test_webhook():
    """Test the n8n webhook with sample bot data"""
    webhook_url = "https://n8n.lotwizard.us/webhook-test/70422972-329f-471f-8602-7f91e2f94c11"
    
    # Test data mimicking different bot scenarios
    test_cases = [
        {
            "name": "Start Command",
            "data": {
                "type": "command",
                "command": "start",
                "user_id": 123456789,
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "timestamp": datetime.now().isoformat()
            }
        },
        {
            "name": "Text Message",
            "data": {
                "type": "message",
                "message_id": 1,
                "text": "Hello, this is a test message from the bot!",
                "user_id": 123456789,
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "chat_id": 987654321,
                "timestamp": datetime.now().isoformat()
            }
        },
        {
            "name": "Photo Message",
            "data": {
                "type": "photo",
                "message_id": 2,
                "photo_file_id": "BAADBAADrwADBREAAWuWASFAtyS5v0MaAg",
                "caption": "Test photo caption",
                "user_id": 123456789,
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "chat_id": 987654321,
                "timestamp": datetime.now().isoformat()
            }
        },
        {
            "name": "Document Message",
            "data": {
                "type": "document",
                "message_id": 3,
                "document_file_id": "BAADBAADrwADBREAAWuWASFAtyS5v0MaAg",
                "document_name": "test_document.pdf",
                "document_mime_type": "application/pdf",
                "caption": "Test document caption",
                "user_id": 123456789,
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "chat_id": 987654321,
                "timestamp": datetime.now().isoformat()
            }
        }
    ]
    
    print("Testing n8n webhook...")
    print(f"Webhook URL: {webhook_url}")
    print("-" * 50)
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            response = requests.post(
                webhook_url, 
                json=test_case['data'], 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.content:
                try:
                    response_json = response.json()
                    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Response Text: {response.text}")
            else:
                print("Empty response body")
            
            results.append({
                "test": test_case['name'],
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": response.text if response.content else "Empty"
            })
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        print("-" * 30)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    print(f"Successful tests: {successful_tests}/{total_tests}")
    
    for result in results:
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"{status} {result['test']}")
        if not result.get('success', False) and 'error' in result:
            print(f"   Error: {result['error']}")
    
    return successful_tests == total_tests


if __name__ == '__main__':
    success = test_webhook()
    exit(0 if success else 1)
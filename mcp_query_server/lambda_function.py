"""
MCP Server 1 - Conversation Query
Returns latest chatbot conversations as hardcoded JSON data
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any


# Hardcoded conversation data
CONVERSATIONS = [
    {
        "id": "conv_001",
        "user_message": "What is Python?",
        "bot_response": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used for web development, data science, automation, and more.",
        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat() + "Z"
    },
    {
        "id": "conv_002",
        "user_message": "How do I install packages in Python?",
        "bot_response": "Use pip.",
        "timestamp": (datetime.now() - timedelta(hours=4)).isoformat() + "Z"
    },
    {
        "id": "conv_003",
        "user_message": "What is machine learning?",
        "bot_response": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms to identify patterns in data.",
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat() + "Z"
    },
    {
        "id": "conv_004",
        "user_message": "Explain Docker containers",
        "bot_response": "Docker containers are lightweight, standalone packages that include everything needed to run an application: code, runtime, system tools, libraries, and settings. They ensure consistency across different environments.",
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat() + "Z"
    },
    {
        "id": "conv_005",
        "user_message": "What is REST API?",
        "bot_response": "REST API is an architectural style for designing networked applications. It uses HTTP requests to access and manipulate data. RESTful APIs are stateless and use standard HTTP methods like GET, POST, PUT, and DELETE.",
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
    },
    {
        "id": "conv_006",
        "user_message": "How does Git work?",
        "bot_response": "Git tracks changes.",
        "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat() + "Z"
    },
    {
        "id": "conv_007",
        "user_message": "What is AWS Lambda?",
        "bot_response": "AWS Lambda is a serverless compute service that runs your code in response to events and automatically manages the underlying compute resources. You only pay for the compute time you consume.",
        "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat() + "Z"
    },
    {
        "id": "conv_008",
        "user_message": "Explain SQL databases",
        "bot_response": "SQL databases are relational database management systems that use Structured Query Language (SQL) for defining and manipulating data. They organize data into tables with rows and columns.",
        "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat() + "Z"
    },
    {
        "id": "conv_009",
        "user_message": "What is Kubernetes?",
        "bot_response": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications across clusters of hosts.",
        "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat() + "Z"
    },
    {
        "id": "conv_010",
        "user_message": "How do I debug Python code?",
        "bot_response": "Print statements.",
        "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat() + "Z"
    }
]


def query_conversations(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Query the latest conversations
    
    Args:
        limit: Number of conversations to return (default: 5)
        
    Returns:
        List of conversation dictionaries
    """
    # Return the most recent conversations (already sorted by timestamp)
    return CONVERSATIONS[-limit:]


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for conversation query
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Response with conversations data
    """
    try:
        # Parse request body if it exists
        body = {}
        if isinstance(event, dict):
            if 'body' in event:
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
            elif 'limit' in event:
                body = event
        
        # Get limit parameter (default to 5)
        limit = body.get('limit', 5)
        
        # Validate limit
        if not isinstance(limit, int) or limit < 1 or limit > 10:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Invalid limit parameter. Must be between 1 and 10.'
                })
            }
        
        # Query conversations
        conversations = query_conversations(limit)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'count': len(conversations),
                'conversations': conversations
            })
        }
        
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


# For local testing
if __name__ == '__main__':
    # Test with default limit
    print("Test 1: Default limit (5 conversations)")
    result = lambda_handler({}, None)
    print(json.dumps(json.loads(result['body']), indent=2))
    print()
    
    # Test with custom limit
    print("Test 2: Custom limit (3 conversations)")
    result = lambda_handler({'limit': 3}, None)
    print(json.dumps(json.loads(result['body']), indent=2))
    print()
    
    # Test with all conversations
    print("Test 3: All conversations (10)")
    result = lambda_handler({'limit': 10}, None)
    print(json.dumps(json.loads(result['body']), indent=2))

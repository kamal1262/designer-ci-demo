"""
MCP Server 2 - LLM Evaluation
Evaluates chatbot responses using AWS Bedrock Claude 3 Sonnet
"""
import json
import os
import boto3
from typing import Dict, Any


# Initialize Bedrock client
# AWS_REGION is automatically available in Lambda environment
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION', 'us-east-1'))
)

# Model configuration
MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')


def evaluate_response(question: str, answer: str) -> Dict[str, Any]:
    """
    Evaluate a chatbot response using Claude 3 Sonnet
    
    Args:
        question: The user's question
        answer: The chatbot's response
        
    Returns:
        Dictionary with score (1-5) and comment
    """
    # Create evaluation prompt
    prompt = f"""You are an expert evaluator of chatbot responses. Evaluate the following chatbot response on a scale of 1-5.

User Question: {question}

Chatbot Answer: {answer}

Evaluation Criteria:
- Accuracy: Is the answer factually correct?
- Completeness: Does it fully address the question?
- Clarity: Is it easy to understand?
- Helpfulness: Would this help the user?

Provide:
1. A score from 1-5 (1=poor, 5=excellent)
2. A brief comment explaining the score

Respond in JSON format:
{{"score": <number>, "comment": "<explanation>"}}

Your evaluation:"""

    # Prepare request body
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.3,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response
        # Try to find JSON in the response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            evaluation = json.loads(json_str)
            
            # Validate score
            score = evaluation.get('score', 3)
            if not isinstance(score, (int, float)) or score < 1 or score > 5:
                score = 3
            
            return {
                'score': int(score),
                'comment': evaluation.get('comment', 'No comment provided')
            }
        else:
            # Fallback if JSON parsing fails
            return {
                'score': 3,
                'comment': 'Unable to parse evaluation response'
            }
            
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        # Return a default evaluation on error
        return {
            'score': 3,
            'comment': f'Evaluation error: {str(e)}'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for response evaluation
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Response with evaluation score and comment
    """
    try:
        # Parse request body
        body = {}
        if isinstance(event, dict):
            if 'body' in event:
                if isinstance(event['body'], str):
                    body = json.loads(event['body'])
                else:
                    body = event['body']
            elif 'question' in event:
                body = event
        
        # Get question and answer
        question = body.get('question', '')
        answer = body.get('answer', '')
        
        # Validate inputs
        if not question or not answer:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'Both question and answer are required'
                })
            }
        
        # Evaluate response
        evaluation = evaluate_response(question, answer)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'question': question,
                'answer': answer,
                'score': evaluation['score'],
                'comment': evaluation['comment']
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
    # Test cases
    test_cases = [
        {
            'question': 'What is Python?',
            'answer': 'Python is a high-level programming language known for its simplicity.'
        },
        {
            'question': 'How do I install packages in Python?',
            'answer': 'Use pip.'
        },
        {
            'question': 'What is machine learning?',
            'answer': 'Machine learning is a subset of AI that enables systems to learn from data.'
        }
    ]
    
    print("Testing MCP Evaluation Server")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Question: {test['question']}")
        print(f"Answer: {test['answer']}")
        
        result = lambda_handler(test, None)
        response = json.loads(result['body'])
        
        if response.get('success'):
            print(f"Score: {response['score']}/5")
            print(f"Comment: {response['comment']}")
        else:
            print(f"Error: {response.get('error')}")
        print("-" * 60)

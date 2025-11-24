"""
Planner Agent - Orchestrates MCP Servers using Strands Framework
Uses natural language to coordinate intelligent workflows across multiple MCP servers
"""
import json
import os
import argparse
import ssl
from typing import Dict, Any, List
from urllib import request


# MCP Server endpoints from environment variables
MCP_QUERY_URL = 'https://dltsnftnbwnpbqcea3lm4ljdlu0uaaia.lambda-url.us-east-1.on.aws/'
MCP_EVAL_URL = 'https://alq6pflsaerscwzvkxqlyonfki0tzytu.lambda-url.us-east-1.on.aws/'
MCP_GITHUB_URL = 'https://dlxagky44bv6odorc6763yswfa0qnbhp.lambda-url.us-east-1.on.aws/'

# Debug print to verify URLs
# print(f"Using Query URL: {MCP_QUERY_URL}")
# print(f"Using Eval URL: {MCP_EVAL_URL}")
# print(f"Using GitHub URL: {MCP_GITHUB_URL}")

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')


class MCPTool:
    """Wrapper for MCP server tools"""
    
    def __init__(self, name: str, description: str, endpoint: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.endpoint = endpoint
        self.input_schema = input_schema
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Execute the MCP tool"""
        try:
            # Prepare request
            payload = json.dumps(kwargs).encode('utf-8')
            
            req = request.Request(
                self.endpoint,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            # Create SSL context that doesn't verify certificates (for demo purposes)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            # Call MCP server
            with request.urlopen(req, timeout=30, context=ctx) as response:
                result = json.loads(response.read().decode())
                
                # Handle Lambda response format
                if 'body' in result:
                    if isinstance(result['body'], str):
                        return json.loads(result['body'])
                    return result['body']
                
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error calling {self.name}: {str(e)}'
            }


class PlannerAgent:
    """Agent that orchestrates MCP servers with autonomous reasoning"""
    
    def __init__(self, debug: bool = False, custom_prompt: str = None):
        self.debug = debug
        self.custom_prompt = custom_prompt
        
        # Initialize MCP tools with clear descriptions for autonomous reasoning
        self.query_tool = MCPTool(
            name='query_conversations',
            description='Retrieves the latest chatbot conversations with user messages and bot responses. Returns up to 10 most recent conversations.',
            endpoint=MCP_QUERY_URL,
            input_schema={
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of conversations to return (1-10)',
                        'default': 5
                    }
                }
            }
        )
        
        self.eval_tool = MCPTool(
            name='evaluate_response',
            description='Evaluates chatbot responses using AWS Bedrock Claude 3 Sonnet. Returns a score from 1-5 and a detailed comment.',
            endpoint=MCP_EVAL_URL,
            input_schema={
                'type': 'object',
                'properties': {
                    'question': {'type': 'string', 'description': 'The user\'s question'},
                    'answer': {'type': 'string', 'description': 'The chatbot\'s response'}
                },
                'required': ['question', 'answer']
            }
        )
        
        self.github_tool = MCPTool(
            name='submit_prompt_update',
            description='Creates a GitHub pull request to update the system prompt. Only use when evaluation scores are low (<3) or explicitly requested.',
            endpoint=MCP_GITHUB_URL,
            input_schema={
                'type': 'object',
                'properties': {
                    'prompt_text': {'type': 'string', 'description': 'The updated prompt text'},
                    'reason': {'type': 'string', 'description': 'Reason for the update'}
                },
                'required': ['prompt_text']
            }
        )
        
        self.tools = {
            'query_conversations': self.query_tool,
            'evaluate_response': self.eval_tool,
            'submit_prompt_update': self.github_tool
        }
    
    def execute_goal(self, goal: str, stream: bool = True, custom_prompt_override: str = None) -> str:
        """Execute a natural language goal by reasoning about which tools to use"""
        
        if self.debug:
            print(f"\n{'='*60}")
            print(f"Goal: {goal}")
            print(f"{'='*60}\n")
        
        try:
            # Parse the goal and determine actions
            goal_lower = goal.lower()
            
            # Extract number of conversations if specified
            import re
            match = re.search(r'(\d+)\s+(?:chat|conversation)', goal_lower)
            limit = int(match.group(1)) if match else 5
            
            results = []
            
            # Use custom_prompt_override if provided, otherwise use instance custom_prompt
            effective_custom_prompt = custom_prompt_override or self.custom_prompt
            
            # Check if this is a direct PR creation (without review)
            is_direct_pr = (
                ('update prompt' in goal_lower or 'create pr' in goal_lower) and
                'review' not in goal_lower and
                'evaluate' not in goal_lower and
                'get' not in goal_lower and
                'show' not in goal_lower and
                'list' not in goal_lower
            )
            
            if is_direct_pr:
                # Direct PR creation without querying conversations
                if stream:
                    print("\n🚀 Creating PR directly...")
                
                # Use custom prompt if provided, otherwise use default
                if effective_custom_prompt:
                    prompt_text = effective_custom_prompt
                    if stream:
                        print(f"Using custom prompt ({len(prompt_text)} characters)")
                else:
                    prompt_text = """You are a helpful AI assistant focused on providing accurate, complete, and clear responses.

Guidelines:
- Provide comprehensive answers that fully address the user's question
- Use clear, easy-to-understand language
- Include relevant examples when helpful
- Be accurate and factual
- Structure responses logically
- Anticipate follow-up questions

Always aim to be helpful, informative, and user-friendly."""
                
                reason = "Manual prompt update requested"
                
                pr_result = self.github_tool(
                    prompt_text=prompt_text,
                    reason=reason
                )
                
                if pr_result.get('success'):
                    result_msg = f"✓ Created PR: {pr_result.get('pr_url')}"
                    if stream:
                        print(result_msg)
                    return result_msg
                else:
                    error_msg = f"❌ Error creating PR: {pr_result.get('error')}"
                    if stream:
                        print(error_msg)
                    return error_msg
            
            # Step 1: Query conversations
            if self.debug:
                print(f"[Agent] Calling query_conversations(limit={limit})")
            
            query_result = self.query_tool(limit=limit)
            
            if not query_result.get('success'):
                error_msg = f"❌ Error fetching conversations: {query_result.get('error')}"
                if stream:
                    print(error_msg)
                return error_msg
            
            conversations = query_result.get('conversations', [])
            msg = f"✓ Retrieved {len(conversations)} conversations"
            results.append(msg)
            if stream:
                print(f"\n{msg}")
            
            if self.debug:
                print(f"[Agent] Retrieved {len(conversations)} conversations")
            
            # Print conversations if "get", "show", or "list" is in the goal
            if any(keyword in goal_lower for keyword in ['get', 'show', 'list', 'display']):
                if stream:
                    print()  # Empty line
                for conv in conversations:
                    lines = [
                        f"[{conv['id']}] {conv['timestamp']}",
                        f"Q: {conv['user_message']}",
                        f"A: {conv['bot_response']}",
                        ""
                    ]
                    results.extend(lines)
                    if stream:
                        for line in lines:
                            print(line)
            
            # Step 2: Evaluate if requested
            if 'review' in goal_lower or 'evaluate' in goal_lower or 'check' in goal_lower:
                scores = []
                evaluations = []
                
                if self.debug:
                    print(f"[Agent] Evaluating {len(conversations)} responses...")
                
                if stream:
                    print(f"\n📊 Evaluating {len(conversations)} responses...")
                
                for i, conv in enumerate(conversations, 1):
                    if self.debug:
                        print(f"[Agent] Evaluating conversation {i}/{len(conversations)}")
                    
                    if stream:
                        print(f"  Evaluating [{conv['id']}]...", end=" ", flush=True)
                    
                    eval_result = self.eval_tool(
                        question=conv['user_message'],
                        answer=conv['bot_response']
                    )
                    
                    if eval_result.get('success'):
                        score = eval_result.get('score')
                        comment = eval_result.get('comment')
                        scores.append(score)
                        evaluations.append({
                            'id': conv['id'],
                            'score': score,
                            'comment': comment
                        })
                        
                        if stream:
                            print(f"Score: {score}/5")
                        
                        if self.debug:
                            print(f"  [{conv['id']}] Score: {score}/5")
                
                # Calculate average
                if scores:
                    avg_score = sum(scores) / len(scores)
                    
                    eval_header = f"\n📊 Evaluation Results:"
                    avg_line = f"Average score: {avg_score:.1f}/5"
                    results.append(eval_header)
                    results.append(avg_line)
                    
                    if stream:
                        print(eval_header)
                        print(avg_line)
                    
                    # Show individual scores
                    for eval_data in evaluations:
                        score_line = f"\n[{eval_data['id']}] Score: {eval_data['score']}/5"
                        comment_line = f"Comment: {eval_data['comment'][:100]}..."
                        results.append(score_line)
                        results.append(comment_line)
                        
                        if stream:
                            print(score_line)
                            print(comment_line)
                    
                    # Step 3: Create PR if needed
                    # Check for custom score threshold in goal
                    score_threshold_match = re.search(r'if\s+(?:any|average|avg)?\s+score\s+(?:is\s+)?(?:below|<)\s+(\d+(?:\.\d+)?)', goal_lower)
                    custom_threshold = float(score_threshold_match.group(1)) if score_threshold_match else None
                    
                    # Check if any score is below the threshold mentioned in the goal
                    if custom_threshold and any(score < custom_threshold for score in scores):
                        if self.debug:
                            print(f"[Agent] Found scores below threshold {custom_threshold}, creating PR...")
                        should_create_pr = True
                    else:
                        # Use default threshold if no custom threshold is specified
                        should_create_pr = (
                            avg_score < 3.5 or 
                            'update prompt' in goal_lower or 
                            'create pr' in goal_lower or
                            'pull request' in goal_lower
                        )
                    
                    if should_create_pr:
                        if self.debug:
                            print(f"\n[Agent] Average score {avg_score:.1f} is low, creating PR...")
                        
                        if stream:
                            print(f"\n🚀 Creating PR (avg score: {avg_score:.1f})...")
                        
                        # Use custom prompt if provided, otherwise use default
                        if effective_custom_prompt:
                            prompt_text = effective_custom_prompt
                            if stream:
                                print(f"Using custom prompt ({len(prompt_text)} characters)")
                        else:
                            prompt_text = """You are a helpful AI assistant focused on providing accurate, complete, and clear responses.

Guidelines:
- Provide comprehensive answers that fully address the user's question
- Use clear, easy-to-understand language
- Include relevant examples when helpful
- Be accurate and factual
- Structure responses logically
- Anticipate follow-up questions

Always aim to be helpful, informative, and user-friendly."""
                        
                        reason = f"Automated prompt update based on evaluation. Average score: {avg_score:.1f}/5. {len([s for s in scores if s < 3])} conversations scored below 3."
                        
                        pr_result = self.github_tool(
                            prompt_text=prompt_text,
                            reason=reason
                        )
                        
                        if pr_result.get('success'):
                            pr_msg = f"\n✓ Created PR: {pr_result.get('pr_url')}"
                            results.append(pr_msg)
                            if stream:
                                print(pr_msg)
                        else:
                            error_msg = f"\n❌ Error creating PR: {pr_result.get('error')}"
                            results.append(error_msg)
                            if stream:
                                print(error_msg)
                    else:
                        good_msg = f"\n✓ Scores are good, no PR needed"
                        results.append(good_msg)
                        if stream:
                            print(good_msg)
            
            return '\n'.join(results)
            
        except Exception as e:
            error_msg = f"Error executing goal: {str(e)}"
            if self.debug:
                import traceback
                print(f"\n❌ {error_msg}")
                print(traceback.format_exc())
            return error_msg


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Planner Agent - MCP Server Orchestrator')
    parser.add_argument('--goal', type=str, help='Natural language goal to execute')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--prompt', type=str, help='Custom prompt text for PR creation')
    parser.add_argument('--prompt-file', type=str, help='Path to file containing custom prompt text')
    
    args = parser.parse_args()
    
    # Load custom prompt if provided
    custom_prompt = None
    if args.prompt:
        custom_prompt = args.prompt
    elif args.prompt_file:
        try:
            with open(args.prompt_file, 'r') as f:
                custom_prompt = f.read().strip()
        except Exception as e:
            print(f"Error reading prompt file: {e}")
            return
    
    # Initialize agent
    agent = PlannerAgent(debug=args.debug, custom_prompt=custom_prompt)
    
    if args.goal:
        # Execute single goal (streaming disabled for command-line mode to return full result)
        result = agent.execute_goal(args.goal, stream=False)
        print(f"\n{result}\n")
    else:
        # Interactive mode
        print("=" * 60)
        print("Planner Agent - Interactive Mode")
        print("=" * 60)
        print("\nExamples:")
        print("  - Review last 5 chats")
        print("  - Review last 3 conversations and update prompt if needed")
        print("  - Evaluate the most recent conversation")
        print("\nType 'exit' to quit\n")
        
        while True:
            try:
                goal = input("Goal: ").strip()
                
                if goal.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!\n")
                    break
                
                if not goal:
                    continue
                
                # In interactive mode, use streaming for real-time feedback
                result = agent.execute_goal(goal, stream=True)
                print("\n" + "-" * 60)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!\n")
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")


if __name__ == '__main__':
    main()

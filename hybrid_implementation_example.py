"""
Hybrid Architecture Example: Autonomous Agent + LangGraph Workflows

This example demonstrates how the hybrid architecture combining an autonomous agent with
structured LangGraph workflows might be implemented. This is a conceptual implementation.

Note: This code requires langchain, langgraph, and other dependencies to run.
"""
from typing import Dict, Any, List, TypedDict, Literal, Annotated, Union
from enum import Enum
import re
import json
import os
import uuid
from datetime import datetime

# --------------------------------
# AUTONOMOUS AGENT LAYER
# --------------------------------

class AutonomousAgent:
    """Autonomous agent that interprets natural language goals and orchestrates workflows"""
    
    def __init__(self):
        self.workflows = {}
        
    def register_workflow(self, name: str, workflow):
        """Register a LangGraph workflow"""
        self.workflows[name] = workflow
    
    def process_goal(self, goal: str) -> Dict[str, Any]:
        """Process natural language goal and select appropriate workflow"""
        
        # Natural Language Processing
        goal_lower = goal.lower()
        
        # Intent Classification
        intent, params = self._classify_intent(goal_lower)
        
        # Workflow Selection & Orchestration
        return self._orchestrate_workflow(intent, params)
    
    def _classify_intent(self, goal_lower: str) -> tuple:
        """Determine the intent and extract parameters from the goal"""
        
        # Simple rule-based intent classification
        params = {}
        
        # Extract conversation count
        count_match = re.search(r'(\d+)\s+(?:chat|conversation)', goal_lower)
        if count_match:
            params['conversation_count'] = int(count_match.group(1))
        else:
            params['conversation_count'] = 5  # Default
        
        # Extract score threshold
        score_match = re.search(r'(?:score|scores)\s+(?:is|are)\s+(?:below|under|less than)\s+(\d+(?:\.\d+)?)', goal_lower)
        if score_match:
            params['score_threshold'] = float(score_match.group(1))
        else:
            params['score_threshold'] = 3.0  # Default
        
        # Determine intent
        if any(keyword in goal_lower for keyword in ['review', 'evaluate', 'check']):
            if any(keyword in goal_lower for keyword in ['update', 'improve', 'create pr']):
                return 'review_and_update', params
            return 'review_only', params
        
        elif any(keyword in goal_lower for keyword in ['update prompt', 'create pr']):
            return 'direct_update', params
        
        return 'unknown', params
    
    def _orchestrate_workflow(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Select and execute the appropriate workflow"""
        
        if intent == 'review_only':
            if 'review_workflow' in self.workflows:
                params['update_required'] = False
                return self.workflows['review_workflow'].invoke(params)
        
        elif intent == 'review_and_update':
            if 'review_workflow' in self.workflows:
                params['update_required'] = True
                return self.workflows['review_workflow'].invoke(params)
        
        elif intent == 'direct_update':
            if 'update_workflow' in self.workflows:
                return self.workflows['update_workflow'].invoke(params)
        
        return {"error": "No suitable workflow found for intent: " + intent}


# --------------------------------
# LANGGRAPH WORKFLOWS
# --------------------------------

# Required imports for LangGraph 
# from langgraph.graph import StateGraph, END
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI

class ConversationState(TypedDict):
    """State for the conversation review workflow"""
    conversations: List[Dict[str, Any]]
    evaluations: List[Dict[str, Any]]
    average_score: float
    update_required: bool
    approval_required: bool
    approval_status: str
    prompt_text: str
    reason: str
    pr_url: str
    

# Example function for LangGraph nodes
def query_conversations(state: ConversationState) -> ConversationState:
    """Query conversations node in the workflow"""
    count = state.get('conversation_count', 5)
    
    # Simulated query to MCP server
    conversations = [
        {
            "id": f"conv_{i+1:03d}",
            "user_message": f"Sample question {i+1}",
            "bot_response": f"Sample response {i+1}",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(count)
    ]
    
    return {"conversations": conversations}


def evaluate_responses(state: ConversationState) -> ConversationState:
    """Evaluate responses node in the workflow"""
    conversations = state.get('conversations', [])
    evaluations = []
    total_score = 0
    
    for conv in conversations:
        # Simulated evaluation using MCP server
        score = 3 + (hash(conv['id']) % 3) - 1  # Random score between 2-5
        comment = f"Evaluation comment for {conv['id']}"
        
        evaluations.append({
            "id": conv['id'],
            "score": score,
            "comment": comment
        })
        
        total_score += score
    
    average_score = total_score / len(conversations) if conversations else 0
    
    return {
        **state,
        "evaluations": evaluations,
        "average_score": average_score
    }


def check_update_needed(state: ConversationState) -> Literal["needs_update", "no_update"]:
    """Decision node to check if update is needed"""
    average_score = state.get('average_score', 0)
    threshold = state.get('score_threshold', 3.0)
    update_required = state.get('update_required', False)
    
    if average_score < threshold or update_required:
        return "needs_update"
    else:
        return "no_update"


def prepare_update(state: ConversationState) -> ConversationState:
    """Prepare update node in the workflow"""
    average_score = state.get('average_score', 0)
    
    # Generate improved prompt
    prompt_text = """You are a helpful AI assistant focused on providing accurate, complete, and clear responses.

Guidelines:
- Provide comprehensive answers that fully address the user's question
- Use clear, easy-to-understand language
- Include relevant examples when helpful
- Be accurate and factual
- Structure responses logically
- Anticipate follow-up questions

Always aim to be helpful, informative, and user-friendly."""
    
    reason = f"Automated prompt update based on evaluation. Average score: {average_score:.1f}/5"
    
    return {
        **state,
        "prompt_text": prompt_text,
        "reason": reason,
        "approval_required": True
    }


def check_approval_status(state: ConversationState) -> Literal["approved", "rejected", "pending"]:
    """Decision node to check approval status"""
    if not state.get('approval_required', False):
        return "approved"
    
    status = state.get('approval_status', 'pending')
    return status


def create_approval_request(state: ConversationState) -> ConversationState:
    """Create approval request node in workflow"""
    prompt_text = state.get('prompt_text', '')
    reason = state.get('reason', '')
    
    # In a real implementation, this would create an entry in the approval store
    approval_id = f"req_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
    
    print(f"⏳ PR creation requires approval (ID: {approval_id})")
    print(f"Reason: {reason}")
    
    return {
        **state,
        "approval_id": approval_id
    }


def create_pr(state: ConversationState) -> ConversationState:
    """Create PR node in workflow"""
    prompt_text = state.get('prompt_text', '')
    reason = state.get('reason', '')
    
    # In a real implementation, this would call the GitHub MCP server
    pr_url = f"https://github.com/username/repo/pull/{uuid.uuid4().hex[:6]}"
    
    print(f"✓ Created PR: {pr_url}")
    
    return {
        **state,
        "pr_url": pr_url
    }


def handle_rejection(state: ConversationState) -> ConversationState:
    """Handle rejection node in workflow"""
    print(f"❌ PR creation rejected")
    
    return {
        **state,
        "pr_url": None
    }


# Define the LangGraph workflow structure
"""
# Review workflow definition using LangGraph (commented out as imports aren't available)
def create_review_workflow():
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("query_conversations", query_conversations)
    workflow.add_node("evaluate_responses", evaluate_responses)
    workflow.add_node("prepare_update", prepare_update)
    workflow.add_node("create_approval_request", create_approval_request)
    workflow.add_node("create_pr", create_pr)
    workflow.add_node("handle_rejection", handle_rejection)
    
    # Add edges
    workflow.add_edge("query_conversations", "evaluate_responses")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "evaluate_responses",
        check_update_needed,
        {
            "needs_update": "prepare_update",
            "no_update": END
        }
    )
    
    workflow.add_edge("prepare_update", "create_approval_request")
    
    workflow.add_conditional_edges(
        "create_approval_request",
        check_approval_status,
        {
            "approved": "create_pr",
            "rejected": "handle_rejection",
            "pending": END
        }
    )
    
    workflow.add_edge("create_pr", END)
    workflow.add_edge("handle_rejection", END)
    
    return workflow.compile()
"""

# --------------------------------
# SIMULATED IMPLEMENTATION
# --------------------------------

class SimulatedWorkflow:
    """Simulated workflow for demonstration purposes"""
    
    def __init__(self, name):
        self.name = name
    
    def invoke(self, params):
        """Simulate workflow execution"""
        print(f"\n[Executing {self.name}]")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        
        if self.name == "review_workflow":
            # Simulate review workflow
            print("\n1. Querying conversations...")
            conversations = query_conversations(params)
            
            print(f"\n2. Evaluating {len(conversations.get('conversations', []))} conversations...")
            state = evaluate_responses({**params, **conversations})
            
            print(f"\n3. Analysis complete - Average score: {state.get('average_score', 0):.1f}/5")
            
            decision = check_update_needed(state)
            if decision == "needs_update":
                print("\n4. Update needed - preparing prompt...")
                state = prepare_update(state)
                
                print("\n5. Creating approval request...")
                state = create_approval_request(state)
                
                # In real implementation, workflow would pause here until approval status changes
                print("\n6. Workflow paused - waiting for human approval")
                return {
                    "status": "waiting_approval",
                    "approval_id": state.get('approval_id'),
                    "state": state
                }
            else:
                print("\n4. No update needed")
                return {
                    "status": "completed",
                    "message": "Review completed - no updates required"
                }
                
        elif self.name == "update_workflow":
            # Simulate direct update workflow
            print("\n1. Preparing prompt update...")
            state = prepare_update(params)
            
            print("\n2. Creating approval request...")
            state = create_approval_request(state)
            
            # In real implementation, workflow would pause here until approval status changes
            print("\n3. Workflow paused - waiting for human approval")
            return {
                "status": "waiting_approval",
                "approval_id": state.get('approval_id'),
                "state": state
            }
        
        return {
            "status": "error",
            "message": f"Workflow {self.name} execution failed"
        }


# --------------------------------
# DEMO EXECUTION
# --------------------------------

def run_demo():
    """Run a demonstration of the hybrid architecture"""
    
    print("\n" + "=" * 60)
    print("HYBRID ARCHITECTURE DEMO: Autonomous Agent + LangGraph Workflows")
    print("=" * 60)
    
    # Initialize agent
    agent = AutonomousAgent()
    
    # Register workflows
    agent.register_workflow("review_workflow", SimulatedWorkflow("review_workflow"))
    agent.register_workflow("update_workflow", SimulatedWorkflow("update_workflow"))
    
    # Test different natural language goals
    goals = [
        "Review the last 5 conversations",
        "Check the last 3 chats and update prompt if scores are below 3.5",
        "Create a PR to update the system prompt"
    ]
    
    for i, goal in enumerate(goals, 1):
        print(f"\n\nTEST {i}: \"{goal}\"")
        print("-" * 60)
        
        # Process goal through autonomous agent
        result = agent.process_goal(goal)
        
        print("\nRESULT:")
        if result.get('status') == "waiting_approval":
            print(f"Waiting for approval (ID: {result.get('approval_id')})")
            
            # Simulate approval
            print("\n[Human approver approves the request]")
            
            # In real implementation, this would be handled by the approval system
            approval_id = result.get('approval_id')
            state = result.get('state', {})
            state['approval_status'] = 'approved'
            
            # Resume workflow with approved state
            print("\n[Workflow resumes with approved state]")
            print("\nCreating PR...")
            
            final_state = create_pr(state)
            print(f"PR URL: {final_state.get('pr_url')}")
            
        else:
            print(result.get('message', json.dumps(result, indent=2)))
        
        print("\n" + "=" * 60)

    print("\nHybrid Architecture Demo Complete")


if __name__ == "__main__":
    run_demo()

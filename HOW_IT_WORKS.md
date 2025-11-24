# How the Autonomous Planner Agent Works

This document explains the **autonomous reasoning** implementation in the Planner Agent, inspired by Strands Agent architecture.

## 🎯 Core Concept: Autonomous Tool Orchestration

Instead of manually calling each MCP server, you give the agent a **natural language goal**, and it autonomously decides:
1. Which tools (MCP servers) to call
2. In what order
3. What parameters to use
4. Whether additional actions are needed

## 🧠 The Architecture

### 1. Tool Registration with Clear Descriptions

Each MCP server is registered as a tool with a **semantic description**:

```python
class PlannerAgent:
    def __init__(self):
        # Tool 1: Query Conversations
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
        
        # Tool 2: Evaluate Response
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
        
        # Tool 3: Submit PR
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
```

**Key Point:** The descriptions are written in natural language that explains **what** each tool does, not **how** to use it.

### 2. Semantic Goal Parsing

When you provide a goal like "Review last 5 chats", the agent parses it semantically:

```python
def execute_goal(self, goal: str) -> str:
    goal_lower = goal.lower()
    
    # Extract parameters from natural language
    import re
    match = re.search(r'(\d+)\s+(?:chat|conversation)', goal_lower)
    limit = int(match.group(1)) if match else 5
    
    # Determine intent
    needs_evaluation = any(keyword in goal_lower 
                          for keyword in ['review', 'evaluate', 'check'])
    needs_pr = any(keyword in goal_lower 
                   for keyword in ['update prompt', 'create pr', 'pull request'])
```

**Reasoning Process:**
- "Review last 5 chats" → `limit=5`, `needs_evaluation=True`
- "Get last 3 conversations" → `limit=3`, `needs_evaluation=False`
- "Review and create PR" → `needs_evaluation=True`, `needs_pr=True`

### 3. Autonomous Workflow Execution

Based on the parsed intent, the agent executes a workflow:

```python
# Step 1: Always query conversations first
query_result = self.query_tool(limit=limit)
conversations = query_result.get('conversations', [])

# Step 2: Evaluate if needed
if needs_evaluation:
    scores = []
    for conv in conversations:
        eval_result = self.eval_tool(
            question=conv['user_message'],
            answer=conv['bot_response']
        )
        scores.append(eval_result.get('score'))
    
    avg_score = sum(scores) / len(scores)
    
    # Step 3: Create PR if scores are low or explicitly requested
    if avg_score < 3.5 or needs_pr:
        pr_result = self.github_tool(
            prompt_text=improved_prompt,
            reason=f"Average score: {avg_score:.1f}/5"
        )
```

## 🔄 How It Differs from Manual Orchestration

### Manual Approach (What We Removed)
```bash
# You explicitly tell the system what to do
./planner.sh conversations 5
./planner.sh evaluate "Q1" "A1"
./planner.sh evaluate "Q2" "A2"
./planner.sh pr "prompt" "reason"
```

**Characteristics:**
- ❌ You decide the workflow
- ❌ You call each tool explicitly
- ❌ You handle the logic

### Autonomous Approach (Current Implementation)
```bash
# You describe the goal, agent decides the workflow
python3 planner_agent/planner_agent.py --goal "Review last 5 chats"
```

**Characteristics:**
- ✅ Agent decides the workflow
- ✅ Agent calls tools autonomously
- ✅ Agent handles the logic

## 🎓 Strands Agent Pattern

The implementation follows the **Strands Agent pattern**:

### 1. Tool Definition
Each tool has:
- **Name**: Semantic identifier
- **Description**: What it does (for reasoning)
- **Input Schema**: What parameters it accepts
- **Callable**: How to execute it

### 2. Agent Reasoning Loop
```
User Goal → Parse Intent → Select Tools → Execute Workflow → Return Result
```

### 3. Example Reasoning Trace

**Goal:** "Review last 5 chats"

```
[Agent] Parsing goal: "Review last 5 chats"
[Agent] Detected intent: REVIEW
[Agent] Extracted parameter: limit=5
[Agent] Planning workflow:
  1. Call query_conversations(limit=5)
  2. For each conversation, call evaluate_response()
  3. Calculate average score
  4. If avg < 3.5, call submit_prompt_update()

[Agent] Executing workflow...
[Agent] Step 1: query_conversations(limit=5) → 5 conversations
[Agent] Step 2: evaluate_response() × 5 → scores: [2, 5, 4, 5, 2]
[Agent] Step 3: avg_score = 3.6
[Agent] Step 4: avg_score >= 3.5, skip PR creation

[Agent] Result: ✓ Scores are good, no PR needed
```

## 💡 Key Implementation Details

### 1. MCPTool Wrapper
```python
class MCPTool:
    """Wrapper that makes MCP servers callable as Python functions"""
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        # Prepare HTTP request
        payload = json.dumps(kwargs).encode('utf-8')
        req = request.Request(self.endpoint, data=payload, ...)
        
        # Call MCP server
        with request.urlopen(req, context=ssl_context) as response:
            return json.loads(response.read().decode())
```

This allows calling MCP servers like regular Python functions:
```python
result = self.query_tool(limit=5)  # Calls Lambda function
```

### 2. Semantic Intent Detection
```python
# Keywords that trigger evaluation
EVALUATION_KEYWORDS = ['review', 'evaluate', 'check', 'assess', 'analyze']

# Keywords that trigger PR creation
PR_KEYWORDS = ['update prompt', 'create pr', 'pull request', 'improve']

# Detect intent
needs_evaluation = any(kw in goal_lower for kw in EVALUATION_KEYWORDS)
needs_pr = any(kw in goal_lower for kw in PR_KEYWORDS)
```

### 3. Parameter Extraction
```python
# Extract number from "last N chats/conversations"
match = re.search(r'(\d+)\s+(?:chat|conversation)', goal_lower)
limit = int(match.group(1)) if match else 5  # Default to 5
```

### 4. Conditional Workflow
```python
# Always query first
conversations = self.query_tool(limit=limit)

# Conditionally evaluate
if needs_evaluation:
    scores = [self.eval_tool(...) for conv in conversations]
    avg_score = sum(scores) / len(scores)
    
    # Conditionally create PR
    if avg_score < 3.5 or needs_pr:
        self.github_tool(prompt_text=..., reason=...)
```

## 🚀 Usage Examples

### Example 1: Simple Query
```bash
python3 planner_agent/planner_agent.py --goal "Get last 3 conversations"
```

**Agent Reasoning:**
- Detects "Get" → No evaluation needed
- Extracts "3" → limit=3
- Calls only `query_conversations(limit=3)`

**Output:**
```
✓ Retrieved 3 conversations
```

### Example 2: Review with Evaluation
```bash
python3 planner_agent/planner_agent.py --goal "Review last 5 chats" --debug
```

**Agent Reasoning:**
- Detects "Review" → Evaluation needed
- Extracts "5" → limit=5
- Workflow: query → evaluate each → calculate avg → decide PR

**Output:**
```
[Agent] Calling query_conversations(limit=5)
[Agent] Retrieved 5 conversations
[Agent] Evaluating 5 responses...
  [conv_006] Score: 2/5
  [conv_007] Score: 5/5
  [conv_008] Score: 4/5
  [conv_009] Score: 5/5
  [conv_010] Score: 2/5

📊 Evaluation Results:
Average score: 3.6/5
✓ Scores are good, no PR needed
```

### Example 3: Force PR Creation
```bash
python3 planner_agent/planner_agent.py --goal "Review last 3 chats and create PR"
```

**Agent Reasoning:**
- Detects "Review" → Evaluation needed
- Detects "create PR" → Force PR creation
- Workflow: query → evaluate → create PR (regardless of score)

## 🎯 Benefits of This Approach

1. **Natural Language Interface**
   - Users describe goals, not steps
   - More intuitive and flexible

2. **Autonomous Decision Making**
   - Agent decides which tools to use
   - Adapts workflow based on context

3. **Maintainable**
   - Add new tools by registering them
   - Update reasoning logic in one place

4. **Extensible**
   - Easy to add new intents
   - Easy to add new tools

5. **Debuggable**
   - Debug mode shows reasoning trace
   - Clear separation of concerns

## 🔮 Future Enhancements

With a true Strands Agent (using LLM for reasoning), you could:

1. **More Complex Goals**
   ```
   "Review last 10 chats, focus on technical questions, 
    and create PR only if technical accuracy is below 4"
   ```

2. **Multi-Step Reasoning**
   ```
   "Check if recent responses are good. If not, analyze 
    which topics need improvement and create targeted PR"
   ```

3. **Adaptive Thresholds**
   ```
   "Review chats and determine appropriate quality threshold 
    based on conversation complexity"
   ```

## 📚 Summary

The Planner Agent demonstrates **autonomous tool orchestration**:

- ✅ **Tool Registration**: Each MCP server is a callable tool with semantic description
- ✅ **Intent Parsing**: Natural language goals are parsed for intent and parameters
- ✅ **Workflow Planning**: Agent decides which tools to call and in what order
- ✅ **Conditional Execution**: Workflow adapts based on results and context
- ✅ **Result Synthesis**: Agent combines tool outputs into coherent response

This is the foundation of **agentic AI systems** - where you describe **what** you want, not **how** to do it.

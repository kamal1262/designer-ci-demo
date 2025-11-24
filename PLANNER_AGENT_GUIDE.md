# Planner Agent - Natural Language MCP Orchestration

The Planner Agent uses **autonomous reasoning** to orchestrate multiple MCP servers based on natural language prompts. Simply tell it what you want, and it decides which tools to call and in what order.

## 🎯 Key Concept

Instead of manually calling each MCP server, you give the agent a **natural language goal** like:
- "Review last 5 chats"
- "Get last 3 conversations"
- "Evaluate recent responses and create PR if needed"

The agent **autonomously decides**:
1. Which MCP servers to call
2. In what order
3. What parameters to use
4. Whether to create a PR based on results

## 🚀 Quick Start

### Basic Usage

```bash
# Get and display conversations
python3 planner_agent/planner_agent.py --goal "Get last 5 chats"

# Review conversations with evaluation
python3 planner_agent/planner_agent.py --goal "Review last 5 chats"

# Review with custom prompt (inline)
python3 planner_agent/planner_agent.py --goal "Review last 5 chats and create PR" --prompt "Your custom prompt here..."

# Review with custom prompt (from file)
python3 planner_agent/planner_agent.py --goal "Review last 5 chats and create PR" --prompt-file custom_prompt.txt

# Debug mode (see agent reasoning)
python3 planner_agent/planner_agent.py --goal "Review last 5 chats" --debug
```

### Interactive Mode

```bash
python3 planner_agent/planner_agent.py
```

Then enter goals interactively:
```
Goal: Review last 5 chats
Goal: Get last 10 conversations
Goal: exit
```

## 📋 Example Prompts

### 1. Get and Display Conversations
```bash
--goal "Get last 3 chats"
```
**Agent reasoning:**
- Detects "Get" → only calls `query_conversations`
- Detects "get/show/list" → prints conversation details
- No evaluation needed

**Output:**
```
✓ Retrieved 3 conversations

[conv_008] 2025-11-13T16:54:15.025470Z
Q: Explain SQL databases
A: SQL databases are relational database management systems...

[conv_009] 2025-11-13T17:04:15.025474Z
Q: What is Kubernetes?
A: Kubernetes is an open-source container orchestration platform...

[conv_010] 2025-11-13T17:09:15.025478Z
Q: How do I debug Python code?
A: Print statements.
```

### 2. Review with Evaluation
```bash
--goal "Review last 5 chats"
```
**Agent reasoning:**
- Detects "Review" → calls `query_conversations`
- Then calls `evaluate_response` for each conversation
- Calculates average score
- Decides if PR needed (avg < 3.5)

**Output:**
```
✓ Retrieved 5 conversations

📊 Evaluation Results:
Average score: 3.6/5

[conv_006] Score: 2/5
Comment: While the statement 'Git tracks changes' is technically correct...

[conv_007] Score: 5/5
Comment: The chatbot's answer is accurate, complete, clear...

✓ Scores are good, no PR needed
```

### 3. Review with Custom Prompt
```bash
--goal "Review last 3 chats and create PR" --prompt-file custom_prompt.txt
```
**Agent reasoning:**
- Calls `query_conversations(limit=3)`
- Evaluates each response
- If avg < 3.5 OR "create PR" in goal → calls `submit_prompt_update` with custom prompt

**Output:**
```
✓ Retrieved 3 conversations

📊 Evaluation Results:
Average score: 2.3/5

[conv_006] Score: 2/5
[conv_010] Score: 2/5
[conv_011] Score: 3/5

✓ Created PR: https://github.com/your-org/your-repo/pull/125
```

### 4. Inline Custom Prompt
```bash
--goal "Review last 2 chats and create PR" --prompt "You are an expert assistant..."
```
**Agent reasoning:**
- Same as above, but uses inline prompt instead of file

## 🧠 How It Works

### Autonomous Reasoning

The agent parses your natural language goal and decides:

1. **Extract parameters:**
   - "last 5 chats" → `limit=5`
   - "last 10 conversations" → `limit=10`
   - No number specified → `limit=5` (default)

2. **Determine actions:**
   - Contains "review", "evaluate", "check" → Run evaluation
   - Contains "get", "fetch", "show" → Just query
   - Contains "update prompt", "create pr" → Force PR creation

3. **Execute workflow:**
   - Always starts with `query_conversations`
   - If evaluation needed, calls `evaluate_response` for each
   - If scores low or PR requested, calls `submit_prompt_update`

### Tool Descriptions

Each MCP server has a clear description that helps the agent reason:

```python
query_conversations:
  "Retrieves the latest chatbot conversations with user messages 
   and bot responses. Returns up to 10 most recent conversations."

evaluate_response:
  "Evaluates chatbot responses using AWS Bedrock Claude 3 Sonnet. 
   Returns a score from 1-5 and a detailed comment."

submit_prompt_update:
  "Creates a GitHub pull request to update the system prompt. 
   Only use when evaluation scores are low (<3) or explicitly requested."
```

## 🔧 Configuration

### Environment Variables

The agent reads from `.env`:
```bash
MCP_QUERY_URL=https://...lambda-url.us-east-1.on.aws/
MCP_EVAL_URL=https://...lambda-url.us-east-1.on.aws/
MCP_GITHUB_URL=https://...lambda-url.us-east-1.on.aws/
```

### Command-Line Arguments

```bash
--goal "..."           # Natural language goal (required in non-interactive mode)
--debug                # Enable debug mode to see agent reasoning
--prompt "..."         # Custom prompt text for PR creation (inline)
--prompt-file path     # Path to file containing custom prompt text
```

### Custom Prompt Files

Create a text file with your custom prompt:

```bash
# custom_prompt.txt
You are an expert technical assistant specializing in software development.

Guidelines:
- Provide detailed, technically accurate responses
- Include code examples when relevant
- Explain complex concepts clearly
...
```

Then use it:
```bash
python3 planner_agent/planner_agent.py \
  --goal "Review last 5 chats and create PR" \
  --prompt-file custom_prompt.txt
```

### Debug Mode

Enable debug mode to see agent reasoning:
```bash
python3 planner_agent/planner_agent.py --goal "Review last 5 chats" --debug
```

**Debug output:**
```
============================================================
Goal: Review last 5 chats
============================================================

[Agent] Calling query_conversations(limit=5)
[Agent] Retrieved 5 conversations
[Agent] Evaluating 5 responses...
[Agent] Evaluating conversation 1/5
  [conv_006] Score: 2/5
[Agent] Evaluating conversation 2/5
  [conv_007] Score: 5/5
...
```

## 📊 Use Cases

### Use Case 1: Daily Quality Check
```bash
# Run every morning to check overnight conversations
python3 planner_agent/planner_agent.py --goal "Review last 20 chats"
```

### Use Case 2: Quick Spot Check
```bash
# Just see what the latest conversations are
python3 planner_agent/planner_agent.py --goal "Get last 5 conversations"
```

### Use Case 3: Automated PR Creation
```bash
# Evaluate and auto-create PR if quality is low
python3 planner_agent/planner_agent.py --goal "Review last 10 chats and update prompt if needed"
```

### Use Case 4: Manual Review
```bash
# Interactive mode for ad-hoc analysis
python3 planner_agent/planner_agent.py

Goal: Review last 5 chats
Goal: Get last 10 conversations
Goal: Review last 3 chats and create PR
```

## 🔄 Comparison: Planner Agent vs Manual Scripts

### Manual Approach (planner.sh)
```bash
# You explicitly call each step
./planner.sh conversations 5
./planner.sh evaluate "question" "answer"
./planner.sh pr "prompt" "reason"
```
**Pros:** Full control, simple bash script
**Cons:** Manual orchestration, no reasoning

### Planner Agent Approach
```bash
# Agent decides what to do
python3 planner_agent/planner_agent.py --goal "Review last 5 chats"
```
**Pros:** Natural language, autonomous reasoning, flexible
**Cons:** Requires Python, more complex

## 🎓 Advanced Examples

### Custom Evaluation Threshold
The agent creates PRs when average score < 3.5. To change this, modify `planner_agent.py`:

```python
should_create_pr = (
    avg_score < 3.0 or  # Change threshold here
    'update prompt' in goal_lower or 
    'create pr' in goal_lower
)
```

### Add New Goal Patterns
Add custom reasoning patterns:

```python
# In execute_goal method
if 'urgent' in goal_lower:
    # Send Slack notification
    notify_slack(f"Urgent review requested: {goal}")
```

## 🚀 Integration

### Cron Job
```bash
# Daily quality check at 9 AM
0 9 * * * cd /path/to/project && python3 planner_agent/planner_agent.py --goal "Review last 20 chats" >> /var/log/planner.log 2>&1
```

### CI/CD Pipeline
```yaml
# GitHub Actions
- name: Quality Check
  run: |
    python3 planner_agent/planner_agent.py --goal "Review last 10 chats"
```

### Slack Bot
```python
@slack_bot.command("/review")
def review_chats(ack, command):
    ack()
    agent = PlannerAgent()
    result = agent.execute_goal(f"Review last {command['text']} chats")
    slack_bot.post_message(result)
```

## 🎯 Summary

The Planner Agent demonstrates **true autonomous orchestration**:

✅ **Natural language interface** - Just describe what you want
✅ **Autonomous reasoning** - Agent decides which tools to call
✅ **Flexible workflows** - Adapts based on your goal
✅ **Clear tool descriptions** - Each MCP server explains its purpose
✅ **Debug mode** - See exactly how the agent reasons

This is the power of MCP + intelligent agents: **describe the goal, not the steps**.

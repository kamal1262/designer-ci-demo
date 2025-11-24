# Demo Guide - Testing After AWS Deployment

This guide shows how to test and demo the MCP Server system after deploying to AWS.

## 🚀 Prerequisites

After running `./deploy.sh`, you should have:
1. ✅ Three Lambda functions deployed with Function URLs
2. ✅ `.env` file with the Lambda URLs
3. ✅ GitHub token configured

## 📋 Quick Demo Script

### Demo 1: Get Conversations (30 seconds)

**What it shows:** Basic MCP server query functionality

```bash
# Interactive mode
python3 planner_agent/planner_agent.py

Goal: get last 3 chats
```

**Expected output:**
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

**Key points to highlight:**
- ✅ Agent autonomously calls the Query MCP server
- ✅ Displays conversation details in real-time
- ✅ No manual API calls needed

---

### Demo 2: Review with Evaluation (1-2 minutes)

**What it shows:** Multi-server orchestration with autonomous reasoning

```bash
Goal: review last 5 chats
```

**Expected output:**
```
✓ Retrieved 5 conversations

📊 Evaluating 5 responses...
  Evaluating [conv_006]... Score: 2/5
  Evaluating [conv_007]... Score: 5/5
  Evaluating [conv_008]... Score: 4/5
  Evaluating [conv_009]... Score: 5/5
  Evaluating [conv_010]... Score: 2/5

📊 Evaluation Results:
Average score: 3.6/5

[conv_006] Score: 2/5
Comment: While the statement 'Git tracks changes' is technically correct...

[conv_007] Score: 5/5
Comment: The chatbot's answer is accurate, complete, clear...

✓ Scores are good, no PR needed
```

**Key points to highlight:**
- ✅ Agent calls Query MCP → then Evaluation MCP for each conversation
- ✅ Real-time streaming shows progress
- ✅ Autonomous decision: avg score 3.6 → no PR needed
- ✅ Uses AWS Bedrock Claude 3 Sonnet for evaluation

---

### Demo 3: Automated PR Creation (2-3 minutes)

**What it shows:** Full workflow with GitHub integration

```bash
Goal: review last 2 chats and create pr
```

**Expected output:**
```
✓ Retrieved 2 conversations

📊 Evaluating 2 responses...
  Evaluating [conv_009]... Score: 5/5
  Evaluating [conv_010]... Score: 2/5

📊 Evaluation Results:
Average score: 3.5/5

[conv_009] Score: 5/5
Comment: Excellent response...

[conv_010] Score: 2/5
Comment: Too brief and incomplete...

🚀 Creating PR (avg score: 3.5)...
✓ Created PR: https://github.com/your-org/your-repo/pull/123
```

**Key points to highlight:**
- ✅ Agent orchestrates all 3 MCP servers
- ✅ Autonomous decision: avg score 3.5 → triggers PR
- ✅ Creates actual GitHub PR with improved prompt
- ✅ Click the PR link to show the actual PR in GitHub

---

### Demo 4: Custom Prompt PR (1 minute)

**What it shows:** Direct PR creation with custom prompt

```bash
# Exit interactive mode and use command-line
python3 planner_agent/planner_agent.py \
  --goal "update prompt" \
  --prompt-file custom_prompt.txt
```

**Expected output:**
```
🚀 Creating PR directly...
Using custom prompt (XXX characters)
✓ Created PR: https://github.com/your-org/your-repo/pull/124
```

**Key points to highlight:**
- ✅ Direct PR creation without review
- ✅ Custom prompt from file
- ✅ Skips query/evaluation (efficient)

---

## 🎬 Full Demo Flow (5-7 minutes)

### Setup (30 seconds)
```bash
cd /path/to/mcp-server-demo
source .env
python3 planner_agent/planner_agent.py
```

### Act 1: Simple Query (30 seconds)
```
Goal: get last 3 chats
```
**Narration:** "The agent autonomously calls the Query MCP server and displays conversations in real-time."

### Act 2: Intelligent Review (1-2 minutes)
```
Goal: review last 5 chats
```
**Narration:** "Now the agent orchestrates two MCP servers: first queries conversations, then evaluates each one using AWS Bedrock. Notice the real-time streaming - you see progress as it happens. The agent autonomously decides the average score is good, so no PR is needed."

### Act 3: Automated PR (2-3 minutes)
```
Goal: review last 2 chats and create pr
```
**Narration:** "This time we force PR creation. The agent evaluates conversations, calculates the average score, and autonomously creates a GitHub pull request with an improved prompt. Let's click the PR link to see the actual PR..."

**[Open the PR in browser]**

**Narration:** "Here's the actual PR created by the agent. It includes the improved prompt and a detailed reason for the update based on evaluation scores."

### Act 4: Custom Prompt (1 minute)
```
Goal: exit
```
```bash
python3 planner_agent/planner_agent.py \
  --goal "update prompt" \
  --prompt-file custom_prompt.txt
```
**Narration:** "Finally, you can create PRs directly with custom prompts, skipping the review process entirely. This is useful for manual prompt updates or A/B testing."

---

## 🧪 Testing Individual MCP Servers

### Test Query MCP Server
```bash
curl -X POST $MCP_QUERY_URL \
  -H "Content-Type: application/json" \
  -d '{"limit": 3}'
```

**Expected response:**
```json
{
  "success": true,
  "conversations": [
    {
      "id": "conv_008",
      "timestamp": "2025-11-13T16:54:15.025470Z",
      "user_message": "Explain SQL databases",
      "bot_response": "SQL databases are..."
    }
  ]
}
```

### Test Evaluation MCP Server
```bash
curl -X POST $MCP_EVAL_URL \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "answer": "Python is a programming language."
  }'
```

**Expected response:**
```json
{
  "success": true,
  "score": 4,
  "comment": "The response is accurate and clear..."
}
```

### Test GitHub MCP Server
```bash
curl -X POST $MCP_GITHUB_URL \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "You are a helpful assistant...",
    "reason": "Testing PR creation"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "pr_url": "https://github.com/your-org/your-repo/pull/125",
  "pr_number": 125
}
```

---

## 🎯 Demo Talking Points

### 1. Autonomous Orchestration
"Notice how you just describe **what** you want, not **how** to do it. The agent autonomously decides which MCP servers to call and in what order."

### 2. Real-Time Streaming
"The streaming output shows progress as it happens - you're not waiting for everything to complete before seeing results."

### 3. Intelligent Decision Making
"The agent makes autonomous decisions based on context. For example, it only creates a PR when scores are low or explicitly requested."

### 4. Production-Ready Architecture
"All three MCP servers are deployed as AWS Lambda functions with Function URLs. They're scalable, serverless, and production-ready."

### 5. Natural Language Interface
"You can use natural language like 'review last 5 chats' or 'get conversations' - the agent understands your intent."

---

## 🐛 Troubleshooting

### Issue: "Error fetching conversations"
**Solution:** Check Lambda URLs in `.env`:
```bash
cat .env | grep MCP_
```

### Issue: "Error creating PR"
**Solution:** Verify GitHub token:
```bash
echo $GITHUB_TOKEN
```

### Issue: Lambda timeout
**Solution:** Increase timeout in `infra/serverless.yml`:
```yaml
timeout: 60  # Increase from 30 to 60 seconds
```

---

## 📊 Metrics to Show

After demo, show AWS CloudWatch metrics:

1. **Lambda Invocations:** Number of times each MCP server was called
2. **Duration:** How long each Lambda execution took
3. **Success Rate:** Percentage of successful invocations
4. **Cost:** Actual cost of running the demo (usually < $0.01)

---

## 🎓 Advanced Demo Scenarios

### Scenario 1: Daily Quality Check
```bash
# Simulate daily cron job
python3 planner_agent/planner_agent.py --goal "Review last 20 chats"
```

### Scenario 2: A/B Testing
```bash
# Test variant A
python3 planner_agent/planner_agent.py \
  --goal "update prompt" \
  --prompt-file prompts/variant_a.txt

# Test variant B
python3 planner_agent/planner_agent.py \
  --goal "update prompt" \
  --prompt-file prompts/variant_b.txt
```

### Scenario 3: Threshold Tuning
```bash
# Review with custom threshold
python3 planner_agent/planner_agent.py \
  --goal "Review last 10 chats and create PR if average < 4.0"
```

---

## 🎬 Video Demo Script

**[0:00-0:30] Introduction**
"Today I'm demonstrating an autonomous agent that orchestrates multiple MCP servers deployed on AWS Lambda."

**[0:30-1:00] Architecture Overview**
"We have three MCP servers: Query for conversations, Evaluation using AWS Bedrock, and GitHub for PR creation."

**[1:00-2:00] Demo 1: Get Conversations**
[Show command and output]

**[2:00-4:00] Demo 2: Review with Evaluation**
[Show command, streaming output, and decision]

**[4:00-6:00] Demo 3: Automated PR Creation**
[Show command, PR creation, open PR in browser]

**[6:00-7:00] Conclusion**
"This demonstrates true autonomous orchestration - you describe the goal, the agent decides the workflow."

---

## 📝 Demo Checklist

Before demo:
- [ ] Deploy to AWS: `./deploy.sh`
- [ ] Verify `.env` has Lambda URLs
- [ ] Test GitHub token: `echo $GITHUB_TOKEN`
- [ ] Test one command: `python3 planner_agent/planner_agent.py --goal "get last 3 chats"`
- [ ] Prepare browser with GitHub repo open
- [ ] Clear terminal for clean demo

During demo:
- [ ] Show architecture diagram (if available)
- [ ] Demonstrate 3-4 scenarios
- [ ] Open created PRs in browser
- [ ] Show CloudWatch metrics (optional)
- [ ] Answer questions

After demo:
- [ ] Share GitHub repo link
- [ ] Share documentation links
- [ ] Discuss production considerations

---

## 🚀 Quick Start for Demo

```bash
# 1. Deploy (if not already done)
./deploy.sh

# 2. Start interactive mode
python3 planner_agent/planner_agent.py

# 3. Run demo commands
Goal: get last 3 chats
Goal: review last 5 chats
Goal: review last 2 chats and create pr
Goal: exit

# 4. Show custom prompt
python3 planner_agent/planner_agent.py \
  --goal "update prompt" \
  --prompt-file custom_prompt.txt
```

That's it! You're ready to demo the autonomous MCP orchestration system.

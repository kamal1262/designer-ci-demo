# MCP Serverless AI Agent System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you deploy and test the MCP Serverless AI Agent System quickly.

## Prerequisites Checklist

- [ ] AWS CLI installed and configured
- [ ] Docker installed and running
- [ ] Python 3.11+ installed
- [ ] GitHub Personal Access Token (for PR creation)
- [ ] AWS Bedrock access enabled (Claude 3 Sonnet)

## Step 1: Clone and Setup (2 minutes)

```bash
# Navigate to project directory
cd mcp-server-demo

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required .env variables:**
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012  # Your AWS account ID
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=username/repo
```

## Step 2: Test Locally (1 minute)

```bash
# Test the query server
./test_local.sh
```

**Expected output:**
```
✓ Query server returns 5 conversations
✓ All tests passed
```

## Step 3: Deploy to AWS (5-10 minutes)

```bash
# Deploy all MCP servers
./deploy.sh
```

**What happens:**
1. Authenticates with AWS ECR
2. Builds 3 Docker images
3. Pushes to ECR
4. Creates Lambda functions
5. Creates Function URLs

**Expected output:**
```
✓ mcp-query-server deployed
✓ mcp-evaluation-server deployed
✓ mcp-github-server deployed

MCP Server URLs:
Query Server:      https://xxxxx.lambda-url.us-east-1.on.aws/
Evaluation Server: https://yyyyy.lambda-url.us-east-1.on.aws/
GitHub Server:     https://zzzzz.lambda-url.us-east-1.on.aws/
```

## Step 4: Update .env with URLs

Copy the URLs from deployment output and update your `.env`:

```bash
MCP_QUERY_URL=https://xxxxx.lambda-url.us-east-1.on.aws/
MCP_EVAL_URL=https://yyyyy.lambda-url.us-east-1.on.aws/
MCP_GITHUB_URL=https://zzzzz.lambda-url.us-east-1.on.aws/
```

## Step 5: Test Deployed Servers (2 minutes)

### Test Query Server
```bash
curl -X POST https://your-query-url/ \
  -H 'Content-Type: application/json' \
  -d '{"limit": 5}'
```

### Test Evaluation Server
```bash
curl -X POST https://your-eval-url/ \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "What is Python?",
    "answer": "Python is a programming language."
  }'
```

### Test GitHub Server
```bash
curl -X POST https://your-github-url/ \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt_text": "You are a helpful assistant.",
    "reason": "Testing PR creation"
  }'
```

## Step 6: Run Planner Agent (1 minute)

```bash
# Install dependencies
cd planner_agent
pip install -r requirements.txt

# Run in interactive mode
python planner_agent.py
```

**Try these commands:**
```
Goal: Review last 5 chats
Goal: Review last 3 conversations and update prompt if needed
Goal: Evaluate the most recent conversation
```

## Example Workflow

### Scenario: Review Recent Conversations

**User Input:**
```
Goal: Review last 5 chats
```

**Agent Actions:**
1. Calls `query_conversations(limit=5)` → Gets 5 conversations
2. For each conversation:
   - Calls `evaluate_response(question, answer)` → Gets score
3. Calculates average score: 3.2/5
4. Identifies 2 conversations with score < 3
5. Provides summary

**Agent Output:**
```
Reviewed 5 conversations:
- Average score: 3.2/5
- 2 conversations scored below 3:
  * "How do I install packages in Python?" - Score: 2/5
    Comment: "Too brief, lacks detail"
  * "How does Git work?" - Score: 2/5
    Comment: "Oversimplified response"
- Recommendation: Consider updating prompts for technical questions
```

### Scenario: Auto-Update Prompts

**User Input:**
```
Goal: Review last 5 chats and update prompt if needed
```

**Agent Actions:**
1. Calls `query_conversations(limit=5)`
2. Evaluates each conversation
3. Detects average score < 3
4. Calls `submit_prompt_update()` → Creates PR
5. Returns PR URL

**Agent Output:**
```
Reviewed 5 conversations:
- Average score: 2.6/5
- Created PR: https://github.com/user/repo/pull/123
- Reason: Low evaluation scores detected
- Updated prompt to provide more detailed technical responses
```

## Troubleshooting

### Issue: Docker not running
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Issue: AWS credentials not configured
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
```

### Issue: Bedrock access denied
1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Enable "Claude 3 Sonnet"
4. Wait for approval (usually instant)

### Issue: Lambda timeout
```bash
# Increase timeout to 60 seconds
aws lambda update-function-configuration \
  --function-name mcp-evaluation-server \
  --timeout 60 \
  --region us-east-1
```

## Architecture Overview

```
User → Planner Agent → MCP Servers → AWS Services
                ↓
        Natural Language
                ↓
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
Query Server          Eval Server
    │                       │
    └───────────┬───────────┘
                ▼
          GitHub Server
                │
                ▼
          Create PR
```

## Key Features

✅ **Natural Language Interface** - Talk to your agent in plain English
✅ **Intelligent Orchestration** - Agent decides which tools to use
✅ **Automated Workflows** - Review → Evaluate → Update
✅ **Serverless Architecture** - Pay only for what you use
✅ **Production Ready** - Docker containers, IAM roles, monitoring

## Next Steps

1. **Customize Conversations** - Edit `mcp_query_server/lambda_function.py`
2. **Adjust Thresholds** - Modify score thresholds in planner agent
3. **Add More Tools** - Create additional MCP servers
4. **Enable Monitoring** - Set up CloudWatch dashboards
5. **Add Authentication** - Secure endpoints with API Gateway

## Cleanup

When you're done testing:

```bash
./cleanup.sh
```

This will delete:
- All Lambda functions
- ECR repositories
- IAM roles

## Cost Estimate

**Monthly costs (assuming 1000 requests/month):**
- Lambda: ~$0.20
- ECR: ~$0.10
- Bedrock: ~$3.00 (Claude 3 Sonnet)
- **Total: ~$3.30/month**

## Support

- 📖 Full documentation: `README.md`
- 🐛 Issues: Check CloudWatch Logs
- 💬 Questions: Review architecture diagrams

## Success Checklist

- [ ] All 3 MCP servers deployed
- [ ] Function URLs working
- [ ] Planner agent running
- [ ] Successfully reviewed conversations
- [ ] Evaluated responses with scores
- [ ] (Optional) Created test PR

**Congratulations! Your MCP Serverless AI Agent System is ready! 🎉**

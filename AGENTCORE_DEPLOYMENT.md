# MCP Server Demo - Deployment and Usage Guide

This guide provides comprehensive instructions for deploying and using the MCP Server Demo system, including setup, configuration, troubleshooting, and usage examples.

## Overview

The MCP Server Demo consists of:

1. **Three MCP Servers** deployed as AWS Lambda functions:
   - **Query Server**: Retrieves conversation data
   - **Evaluation Server**: Evaluates response quality using Claude 3
   - **GitHub Server**: Creates PRs for prompt updates

2. **Planner Agent**: A local Python script that orchestrates these MCP servers using natural language goals

## Prerequisites

- AWS account with Lambda and Bedrock access
- Docker installed
- Python 3.11+
- GitHub Personal Access Token
- Basic knowledge of AWS services

## Deployment Process

### Step 1: Configure Environment

Create and populate your `.env` file with the necessary credentials:

```bash
# Copy the template
cp .env.example .env

# Edit with your actual values
nano .env
```

Required `.env` values:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your_account_id
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repo
```

### Step 2: Test Locally (Optional)

Test your MCP servers locally before deployment:

```bash
./test_local.sh
```

### Step 3: Deploy to AWS

Deploy all three MCP servers to AWS Lambda:

```bash
./deploy.sh
```

The deployment script will:
1. Build Docker images for each server
2. Push images to AWS ECR
3. Deploy Lambda functions
4. Create Function URLs
5. Output the URLs for each server

### Step 4: Update Configuration with Lambda URLs

After deployment, you'll receive Lambda Function URLs. Add these to your `.env` file:

```bash
MCP_QUERY_URL=https://xxxxxxxxxxxx.lambda-url.us-east-1.on.aws/
MCP_EVAL_URL=https://xxxxxxxxxxxx.lambda-url.us-east-1.on.aws/
MCP_GITHUB_URL=https://xxxxxxxxxxxx.lambda-url.us-east-1.on.aws/
```

## Important: URL Configuration Fix

**Critical**: If you encounter connection issues, you may need to directly modify the `planner_agent.py` file to use the correct URLs:

1. Open `planner_agent/planner_agent.py`
2. Locate the URL configuration section (near the top)
3. Replace with hardcoded Lambda URLs:

```python
# MCP Server endpoints (hardcoded for reliability)
MCP_QUERY_URL = 'https://your-query-url.lambda-url.us-east-1.on.aws/'
MCP_EVAL_URL = 'https://your-eval-url.lambda-url.us-east-1.on.aws/'
MCP_GITHUB_URL = 'https://your-github-url.lambda-url.us-east-1.on.aws/'
```

This ensures the correct URLs are used regardless of environment variable issues.

## Using the Planner Agent

The Planner Agent is used to interact with the MCP servers using natural language goals.

### Installation

```bash
cd planner_agent
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run with a specific goal
python planner_agent.py --goal "your goal here"

# Interactive mode
python planner_agent.py
```

### Example Commands

#### 1. Get Recent Conversations

```bash
python planner_agent.py --goal "Get last 5 chats"
```

#### 2. Review Conversations

```bash
python planner_agent.py --goal "Review last 5 conversations"
```

#### 3. Create PR with Custom Prompt (Direct Text)

```bash
python planner_agent.py --goal "update prompt" --prompt "Your custom prompt here"
```

#### 4. Create PR with Custom Prompt (From File)

```bash
python planner_agent.py --goal "update prompt" --prompt-file "../custom_prompt.txt"
```

#### 5. Review and Conditionally Create PR

```bash
python planner_agent.py --goal "review the last 5 conversations and create a PR if score is <4"
```

### Advanced Usage

You can combine multiple actions in a single goal:

```bash
python planner_agent.py --goal "Get the last 3 conversations, evaluate them, and create a PR if any score below 3"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Connection Refused Error

**Symptom:**
```
❌ Error fetching conversations: Error calling query_conversations: <urlopen error [Errno 61] Connection refused>
```

**Solutions:**
- Ensure Lambda functions are deployed and running
- Check Lambda Function URLs in `.env` or hardcoded in `planner_agent.py`
- Verify correct URL mapping (Query/Eval/GitHub)
- Test Lambda functions directly using curl

#### 2. Environment Variable Issues

**Symptom:** URLs in `.env` file not being used

**Solution:** Hardcode the URLs directly in `planner_agent.py` as shown above

#### 3. URL Mapping Issues

**Symptom:** Wrong server responds to requests

**Solution:**
- Test each endpoint individually:
```bash
curl -X POST $MCP_QUERY_URL -H "Content-Type: application/json" -d '{"limit": 3}'
curl -X POST $MCP_EVAL_URL -H "Content-Type: application/json" -d '{"question": "Test", "answer": "Test"}'
curl -X POST $MCP_GITHUB_URL -H "Content-Type: application/json" -d '{"prompt_text": "Test", "reason": "Test"}'
```
- Update URLs to correct mapping based on responses

#### 4. GitHub Token Issues

**Symptom:** PR creation fails with authentication errors

**Solution:** Generate a new GitHub token with repo access

#### 5. AWS Permissions

**Symptom:** Lambda deployment fails

**Solution:** Ensure your AWS credentials have sufficient permissions

## Testing Your Deployment

### 1. Basic Connectivity Test

```bash
python planner_agent.py --goal "Get last 3 chats"
```

Expected output:
```
✓ Retrieved 3 conversations
[conv_id] timestamp
Q: User question
A: Bot response
...
```

### 2. Evaluation Test

```bash
python planner_agent.py --goal "Review last 2 chats"
```

Expected output:
```
✓ Retrieved 2 conversations
📊 Evaluating 2 responses...
  Evaluating [conv_id]... Score: X/5
  ...
📊 Evaluation Results:
Average score: X.X/5
...
```

### 3. PR Creation Test

```bash
python planner_agent.py --goal "update prompt" --prompt "Test prompt"
```

Expected output:
```
✓ Created PR: https://github.com/username/repo/pull/XX
```

## Using AgentCore for Deployment (Future Enhancement)

AgentCore can be used to deploy the Planner Agent as a service:

- **Containerization**: Package the agent in a Docker container
- **API Endpoints**: Define endpoints for agent interaction
- **Scheduled Operations**: Run routine evaluations
- **Scaling**: Handle multiple concurrent users
- **Monitoring**: Track performance and usage

See full AgentCore documentation for details on this advanced deployment option.

## Demo Script

For presentations and demos, follow this script:

1. **Introduction** (2 min):
   - Explain MCP servers and Planner Agent
   - Show architecture diagram

2. **Basic Demo** (3 min):
   - Show retrieving conversations
   - Show evaluation of responses

3. **Advanced Demo** (5 min):
   - Review conversations and create PR
   - Use custom prompt
   - Show PR in GitHub

4. **Troubleshooting Demo** (2 min):
   - Show common errors and fixes

## Conclusion

This MCP Server Demo showcases:
- Serverless deployment of MCP servers
- Natural language interface for AI agent orchestration
- Autonomous multi-step workflows
- Quality control for AI conversations
- Continuous improvement through PR automation

For additional details, refer to the DEMO_GUIDE.md and HOW_IT_WORKS.md files.

# MCP Serverless AI Agent System - Testing Guide

## Overview
This guide shows you how to test and demo the deployed MCP serverless system.

## Prerequisites
- All Lambda functions deployed (run `./deploy.sh`)
- `.env` file updated with Lambda function URLs
- AWS credentials configured
- GitHub token configured

## 1. Testing Individual MCP Servers

### Test MCP Server 1 - Query Conversations

Retrieve recent conversations:

```bash
# Get last 5 conversations (default)
curl -X POST "YOUR_QUERY_SERVER_URL" \
  -H "Content-Type: application/json" \
  -d '{}'

# Get last 3 conversations
curl -X POST "YOUR_QUERY_SERVER_URL" \
  -H "Content-Type: application/json" \
  -d '{"limit": 3}'

# Get all conversations
curl -X POST "YOUR_QUERY_SERVER_URL" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

Expected response:
```json
{
  "success": true,
  "count": 5,
  "conversations": [
    {
      "id": "conv_001",
      "user_message": "What is Python?",
      "bot_response": "Python is a high-level...",
      "timestamp": "2025-11-13T19:09:21.919531Z"
    }
  ]
}
```

### Test MCP Server 2 - Evaluation

Evaluate a chatbot response:

```bash
curl -X POST "YOUR_EVAL_SERVER_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "answer": "Python is a programming language."
  }'
```

Expected response:
```json
{
  "success": true,
  "question": "What is Python?",
  "answer": "Python is a programming language.",
  "score": 4,
  "comment": "The answer is accurate and concise..."
}
```

### Test MCP Server 3 - GitHub PR Creator

Create a pull request:

```bash
curl -X POST "YOUR_GITHUB_SERVER_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "You are a helpful AI assistant...",
    "reason": "Improving response quality based on evaluations"
  }'
```

Expected response:
```json
{
  "success": true,
  "pr_url": "https://github.com/your-repo/pull/1",
  "pr_number": 1,
  "branch": "prompt-update-20251114-001234"
}
```

## 2. Running the Planner Agent

The planner agent orchestrates all three MCP servers to:
1. Query recent conversations
2. Evaluate low-scoring responses
3. Create a GitHub PR if scores are below threshold

### Setup

```bash
cd planner_agent
pip install -r requirements.txt
```

### Run the Agent

```bash
python planner_agent.py
```

### Expected Output

```
========================================
MCP Planner Agent
========================================

Step 1: Querying recent conversations...
✓ Retrieved 5 conversations

Step 2: Evaluating responses...
Evaluating conversation conv_001...
  Score: 4/5 - Good response
Evaluating conversation conv_002...
  Score: 2/5 - Needs improvement
...

Step 3: Analyzing results...
Average score: 3.2/5
Low-scoring conversations: 2

Step 4: Creating GitHub PR for prompt improvement...
✓ PR created: https://github.com/your-repo/pull/1

========================================
Planner Agent Complete
========================================
```

## 3. Full System Demo Workflow

### Scenario: Automated Quality Monitoring

1. **Monitor Conversations**
   ```bash
   # The planner agent queries recent conversations
   curl -X POST "$MCP_QUERY_URL" -H "Content-Type: application/json" -d '{"limit": 5}'
   ```

2. **Evaluate Quality**
   ```bash
   # For each conversation, evaluate the response
   curl -X POST "$MCP_EVAL_URL" \
     -H "Content-Type: application/json" \
     -d '{"question": "...", "answer": "..."}'
   ```

3. **Trigger Improvement**
   ```bash
   # If average score < 3.5, create a PR
   curl -X POST "$MCP_GITHUB_URL" \
     -H "Content-Type: application/json" \
     -d '{"prompt_text": "...", "reason": "Low scores detected"}'
   ```

4. **Review PR**
   - Go to your GitHub repository
   - Review the automatically created PR
   - Merge if the prompt improvements look good

## 4. Testing with Different Scenarios

### Scenario A: High-Quality Responses
```bash
# Test with good responses
curl -X POST "$MCP_EVAL_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "answer": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions based on that data."
  }'
```

Expected: Score 4-5/5

### Scenario B: Low-Quality Responses
```bash
# Test with brief/incomplete responses
curl -X POST "$MCP_EVAL_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I install Python packages?",
    "answer": "Use pip."
  }'
```

Expected: Score 1-2/5

### Scenario C: Trigger PR Creation
```bash
# Run planner agent when there are low scores
python planner_agent/planner_agent.py
```

Expected: PR created if average score < 3.5

## 5. Monitoring and Logs

### View Lambda Logs

```bash
# Query Server logs
aws logs tail /aws/lambda/mcp-query-server --follow

# Evaluation Server logs
aws logs tail /aws/lambda/mcp-evaluation-server --follow

# GitHub Server logs
aws logs tail /aws/lambda/mcp-github-server --follow
```

### Check Lambda Function Status

```bash
# List all functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `mcp-`)].FunctionName'

# Get function details
aws lambda get-function --function-name mcp-query-server
```

## 6. Troubleshooting

### Issue: Lambda returns 500 error

**Solution:**
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/FUNCTION_NAME --follow

# Test locally first
cd mcp_query_server
python3 lambda_function.py
```

### Issue: Bedrock access denied

**Solution:**
- Verify IAM role has `bedrock:InvokeModel` permission
- Check if Bedrock is available in your region
- Verify model ID is correct

### Issue: GitHub PR creation fails

**Solution:**
- Verify GitHub token has repo permissions
- Check if repository exists and is not empty
- Verify repository name format: `owner/repo`

## 7. Performance Testing

### Load Test Query Server

```bash
# Install Apache Bench
brew install apache-bench  # macOS

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -p query.json -T application/json "$MCP_QUERY_URL"
```

### Measure Response Times

```bash
# Time a single request
time curl -X POST "$MCP_EVAL_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "answer": "test"}'
```

## 8. Cleanup

### Remove All Resources

```bash
# Run cleanup script
./cleanup.sh

# Or manually delete
aws lambda delete-function --function-name mcp-query-server
aws lambda delete-function --function-name mcp-evaluation-server
aws lambda delete-function --function-name mcp-github-server

# Delete ECR repositories
aws ecr delete-repository --repository-name mcp-query-server --force
aws ecr delete-repository --repository-name mcp-evaluation-server --force
aws ecr delete-repository --repository-name mcp-github-server --force
```

## 9. Demo Script

Here's a complete demo script you can run:

```bash
#!/bin/bash

echo "=== MCP System Demo ==="
echo ""

# Load environment
source .env

echo "1. Testing Query Server..."
curl -s -X POST "$MCP_QUERY_URL" -H "Content-Type: application/json" -d '{"limit": 3}' | jq .
echo ""

echo "2. Testing Evaluation Server..."
curl -s -X POST "$MCP_EVAL_URL" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?", "answer": "Use pip."}' | jq .
echo ""

echo "3. Running Planner Agent..."
cd planner_agent && python planner_agent.py
echo ""

echo "=== Demo Complete ==="
```

Save this as `demo.sh`, make it executable (`chmod +x demo.sh`), and run it!

## Next Steps

1. Customize the evaluation criteria in `mcp_evaluation_server/lambda_function.py`
2. Adjust the score threshold in `planner_agent/planner_agent.py`
3. Modify the prompt template in `mcp_github_server/lambda_function.py`
4. Add more MCP servers for additional functionality
5. Integrate with your production chatbot system

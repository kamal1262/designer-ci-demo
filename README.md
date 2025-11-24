# MCP Serverless AI Agent System

A production-ready implementation of three MCP (Model Context Protocol) servers deployed as AWS Lambda functions, orchestrated by a Strands Agent planner that uses natural language to coordinate intelligent workflows.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User / Client                                 │
│              "Review last 5 chats"                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Planner Agent (Strands Agent)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Natural Language Understanding                          │   │
│  │  - Parse user goal                                       │   │
│  │  - Plan tool execution sequence                          │   │
│  │  - Coordinate MCP servers                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────┬───────────────┬───────────────┬───────────────────┘
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │   MCP-1     │  │   MCP-2     │  │   MCP-3     │
    │ Query       │  │ Evaluate    │  │ GitHub PR   │
    │ Convos      │  │ Response    │  │ Creator     │
    └─────────────┘  └─────────────┘  └─────────────┘
```

## 📦 Components

### 1. MCP Server 1 – Conversation Query
- **Purpose**: Returns latest chatbot conversations
- **Endpoint**: `/query`
- **Tool**: `query_conversations`
- **Output**: JSON array of conversation objects

### 2. MCP Server 2 – LLM Evaluation
- **Purpose**: Evaluates chatbot responses using Claude 3 Sonnet
- **Endpoint**: `/evaluate`
- **Tool**: `evaluate_response`
- **Output**: Score (1-5) with comment

### 3. MCP Server 3 – GitHub Pull Request
- **Purpose**: Creates GitHub PRs for prompt updates
- **Endpoint**: `/submit-pr`
- **Tool**: `submit_prompt_update`
- **Output**: PR URL and status

### 4. Planner Agent
- **Purpose**: Orchestrates MCP servers using natural language
- **Framework**: Strands Agents
- **Capabilities**: 
  - Parse natural language goals
  - Execute multi-step workflows
  - Intelligent decision making

## 📋 Prerequisites

- **Python 3.11+**
- **AWS CLI** configured with credentials
- **Docker** (for Lambda container builds)
- **GitHub Personal Access Token** (for PR creation)
- **AWS Bedrock** access (Claude 3 Sonnet enabled)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install uv (fast Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# GITHUB_TOKEN=your_github_token
# AWS_REGION=us-east-1
# BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 3. Deploy Lambda Functions

```bash
# Deploy all MCP servers
./deploy.sh

# Or deploy individually
cd mcp_query_server && ./deploy.sh
cd mcp_evaluation_server && ./deploy.sh
cd mcp_github_server && ./deploy.sh
```

### 4. Run Planner Agent

```bash
cd planner_agent
python planner_agent.py
```

## 🧪 Testing

### Test MCP Server 1 (Query Conversations)

```bash
# Local test
cd mcp_query_server
python -m pytest test_lambda.py

# Lambda test
curl -X POST https://your-api-gateway-url/query \
  -H 'Content-Type: application/json' \
  -d '{}'
```

**Expected Response:**
```json
{
  "conversations": [
    {
      "id": "conv_001",
      "user_message": "What is Python?",
      "bot_response": "Python is a high-level programming language...",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Test MCP Server 2 (Evaluate Response)

```bash
# Local test
cd mcp_evaluation_server
python lambda_function.py

# Lambda test
curl -X POST https://your-api-gateway-url/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "What is Python?",
    "answer": "Python is a programming language."
  }'
```

**Expected Response:**
```json
{
  "score": 4,
  "comment": "Accurate but could be more detailed."
}
```

### Test MCP Server 3 (GitHub PR)

```bash
# Local test
cd mcp_github_server
python lambda_function.py

# Lambda test
curl -X POST https://your-api-gateway-url/submit-pr \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt_text": "Updated system prompt for better responses",
    "reason": "Low evaluation scores detected"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "pr_url": "https://github.com/user/repo/pull/123",
  "pr_number": 123
}
```

### Test Planner Agent

```bash
cd planner_agent
python planner_agent.py --goal "Review last 5 chats"
```

**Expected Workflow:**
1. Calls `query_conversations` → Gets 5 conversations
2. For each conversation, calls `evaluate_response` → Gets scores
3. Summarizes results
4. If scores < 3, calls `submit_prompt_update` → Creates PR

## 📁 Project Structure

```
mcp-server-demo/
├── mcp_query_server/
│   ├── lambda_function.py       # Query conversations handler
│   ├── requirements.txt         # Dependencies
│   ├── event.json              # Test event
│   ├── tool_manifest.json      # MCP metadata
│   ├── Dockerfile              # Container image
│   └── deploy.sh               # Deployment script
│
├── mcp_evaluation_server/
│   ├── lambda_function.py       # Evaluation handler
│   ├── requirements.txt
│   ├── event.json
│   ├── tool_manifest.json
│   ├── Dockerfile
│   └── deploy.sh
│
├── mcp_github_server/
│   ├── lambda_function.py       # GitHub PR handler
│   ├── requirements.txt
│   ├── event.json
│   ├── tool_manifest.json
│   ├── Dockerfile
│   └── deploy.sh
│
├── planner_agent/
│   ├── planner_agent.py        # Strands Agent orchestrator
│   ├── requirements.txt
│   └── config.yaml             # MCP server endpoints
│
├── infra/
│   └── serverless.yml          # Serverless Framework config
│
├── .env.example                # Environment variables template
├── deploy.sh                   # Deploy all services
└── README.md                   # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |
| `GITHUB_REPO` | Target repository | `username/repo` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `BEDROCK_MODEL_ID` | Claude model ID | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `MCP_QUERY_URL` | Query server endpoint | `https://xxx.lambda-url.us-east-1.on.aws` |
| `MCP_EVAL_URL` | Evaluation server endpoint | `https://yyy.lambda-url.us-east-1.on.aws` |
| `MCP_GITHUB_URL` | GitHub server endpoint | `https://zzz.lambda-url.us-east-1.on.aws` |

### Planner Agent Prompt Template

The planner uses this reasoning template:

```
You are a planning agent coordinating multiple MCP servers.
Your tools:

1. query_conversations – get latest chatbot conversations and responses.
2. evaluate_response – rate chatbot answers 1–5 for quality.
3. submit_prompt_update – open a pull request to improve prompts.

Instructions:
- Read the user's task (e.g. "Review last 5 chats").
- Decide which tools to call and in what order.
- Only call submit_prompt_update if low scores (<3) or user explicitly requests.
- Summarize findings clearly at the end.
```

## 🔄 Workflow Examples

### Example 1: Review Last 5 Chats

**User Goal:** "Review last 5 chats"

**Agent Execution:**
1. Call `query_conversations()` → Get 5 conversations
2. For each conversation:
   - Call `evaluate_response(question, answer)` → Get score
3. Calculate average score
4. Summarize results

**Output:**
```
Reviewed 5 conversations:
- Average score: 3.8/5
- 2 conversations scored below 3
- Recommendations: Consider updating prompts for edge cases
```

### Example 2: Review and Update Prompts

**User Goal:** "Review last 5 chats and update prompt if needed"

**Agent Execution:**
1. Call `query_conversations()` → Get 5 conversations
2. For each conversation:
   - Call `evaluate_response(question, answer)` → Get score
3. Detect 2 conversations with score < 3
4. Call `submit_prompt_update(prompt_text, reason)` → Create PR

**Output:**
```
Reviewed 5 conversations:
- Average score: 2.6/5
- 2 conversations scored below 3
- Created PR: https://github.com/user/repo/pull/123
- Reason: Low evaluation scores detected
```

## 🛠️ Development

### Local Testing

Each MCP server can be tested locally:

```bash
# Test query server
cd mcp_query_server
python lambda_function.py

# Test evaluation server
cd mcp_evaluation_server
python lambda_function.py

# Test GitHub server
cd mcp_github_server
python lambda_function.py
```

### Adding New MCP Servers

1. Create new directory: `mcp_new_server/`
2. Add `lambda_function.py` with handler
3. Create `tool_manifest.json` with MCP metadata
4. Add to `planner_agent/config.yaml`
5. Register in `planner_agent.py`

### Debugging

```bash
# View Lambda logs
aws logs tail /aws/lambda/mcp-query-server --follow
aws logs tail /aws/lambda/mcp-evaluation-server --follow
aws logs tail /aws/lambda/mcp-github-server --follow

# Test planner agent with debug mode
cd planner_agent
python planner_agent.py --goal "Review last 5 chats" --debug
```

## 🔐 Security Notes

- GitHub token stored as environment variable (not in code)
- Lambda functions use IAM roles with least privilege
- API Gateway endpoints can be secured with API keys
- Consider using AWS Secrets Manager for production

## 🧹 Cleanup

```bash
# Delete all Lambda functions
./cleanup.sh

# Or delete individually
aws lambda delete-function --function-name mcp-query-server
aws lambda delete-function --function-name mcp-evaluation-server
aws lambda delete-function --function-name mcp-github-server
```

## 📚 Additional Resources

- [AWS Strands Documentation](https://github.com/awslabs/strands)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)

## 📝 License

MIT License - See LICENSE file for details

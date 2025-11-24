# Building Agentic AI Systems with Model Context Protocol and AWS AgentCore

*By Kamal Hossain | November 2025*

## Introduction: The Evolution of Conversational AI

As organizations increasingly adopt AI-powered solutions, there's a growing need to bridge the gap between technical capabilities and business user needs. One of the most challenging areas has been empowering non-technical chatbot designers to shape LLM-powered experiences without compromising on governance, security, and quality control.

In this technical deep-dive, I'll explore how the Model Context Protocol (MCP) and AWS AgentCore services create a powerful foundation for building agentic AI systems that empower non-technical users while maintaining enterprise-grade controls.

## The Challenge: Static Systems vs. Dynamic Intelligence

Traditional production chatbots often rely on static, pre-approved answers. While this ensures compliance and predictability, it severely limits the system's ability to handle nuanced customer queries. Organizations want to leverage Large Language Models (LLMs) to provide more dynamic, intelligent responses, but face several challenges:

1. **Skills Gap**: Conversational AI engineers design prompts and flows, then hand them to non-technical CX designers who can't easily modify or improve them
2. **Slow Feedback Cycles**: Changes require engineering resources, creating bottlenecks
3. **Limited Iteration Speed**: Deploying improvements to production takes too long
4. **Governance Concerns**: LLMs need guardrails to ensure policy compliance

These challenges create a situation where organizations must choose between flexibility and control—a choice they shouldn't have to make.

## Enter MCP: The Standardized Protocol for AI Tool Communication

The Model Context Protocol (MCP) provides a standardized way for AI models to interact with external tools and data sources. Unlike traditional function calling or tool use, MCP offers a more robust framework with consistent schemas, versioning, and metadata.

### Before vs. After MCP: A Technical Comparison

**Before MCP**:
- Each tool requires a unique API integration
- LLMs must be specifically trained or fine-tuned for each tool
- No standardized schema for defining tools
- Limited flexibility and extensibility

**After MCP**:
- Unified API approach for all tools
- Consistent schema for tool definitions
- Self-documenting through tool manifests
- Easier to add new capabilities

## Building Agentic Systems with MCP Servers

Our solution leverages MCP servers deployed as AWS Lambda functions to create a flexible, serverless architecture. Each server provides specialized capabilities through a standardized interface:

### Architecture Components

1. **MCP Query Server**
   - Purpose: Retrieves chatbot conversations from a secure database
   - Implementation: AWS Lambda function with access controls
   - Ensures data is properly anonymized and policy-compliant

2. **MCP Evaluation Server**
   - Purpose: Evaluates chatbot responses using Claude 3 Sonnet
   - Implementation: AWS Lambda function calling AWS Bedrock
   - Provides quality scores and improvement suggestions

3. **MCP GitHub Server**
   - Purpose: Manages prompt updates via GitHub PRs
   - Implementation: AWS Lambda function with GitHub API integration
   - Enforces change management and version control

4. **Planner Agent (Orchestration Layer)**
   - Purpose: Interprets natural language goals and coordinates MCP servers
   - Implementation: Python-based agent using Strands framework
   - Makes intelligent decisions about which tools to use and when

### Autonomous Reasoning Implementation

What makes this architecture truly powerful is the autonomous reasoning capability of the Planner Agent. Instead of requiring explicit commands for each MCP server, the system allows users to express goals in natural language, and the agent determines the workflow:

```python
def execute_goal(self, goal: str) -> str:
    # Parse intent from natural language
    goal_lower = goal.lower()
    
    # Extract parameters (like number of conversations)
    match = re.search(r'(\d+)\s+(?:chat|conversation)', goal_lower)
    limit = int(match.group(1)) if match else 5
    
    # Determine required actions based on semantic intent
    needs_evaluation = 'review' in goal_lower or 'evaluate' in goal_lower
    needs_pr = 'update prompt' in goal_lower or 'create pr' in goal_lower
    
    # Execute workflow based on determined intent
    query_result = self.query_tool(limit=limit)
    conversations = query_result.get('conversations', [])
    
    if needs_evaluation:
        # Evaluate each conversation
        scores = []
        for conv in conversations:
            eval_result = self.eval_tool(
                question=conv['user_message'],
                answer=conv['bot_response']
            )
            scores.append(eval_result.get('score'))
        
        # Decide whether to create PR based on scores
        avg_score = sum(scores) / len(scores)
        if avg_score < 3.5 or needs_pr:
            self.github_tool(prompt_text=prompt, reason=reason)
```

This autonomous reasoning approach offers several advantages:

1. **Natural Language Interface**: Users describe what they want, not how to do it
2. **Dynamic Workflow Generation**: The agent determines the appropriate sequence of tool calls
3. **Context-Aware Decision Making**: Subsequent actions are influenced by the results of previous ones
4. **Extensible Design**: New tools can be added by registering them with descriptions

### Technical Implementation

Each MCP server follows a standardized structure:

```
mcp_server/
├── lambda_function.py       # Main handler logic
├── tool_manifest.json       # MCP schema definition
├── requirements.txt         # Dependencies
├── event.json               # Test event template
├── Dockerfile               # Container image definition
└── deploy.sh                # Deployment script
```

The `tool_manifest.json` is particularly important as it defines the server's capabilities in a standardized format:

```json
{
  "name": "query_conversations",
  "description": "Retrieves chatbot conversations",
  "version": "1.0.0",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "Number of conversations to return"
      }
    }
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "conversations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "user_message": { "type": "string" },
            "bot_response": { "type": "string" },
            "timestamp": { "type": "string" }
          }
        }
      }
    }
  }
}
```

## Enhancing the Architecture with AWS AgentCore

While our initial implementation used open-source components and custom Lambda functions, AWS has recently introduced AgentCore services that can significantly enhance this architecture. Let's explore how we can leverage these services to build more robust agentic systems.

### AWS AgentCore Memory

Traditional agent implementations struggle with maintaining context across multiple interactions. AWS AgentCore Memory provides a managed service for storing, retrieving, and managing agent state:

- **Conversational History**: Stores user-agent interactions
- **Knowledge Persistence**: Maintains facts learned during conversations
- **Vector Storage**: Enables semantic search across historical data

For our chatbot designers, this means the agent can remember previous feedback, decisions, and preferences, creating a more consistent experience.

### AWS AgentCore Identity

One of the key challenges in deploying agentic systems is identity and access management. AgentCore Identity solves this by:

- **RBAC Integration**: Role-based access controls for agent capabilities
- **Authentication**: Secure identity verification for agent users
- **Permission Management**: Fine-grained controls over which MCP tools can be accessed

This enables our architecture to enforce stricter access controls, ensuring that CX designers can only access appropriate data and functions.

### AWS AgentCore Gateway

Perhaps the most significant enhancement is AgentCore Gateway, which replaces our custom LiteLLM gateway implementation. AgentCore Gateway provides:

- **Centralized Access Control**: Unified management of all agent interactions
- **Request Routing**: Intelligent routing to appropriate LLMs and tools
- **Usage Monitoring**: Tracking of token consumption and costs
- **Rate Limiting**: Protection against excessive usage

As noted in the AWS User Group presentation: "For identity and access control we used open source LiteLLM as gateway which required a significant engineering effort. Bedrock AgentCore Gateway supports all the features and more out of the box."

The primary advantage of AgentCore Gateway is that it handles the complex orchestration between your application and various LLM providers. When integrating with our MCP architecture, we can configure the gateway to:

1. **Enforce access policies**: Control which users or roles can access specific MCP servers
2. **Route requests optimally**: Send requests to the appropriate LLM based on the task complexity
3. **Handle authentication**: Manage credentials securely across the entire system
4. **Log all interactions**: Create audit trails for compliance and debugging

Implementing this in our architecture requires minimal code changes:

```python
# Instead of direct HTTP requests to Lambda URLs:
response = requests.post(MCP_QUERY_URL, json={"limit": 5})

# Use AgentCore Gateway:
response = agent_core_client.invoke_agent(
    agentId="mcp-planner-agent",
    agentAliasId="PROD",
    sessionId=session_id,
    inputText="Get last 5 chats"
)
```

## Finding the Right Balance: When to Use Agentic Systems

It's important to recognize that not every AI application requires a fully agentic approach. As highlighted in the presentation slides, there's a spectrum of solutions:

| Approach | Task Complexity | Latency | Cost | Risk | Best For |
|----------|----------------|---------|------|------|----------|
| LLMs with RAG | Structured, controllable | <15s | <$0.10 | Minimal | Simple, structured tasks |
| Agentic Workflow | Structured + generative | >15s | >$1 | Moderate | Enhancing deterministic workflows with creative input/output |
| Full Agentic System | Dynamic decision-making | >30s | >$1 | High | Complex tasks, fuzzy business logic, high-value decisions |

For our chatbot designer use case, a hybrid approach combining LLMs with RAG and Agentic Workflows provides the optimal balance between structure and flexibility.

## Deployment Options for MCP Servers & Planner Agent

When implementing this architecture, you have multiple deployment options:

### Option 1: AWS Lambda + Custom Agent

- MCP servers deployed as AWS Lambda functions
- Planner agent runs as a separate process, either locally or as its own Lambda
- Provides maximum flexibility and customization
- Requires more management overhead

### Option 2: AWS Bedrock AgentCore

- Run the planner as a fully managed agent in Amazon Bedrock AgentCore
- Offloads infrastructure management
- Provides native integration with Bedrock models
- Standardizes the agent lifecycle
- Less customization but easier maintenance

Here's how we would configure this deployment:

```bash
# Define the agent in AWS CLI
aws bedrock create-agent \
  --agent-name "mcp-planner-agent" \
  --agent-resource-role-arn "$AGENT_ROLE_ARN" \
  --foundation-model "anthropic.claude-3-sonnet-20240229-v1:0" \
  --description "Planner agent for MCP server orchestration" \
  --instruction "You are a planning agent that coordinates MCP servers"

# Add action groups for each MCP server
aws bedrock create-agent-action-group \
  --agent-id "$AGENT_ID" \
  --action-group-name "query-conversations" \
  --action-group-executor "{\"lambda\":{\"lambdaArn\":\"$QUERY_LAMBDA_ARN\"}}" \
  --description "Retrieves the latest chatbot conversations"
```

This approach abstracts away much of the infrastructure complexity while maintaining the same functional capabilities.

## Conclusion: The Future of Agentic Systems

The combination of MCP and AWS AgentCore services represents a significant advancement in building agentic AI systems that balance flexibility, security, and governance. By standardizing tool interactions through MCP and leveraging AWS's managed services for identity, memory, and access control, we can create systems that empower non-technical users while maintaining enterprise-grade controls.

As these technologies mature, we can expect:

1. **More Autonomous Agents**: Systems that can handle increasingly complex tasks with less supervision
2. **Better Governance**: More sophisticated controls over agent behavior
3. **Enhanced Collaboration**: Seamless interaction between technical and non-technical stakeholders
4. **Reduced Operational Overhead**: Less custom code to maintain as more functionality moves to managed services

The journey toward truly intelligent agentic systems is just beginning, but the foundation provided by MCP and AWS AgentCore gives us a solid platform to build upon.

## Getting Started

If you want to explore this architecture yourself:

1. Clone the MCP server demo repository
2. Configure your AWS credentials and environment variables:

```bash
# Create and populate .env file
cp .env.example .env

# Required values
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your_account_id
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repo
```

3. Test locally before deployment:

```bash
./test_local.sh
```

4. Deploy the MCP servers using the provided scripts:

```bash
./deploy.sh
```

5. Update your configuration with the Lambda URLs:

```bash
# Update these in your .env file or directly in planner_agent.py
MCP_QUERY_URL=https://xxxx.lambda-url.us-east-1.on.aws/
MCP_EVAL_URL=https://yyyy.lambda-url.us-east-1.on.aws/
MCP_GITHUB_URL=https://zzzz.lambda-url.us-east-1.on.aws/
```

6. Experiment with the planner agent to coordinate workflows:

```bash
# Run with a specific goal
python planner_agent.py --goal "Review last 5 chats"

# Or use interactive mode
python planner_agent.py
```

7. Consider migrating components to AWS AgentCore services for enhanced capabilities and easier management.

The code and documentation for this project provide a solid starting point for building your own agentic AI systems.

---

*This blog post is based on a presentation given at the AWS User Group Meetup in November 2025 and the associated MCP server demo project.*

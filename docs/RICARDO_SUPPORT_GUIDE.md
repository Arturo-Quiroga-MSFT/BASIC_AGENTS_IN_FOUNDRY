# Supporting Ricardo: Foundry ↔ Copilot Studio Integration Guide

**Date:** January 22, 2026  
**For:** Arturo Quiroga (Microsoft Foundry - Pro-code)  
**Supporting:** Ricardo Mejia (Copilot Studio - Low-code)

---

## 🎯 Ricardo's Immediate Goals (Based on Meeting)

1. **Create basic agents** (weather, Excel queries) for learning
2. **Register agents in Agent 365** for centralized management
3. **Orchestrate agents** between Foundry and Copilot Studio
4. **Understand endpoint management** and connectivity
5. **Build technical demos** covering registration across platforms

**Note:** A2A protocol implementation is a future/advanced topic, not immediate priority.

---

## 📚 Key Concepts for Ricardo

### 1. **Agent 365 (The Control Plane)**
- **What it is:** Central registry for ALL enterprise AI agents (Microsoft & non-Microsoft)
- **Purpose:** 
  - Unified identity and lifecycle management
  - Security enforcement (Defender, Entra, Purview)
  - Native integration with M365 apps
  - Activity monitoring and policy enforcement

### 2. **Two Development Approaches**

| Aspect | **Foundry (Pro-code)** | **Copilot Studio (Low-code)** |
|--------|------------------------|-------------------------------|
| Tools | VS Code, Python/C#/.NET, SDK | SaaS platform, graphical UI |
| Best for | Complex workflows, custom orchestration | Quick deployment, business users |
| Hosting | Azure (requires subscription) | Fully managed by Microsoft |
| Models | Any model (OpenAI, Anthropic, Meta, etc.) | Built-in with Power Platform |
| Integration | Full API control, custom code | Pre-built connectors, low-code |

### 3. **Simple Integration Pattern (Focus for Now)**

```
┌─────────────────────────────────────────────────────────────┐
│                       Agent 365                              │
│              (Central Control Plane)                         │
└────────────┬──────────────────────────┬─────────────────────┘
             │                          │
    ┌────────▼────────┐        ┌───────▼────────┐
    │  Foundry Agent  │        │ Copilot Studio │
    │   (Pro-code)    │        │  Agent (Low)   │
    └─────────────────┘        └────────────────┘
             │                          │
             │    ┌─────────────────┐  │
             └───►│ Microsoft 365   │◄─┘
                  │ - Teams         │
                  │ - Copilot       │
                  │ - Outlook       │
                  └─────────────────┘
```

**Initial Focus:** Publishing and registration, not agent-to-agent communication.

---

## 🔧 How to Help Ricardo from Foundry Perspective

### **Option 1: Publish Foundry Agent to Agent 365** ⭐ RECOMMENDED FOR RICARDO

**What Ricardo needs to know:**
- Foundry agents can be published directly to Agent 365
- Once published, they appear in M365 Copilot and Teams
- No additional hosting required (Foundry provides managed runtime)

**Prerequisites:**
1. ✅ Access to [Frontier Preview Program](https://adoption.microsoft.com/copilot/frontier-program/)
2. ✅ Azure subscription with appropriate permissions
3. ✅ Azure Developer CLI installed
4. ✅ Docker installed
5. ✅ .NET 9.0 SDK or later

**Publishing Process:**
```bash
# 1. Run the Agent 365 publishing script
# Available at: https://go.microsoft.com/fwlink/?linkid=2343518

# This script automatically:
# - Creates Foundry project with hosted agent support
# - Creates application with stable endpoint
# - Creates Azure Bot Service (relay to M365)
# - Builds and registers hosted agent
# - Deploys agent to application
# - Publishes to organization (requires admin approval)
```

**Key Points for Ricardo:**
- The agent gets a **stable endpoint** that M365 can call
- Uses **Azure Bot Service** as middleware/relay
- Requires **tenant admin approval** before available
- Agent appears in Agent 365 registry automatically

---

### **Option 2: Publish Foundry Agent to M365 Copilot/Teams**

**When to use:** Ricardo wants the agent directly in Teams/Copilot without Agent 365

**Process:**
1. In Foundry portal → Select agent → **Publish**
2. Select **"Publish to Teams and Microsoft 365 Copilot"**
3. Fill in metadata (name, description, icons, privacy policy)
4. Choose scope:
   - **Shared Scope**: Appears under "Your agents"
   - **Organization Scope**: Appears under "Built by your org" (needs admin approval)
5. Download package or continue with automated deployment

--- ⚠️ SIMPLER PATH

**What Ricardo can do in Copilot Studio:**

1. **Add Foundry Agent as External Agent:**
   - In Copilot Studio → **Add an agent** → Select **"Microsoft Foundry"**
   - Provide: Foundry project endpoint URL
   - Provide: Agent ID
   - Add description (so Copilot Studio knows when to invoke it)
   - **This is the recommended starting point** - straightforward and well-documented
3. Copilot Studio reads agent card automatically
4. Agent becomes available for orchestration

---

## 🏢 Tenant & Subscription Requirements

### **What Ricardo Mentioned He Needs:**

1. **Own Tenant + Subscription:**
   - Required for full testing without cross-tenant limitations
   - Needs both Copilot Studio AND Agent 365 in same tenant
   - Enables full control over deployments

2. **Required Roles:**
   - **Tenant Admin** OR
   - **Entra ID Manager** (for identity management)
   - **Contributor** (for Azure resources)
   - **Authentication Policy Administrator** (for Entra configurations)

3. **How to Get It:**
   - Request through Microsoft internal channels
   - Can use Azure free account to start
   - External ID tenant creation requires **Tenant Creator** role

---

## 📊 Example Integration Scenarios

### **Scenario 1: Weather Agent (Basic)**

**Foundry Side (You):**
```python
# Create basic weather agent with real API
from shared_utils import get_real_weather

agent = await provider.create_agent(
    name="WeatherAgent",
    instructions="Provide real weather information",
    tools=get_real_weather
)

# Publish to Agent 365 or expose A2A endpoint
```🔍 Key Endpoints Ricardo Will Need

### **From Your Foundry Agents:**

1. **Agent Application Endpoint:** ⭐ PRIMARY FOCUS
   - Format: `https://<your-foundry-project>.services.ai.azure.com/api/projects/<project>/applications/<app-id>`
   - This is what Copilot Studio will call
   - You'll provide this after publishing your agents

2. **Azure Bot Service Endpoint (auto-generated during publish):**
   - Used as relay between M365 and Foundry
   - Format: `https://your-bot.azurewebsites.net/api/messages`
   - This is created automatically - just note it down

**What Ricardo Doesn't Need Right Now:**
- ❌ A2A endpoints (future/advanced topic)
- ❌ Agent cards (not immediate priority)
- ❌ Direct protocol implementation

---

## 

**Copilot Studio Side (Ricardo):**
- Connect to your published agent
- Or create orchestrator that calls your agent when needed
- Can combine with his low-code flows

---

### **Scenario 2: Multi-Agent Orchestration**

**Architecture:**
```
User Query
    ↓
Copilot Studio Orchestrator (Ricardo)
    ↓
├─→ Foundry Weather Agent (You) ─────→ Returns weather data
├─→ Copilot Studio Excel Agent (Ricardo) → Returns data from Excel
└─→ Foundry SharePoint Agent (You) ───→ Returns documents
    ↓
Aggregated Response to User
```

**Key Points:**
- Copilot Studio acts as orchestrator
- Each agent specializes in specific tasks
- Communication via A2A protocol or direct endpoints
Copilot Studio Uses Your Foundry Agent**

**Architecture (Simple):**
```
User Query in Teams/M365 Copilot
    ↓
Copilot Studio (Ricardo)
    ↓
Calls → Foundry Weather Agent (You)
    ↓
Returns weather data
    ↓
Response to User
```

**Key Points:**
- Start simple: one agent calling another
- Focus on getting the connection working first
- Test with basic queries before complex orchestration
2. Show agent-to-agent communication
3. Demonstrate single pane of glass (Agent 365)
4. Security and monitoring aspects

---

## ⚠️ What About A2A Protocol?

**Agent-to-Agent (A2A) Protocol** is a standardized protocol for agents to communicate with each other, but **Ricardo wants to focus on this much later**.

### **Why A2A is Not the Priority Now:**
- It's an advanced topic requiring deeper technical knowledge
- Basic publishing and registration work without it
- Copilot Studio can connect to Foundry agents using simpler methods
- Focus should be on getting ONE connection working first

### **What Ricardo Should Focus On Instead:**
1. ✅ Publishing Foundry agents to Agent 365
2. ✅ Connecting to them from Copilot Studio using the UI
3. ✅ Understanding endpoints and basic connectivity
4. ✅ Getting hands-on experience with simple scenarios

### **When to Revisit A2A:**
- After mastering basic agent registration
- When building complex multi-agent systems
- When standardization across different frameworks matters
- When ready for advanced orchestration patterns

**For now:** Think of A2A as "phase 3" or later. Focus on phases 1-2 first.

---

## 🔍 Key Endpoints Ricardo Will Need

### **From Your Foundry Agents:**

1. **Agent Application Endpoint:**
   - Format: `https://<your-foundry-project>.services.ai.azure.com/api/projects/<project>/applications/<app-id>`
   Show your published Foundry agent in Agent 365
2. Connect to it from Copilot Studio
3. Make a simple call (e.g., get weather)
4. Display the response

### **Demo 3: End-to-End User Experience** 
1. User asks question in Teams
2. Copilot Studio receives it
3. Calls your Foundry agent
4. Returns answer to user
5. Show monitoring in both platform
---- Link to Agent 365 documentation
   - Link to A2A protocol specs
   - Tenant setup i (Priority Order):**
1. [Agent 365 Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/agent-365) - **START HERE**
2. [Publish Foundry Agents to M365](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-copilot) - **NEXT**
3. [Connect Foundry Agent to Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent) - **FOR RICARDO**
4. [Copilot Studio Basics](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio)

**Future/Advanced (Not Now):**
- [A2A Protocol](https://a2a-protocol.org/latest/) - For much later
- [Agent-to-Agent Communication](https://learn.microsoft.com/en-us/agent-framework/user-guide/hosting/agent-to-agent-integration) - Advanced topic
2. [Publish Foundry Agents to M365](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-copilot)
3. [Connect Foundry Agent to Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent)
4. [A2A Protocol Specification](https://a2a-protocol.org/latest/)
5. [Copilot Studio Agent Orchestration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents)

**Getting Tenant Setup:**
1. [Create Azure External Tenant](https://learn.microsoft.com/en-us/entra/external-id/customers/how-to-create-external-tenant-portal)
2. [Azure Subscription Setup](https://learn.microsoft.com/en-us/entra/external-id/customers/quickstart-tenant-setup)
3. [Entra ID Requirements](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference)

---

##Publishing agents to 365 | Arturo | Foundry portal |
| Low-code agents & orchestration | Ricardo | Copilot Studio |
| Connecting to Foundry agents | Ricardo | Copilot Studio UI

| Task | Owner | Approach |
|------|-------|----------|
| Pro-code agents (complex logic) | Arturo | Foundry + Python/C# |
| Low-code orchestration | Ricardo | Copilot Studio |
| Agent registration in 365 | Both | Different paths, same registry |
| Cross-agent communication | Both | A2A protocol |
| Technical demos | Both | Combined presentations |

### *Agent Capabilities:**
   - Document what your agents do
   - Expected inputs and outputs
   - When Ricardo should use each agent

3. **Testing Together:**
   - Verify connectivity
   - Test with simple queries first
   - Troubleshoot any issuesabilities (what tools/functions available)
   - Ricardo describes when to invoke from orchestrator
   - Document expected inputs/outputs

3. **Security:**
   - Discuss authentication methods
   - Managed identities vs. API keys
   - Entra ID integration

---

## 🚨 Common Challenges & Solutions

### **Challenge Document endpoints explicitly when you publish
- **Tool:** Agent 365 registry shows published agentsin another
- **Solution:** Both need to be in Agent 365, or use A2A with proper auth
- **Best Practice:** Same tenant/subscription when possible

### **Challenge 2: Endpoint Discovery**
- **Problem:** Finding the right endpoint to call
- **Solution:** Use agent cards (A2A) or document endpoints explicitly
- **Tool:** Agent 365 provides registry for discovery

### **Challenge 3: Authentication**
- **Problem:** Securing agent-to-agent calls
- **Solution:** Use Entra ID (Microsoft identity platform)
- **Implementation:** Managed identities or service principals

### **Challenge 4: Observability**
- **Problem:** Hard to debug cross-platform agent calls
- **Solution:** Enable Application Insights (you have it in .env)
- **Monitor:** Both in Foundry portal and Copilot Studio analytics

---

## ✅ Next Steps Checklist

### **For You (Arturo):**
- [ ] Ensure all example agents are working
- [ ] Document endpoints for each agent
- [ ] Test publishing one agent to Agent 365
- [ ] Create A2A endpoint example
- [ ] Share tenant setup guide
- [ ] Prepare joint demo flow
- [ ] Schedule follow-up technical session

### **For Ricardo:**
- [ ] Install VS Code, Python, extensions
- [ ] Clone your GitHub repo
- [ ] Run basic examples locally
- [ ] Request tenant/subscription if needed
- [ ] Connect one of your agents to Copilot Studio
- [ ] Test basic orchestration locally
- [ ] Publish one simple agent (weather) to Agent 365
- [ ] Document the endpoint URL clearly
- [ ] Test that it appears in Agent 365 registry
- [ ] Share access with Ricardo
- [ ] Prepare simpleimplementation
- [ ] Agent registration walkthrough
- [ ] Security and authentication setup
- [ ] Observability configuration
- [ ] Demo rehearsal (optional for now)
- [ ] Review the GitHub repo examples (just read the code)
- [ ] Request tenant/subscription if needed
- [ ] Once Arturo publishes, find agent in Agent 365
- [ ] Connect to it from Copilot Studio
- [ ] Test simple query
**When Ricardo Needs Help:**
1. Installation issues → Share setup scripts
2. Connection problems → Test endpoints together
3. CodAgent registration walkthrough (Arturo shows, Ricardo learns)
- [ ] Endpoint connectivity testing (make first connection)
- [ ] Simple query testing (does it work?)
- [ ] Troubleshooting common issues
- [ ] Plan next steps
- Weekly check-ins during initial setup
- Ad-hoc sessions for troubleshooting
- Demo preparation sessions before presentations

---

## 🎓 Learning Path for Ricardo

**Week 1-2: Foundation**
- Run your basic examples
- Understand agent structure
- Explore Foundry portal
- Set up own tenant

**Week 3-4: Integration**
- Connect Foundry agent to Copilot Studio
- Test basic orchestration
- Implement A2A protocol
- Security configuration

**WeekSimplified Learning Path for Ricardo

**Phase 1: Understanding (Week 1-2)**
- Review GitHub repo examples (just read, don't run yet)
- Understand what Foundry agents do
- Learn about Agent 365 registry
- Set up own tenant/subscription

**Phase 2: First Connection (Week 3-4)**
- Watch Arturo publish an agent to Agent 365
- Find the agent in Agent 365
- Connect to it from Copilot Studio
- Test with simple query

**Phase 3: Building Confidence (Week 5-6)**
- Create simple Copilot Studio agent
- Connect to multiple Foundry agents
- Build basic demo
- Document process for presentations

**Future Phases (Later):**
- A2A protocol (advanced topic)
- Complex orchestration
- Production deploy (Simplified Focus)

1. **Start Simple** - Get one agent working first, then expand
2. **Agent 365 is the registry** - Where all agents get registered and discovered
3. **Publishing is straightforward** - Foundry portal makes it easy
4. **Copilot Studio can connect** - Just needs endpoint URL and Agent ID
5. **Same tenant preferred** - Avoids cross-tenant complexity
6. **Documentation is key** - Clear endpoints and agent descriptions
7. **Complementary not competing** - Pro-code + low-code = powerful solutions
8. **A2A is for later** - Focus on basic publishing and registration first
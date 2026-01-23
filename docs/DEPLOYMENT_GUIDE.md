# Step-by-Step: Deploying Foundry Agents for Ricardo

**Goal:** Deploy your Foundry agents so Ricardo can connect to them from Copilot Studio

---

## 📋 Overview of the Process

Here's what will happen end-to-end:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR SIDE (Arturo)                           │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Create/test agent locally in Foundry                             │
│ 2. Deploy agent to Foundry (hosted agent)                           │
│ 3. Create Agent Application (stable endpoint)                       │
│ 4. Publish to Agent 365 OR M365 Copilot                             │
│ 5. Share info with Ricardo                                          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     RICARDO'S SIDE                                  │
├─────────────────────────────────────────────────────────────────────┤
│ 6. Find agent in Agent 365 registry                                 │
│ 7. In Copilot Studio → Add external agent → Microsoft Foundry       │
│ 8. Enter your Foundry project endpoint + Agent ID                   │
│ 9. Test connection and invoke your agent                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Two Deployment Paths (Choose One)

### **Path A: Publish to Agent 365** ⭐ RECOMMENDED
- **Best for:** Enterprise-wide agent management
- **Benefits:** Centralized registry, security, governance
- **Requires:** Frontier Preview Program access
- **Tool:** Script-based deployment

### **Path B: Publish to M365 Copilot/Teams**
- **Best for:** Direct Teams/M365 Copilot integration
- **Benefits:** Simpler, UI-based process
- **Requires:** Standard Foundry access
- **Tool:** Foundry Portal UI

---

## 🚀 PATH A: Deploy to Agent 365 (Detailed Steps)

### **Prerequisites (Check These First):**
- [ ] Access to [Frontier Preview Program](https://adoption.microsoft.com/copilot/frontier-program/)
- [ ] [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) installed
- [ ] [Docker](https://www.docker.com/) installed
- [ ] [.NET 9.0 SDK](https://dotnet.microsoft.com/download) or later
- [ ] Your Foundry project is set up with proper permissions

### **Step 1: Prepare Your Agent Code**

Your existing agents in `/azure_ai/` are ready to go! Example:
```bash
cd /Users/arturoquiroga/GITHUB/BASIC_AGENTS_IN_FOUNDRY/azure_ai
```

You already have:
- ✅ `azure_ai_basic.py` (weather agent with real API)
- ✅ `azure_ai_with_bing_grounding.py`
- ✅ `azure_ai_with_sharepoint.py`
- ✅ `.env` file with credentials

### **Step 2: Run the Agent 365 Publishing Script**

**Download and run the script:**
```bash
# Get the script from GitHub
curl -L https://go.microsoft.com/fwlink/?linkid=2343518 -o publish_agent_365.sh
chmod +x publish_agent_365.sh

# Run it
./publish_agent_365.sh
```

**What this script does automatically:**

1. **Creates Foundry Project** (if needed)
   - Sets up hosted agent support
   - Configures Azure Container Registry permissions

2. **Creates Agent Application**
   - Generates a stable endpoint URL
   - Creates unique identity for the agent
   - Configures Azure Bot Service permissions

3. **Creates Azure Bot Service**
   - Acts as relay between M365 and Foundry
   - Auto-configured with application endpoint

4. **Builds & Deploys Hosted Agent**
   - Packages your code into Docker container
   - Pushes to Azure Container Registry
   - Registers with Foundry

5. **Publishes to Agent 365**
   - Registers in Agent 365 control plane
   - Creates digital worker identity
   - **Waits for admin approval**

### **Step 3: Note the Generated Information**

After the script completes, you'll get output like this:

```
✅ Agent Published Successfully!

📝 INFORMATION FOR RICARDO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent Name: WeatherAgent
Agent ID: agent_abc123xyz789

Foundry Project Endpoint:
https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject

Agent Application Endpoint:
https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject/applications/app_weather123

Azure Bot Service Endpoint:
https://weather-agent-bot.azurewebsites.net/api/messages

Tenant ID: 7a28b21e-0d3e-4435-a686-d92889d4ee96
Application ID: f1234567-89ab-cdef-0123-456789abcdef

⚠️  NEXT STEP: Tenant admin must approve this agent before it's available
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**✍️ COPY THESE VALUES - Ricardo will need:**
- ✅ Foundry Project Endpoint
- ✅ Agent ID
- ✅ Agent Name

### **Step 4: Request Admin Approval**

Your agent needs admin approval before it's visible in Agent 365:

1. Go to [Microsoft Entra Admin Center](https://entra.microsoft.com)
2. Navigate to **Identity** → **Applications** → **Enterprise applications**
3. Find your agent by Application ID
4. Request approval from your tenant admin
5. Admin reviews and approves

**Typical approval time:** Few hours to 1 day

---

## 🚀 PATH B: Deploy to M365 Copilot/Teams (UI Method)

This is simpler if you don't have Frontier Preview access yet.

### **Step 1: Open Foundry Portal**

1. Go to [https://ai.azure.com](https://ai.azure.com)
2. Select your project: `firstProject`
3. Navigate to **Agents** in the left menu

### **Step 2: Find Your Agent**

1. You should see your agents listed (e.g., "BasicWeatherAgent")
2. If not, run one of your Python scripts first to create the agent:
   ```bash
   cd /Users/arturoquiroga/GITHUB/BASIC_AGENTS_IN_FOUNDRY/azure_ai
   python azure_ai_basic.py
   ```

### **Step 3: Publish the Agent**

1. Select your agent version
2. Click **"Publish"** button (top right)
3. Click **"Publish"** again in the dialog
4. Select **"Publish to Teams and Microsoft 365 Copilot"**

### **Step 4: Configure Publishing Details**

Fill in the form:

**Basic Information:**
- **Name:** Weather Agent
- **Short Description:** Provides real-time weather information
- **Full Description:** This agent fetches real weather data from OpenWeatherMap API and provides current conditions including temperature, humidity, and forecasts.

**Azure Bot Service:**
- Select **"Create an Azure Bot Service"** from dropdown
- It will auto-generate the bot service

**Metadata (Required):**
- **Icons:** Upload small (32x32) and large (192x192) PNG icons
- **Publisher Name:** Microsoft (or your org name)
- **Privacy Policy URL:** Your privacy policy URL
- **Terms of Use URL:** Your terms of use URL

### **Step 5: Prepare and Download Package**

1. Click **"Prepare Agent"**
2. Wait for packaging to complete (1-2 minutes)
3. You can download the package for testing OR continue to publish

### **Step 6: Choose Publishing Scope**

**Option A - Shared Scope:**
- Agent appears under **"Your agents"** in M365 Copilot
- Available to you immediately
- Good for testing

**Option B - Organization Scope:**
- Agent appears under **"Built by your org"**
- Requires admin approval in Microsoft Admin Center
- Good for org-wide deployment

### **Step 7: Copy the Generated Info**

After publishing, note down:

```
📝 INFORMATION FOR RICARDO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent Name: WeatherAgent
Agent ID: [shown in portal - looks like: asst_abc123xyz789]

Foundry Project Endpoint:
https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject

Application ID: [auto-generated UUID]
Tenant ID: 7a28b21e-0d3e-4435-a686-d92889d4ee96
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📦 What Ricardo Needs from You

### **Minimal Information Package:**

Create a simple text file or email with:

```
AGENT CONNECTION INFO
=====================

Agent Name: Weather Agent
Description: Provides real-time weather data using OpenWeatherMap API

Required for Copilot Studio Connection:
1. Foundry Project Endpoint: 
   https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject

2. Agent ID: 
   agent_abc123xyz789
   (or asst_abc123xyz789 depending on deployment method)

Optional (for his reference):
- Tenant ID: 7a28b21e-0d3e-4435-a686-d92889d4ee96
- Application ID: [if published to Agent 365]

Test Query: "What's the weather in Seattle?"
Expected Response: Real weather data with temperature, conditions, humidity
```

### **Additional Context to Share:**

**Agent Capabilities:**
- Input: City name (e.g., "Seattle", "Tokyo", "London")
- Output: Current weather with temperature (°C and °F), conditions, humidity, wind speed
- Data Source: OpenWeatherMap API (real-time data)
- Response Time: ~2-3 seconds

**When to Use This Agent:**
- User asks about weather in any location
- Needs current weather conditions
- Wants specific weather details (temperature, humidity, etc.)

---

## 🔍 How to Find Your Agent ID

### **In Foundry Portal:**

1. Go to [https://ai.azure.com](https://ai.azure.com)
2. Navigate to your project → **Agents**
3. Click on your agent
4. Look for **"ID"** or **"Agent ID"** in the details panel
   - Format: `asst_xxxxxxxxxxxxxxxxx` or `agent_xxxxx`

### **Via Azure CLI:**

```bash
# List all agents in your project
az cognitiveservices account deployment list \
  --name aq-ai-foundry-Sweden-Central \
  --resource-group AI-FOUNDRY-RG

# Get specific agent details
az cognitiveservices account deployment show \
  --name aq-ai-foundry-Sweden-Central \
  --resource-group AI-FOUNDRY-RG \
  --deployment-name WeatherAgent
```

### **Programmatically (Python):**

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
project_client = AIProjectClient(
    credential=credential,
    endpoint="https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject"
)

# List all agents
agents = project_client.agents.list_agents()
for agent in agents:
    print(f"Name: {agent.name}")
    print(f"ID: {agent.id}")
    print("---")
```

---

## 🤝 Ricardo's Connection Process (For Your Understanding)

Once you give Ricardo the information, here's what he'll do:

### **Step 1: Open Copilot Studio**
- Go to [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
- Select or create his agent

### **Step 2: Add External Agent**
1. Go to **"Agents"** page in his agent
2. Click **"Add an agent"**
3. Under **"Connect to an external agent"**
4. Select **"Microsoft Foundry"**

### **Step 3: Create Connection**
- First time: He creates a connection
- **Foundry Project Endpoint:** (you provided this)
- Saves the connection

### **Step 4: Configure Agent**
- **Name:** Weather Agent
- **Description:** (you provided this)
- **Agent ID:** (you provided this)
- Optionally adjust description for better context

### **Step 5: Test**
- Click **"Test"** in Copilot Studio
- Type: "What's the weather in Seattle?"
- Your Foundry agent responds!

---

## 🧪 Testing Before Sharing with Ricardo

### **Test 1: Local Agent Works**

```bash
cd /Users/arturoquiroga/GITHUB/BASIC_AGENTS_IN_FOUNDRY/azure_ai
python azure_ai_basic.py
```

Expected output:
```
=== Non-streaming Response Example ===
User: What's the weather like in Seattle?
Agent: 🌤️ Weather in Seattle, US:
🌡️ Temperature: 15.2°C (59.4°F)
☁️ Conditions: Partly cloudy
💧 Humidity: 72%
💨 Wind: 3.5 m/s
```

### **Test 2: Agent Appears in Foundry Portal**

1. Go to [https://ai.azure.com](https://ai.azure.com)
2. Navigate to your project
3. Click **Agents**
4. Verify your agent is listed with correct name

### **Test 3: Published Successfully**

- Check Agent 365 registry (if using Path A)
- OR check M365 Copilot agent store (if using Path B)
- Verify you can see the agent

### **Test 4: Endpoint is Accessible**

```bash
# Test the endpoint responds (if you have the application endpoint)
curl -X GET "https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject/applications/your-app-id" \
  -H "Authorization: Bearer $(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)"
```

---

## ⚠️ Common Issues & Solutions

### **Issue 1: "Container Registry permissions error"**

**Solution:**
```bash
# Grant permissions to project's managed identity
az role assignment create \
  --assignee <project-managed-identity-id> \
  --role "AcrPull" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.ContainerRegistry/registries/<registry-name>
```

### **Issue 2: "Agent not appearing in Agent 365"**

**Causes:**
- Admin approval pending
- Publishing didn't complete
- Wrong tenant

**Solution:**
- Check admin approval status in Entra
- Re-run publishing script
- Verify tenant ID matches

### **Issue 3: "Ricardo can't find the agent"**

**Causes:**
- Different tenant
- Agent not published yet
- No permissions

**Solution:**
- Ensure same tenant for both of you
- Verify agent shows in your Agent 365
- Check Ricardo has access to the project/application

### **Issue 4: "Connection fails in Copilot Studio"**

**Causes:**
- Wrong endpoint URL
- Wrong Agent ID
- Authentication issue

**Solution:**
- Double-check endpoint URL (no typos)
- Verify Agent ID is correct format
- Ensure connection has proper credentials

---

## 📊 Information Summary Table

Here's everything Ricardo needs in one place:

| **What Ricardo Needs** | **Where You Find It** | **Example Value** |
|------------------------|----------------------|-------------------|
| Foundry Project Endpoint | Azure Portal → Foundry Project → Overview | `https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject` |
| Agent ID | Foundry Portal → Agents → Select agent → ID | `asst_abc123xyz` or `agent_abc123` |
| Agent Name | What you named it | `WeatherAgent` |
| Description | Write this for Ricardo | "Provides real-time weather data..." |
| Test Query | You provide | "What's the weather in Seattle?" |

**Optional but helpful:**
- Tenant ID
- Application ID (for Agent 365 path)
- Bot Service endpoint (auto-generated)
- Expected response format
- Rate limits or usage notes

---

## 🎯 Quick Start Commands (Your Workflow)

### **Option 1: Using Azure Developer CLI (Recommended)**

```bash
# Install azd if not already
brew install azure-cli  # macOS

# Login
az login

# Navigate to your project
cd /Users/arturoquiroga/GITHUB/BASIC_AGENTS_IN_FOUNDRY/azure_ai

# Deploy using azd (if you have azd template)
azd up

# Or use the Agent 365 script
curl -L https://go.microsoft.com/fwlink/?linkid=2343518 -o publish.sh
chmod +x publish.sh
./publish.sh
```

### **Option 2: Using Foundry Portal (Simplest)**

1. Run your agent locally first to create it
2. Go to https://ai.azure.com
3. Select agent → Publish → Teams and M365 Copilot
4. Fill in metadata
5. Click Publish
6. Copy Agent ID and endpoint
7. Share with Ricardo

---

## 📚 Next Steps After Deployment

### **For You:**

1. ✅ Deploy one agent (start with weather)
2. ✅ Test it works in Foundry playground
3. ✅ Publish to Agent 365 OR M365 Copilot
4. ✅ Get Agent ID and endpoint
5. ✅ Create information package for Ricardo
6. ✅ Schedule session to walk through connection together

### **For Ricardo:**

1. ⏳ Receive information package from you
2. ⏳ Open Copilot Studio
3. ⏳ Add external agent → Microsoft Foundry
4. ⏳ Enter your endpoint and Agent ID
5. ⏳ Test connection
6. ⏳ Build his demo

### **Together:**

- Test the connection works end-to-end
- Debug any issues
- Plan for deploying additional agents
- Document the process for presentations

---

## 🔗 Essential Links

**Foundry Portal:**
- [https://ai.azure.com](https://ai.azure.com)

**Copilot Studio:**
- [https://copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)

**Azure Portal:**
- [https://portal.azure.com](https://portal.azure.com)

**Documentation:**
- [Publish to Agent 365](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/agent-365)
- [Publish to M365 Copilot](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/publish-copilot)
- [Connect in Copilot Studio](https://learn.microsoft.com/microsoft-copilot-studio/add-agent-foundry-agent)

**Support:**
- [Frontier Preview Program](https://adoption.microsoft.com/copilot/frontier-program/)
- [Azure Developer CLI Docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)

---

## ✅ Deployment Checklist

**Before You Start:**
- [ ] Your agents run successfully locally
- [ ] .env file has all required credentials
- [ ] You have Foundry project access
- [ ] You have Azure subscription permissions
- [ ] (Optional) Frontier Preview Program access

**During Deployment:**
- [ ] Agent builds/deploys without errors
- [ ] Agent appears in Foundry portal
- [ ] Agent is published to Agent 365 or M365
- [ ] Admin approval requested (if required)
- [ ] Agent ID noted down
- [ ] Endpoint URL copied

**After Deployment:**
- [ ] Test agent in Foundry playground
- [ ] Verify agent shows in registry
- [ ] Create info package for Ricardo
- [ ] Share credentials securely
- [ ] Schedule walkthrough session

**Ricardo's Side:**
- [ ] Receives your information package
- [ ] Opens Copilot Studio
- [ ] Creates connection to Foundry
- [ ] Adds your agent
- [ ] Tests successfully
- [ ] Can invoke your agent from his agent

---

**Last Updated:** January 22, 2026  
**Your Name:** Arturo Quiroga  
**Working With:** Ricardo Mejia

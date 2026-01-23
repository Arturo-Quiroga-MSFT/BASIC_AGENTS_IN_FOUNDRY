# Local Testing Guide for Hosted Weather Agent

This guide explains how to test the hosted weather agent locally before deploying to Azure.

## Prerequisites

- Docker Desktop installed and running
- Python 3.11+ (for standalone testing)
- OpenWeatherMap API key ([get one free here](https://openweathermap.org/api))
- Azure AI Project endpoint (if testing with full Azure integration)

## Option 1: Quick Function Test (No Docker, No Azure)

The fastest way to verify the weather functionality works:

### Steps

1. **Install Python dependencies:**
```bash
cd hosted_agent
pip install httpx python-dotenv
```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

Edit `.env` and add your OpenWeather API key:
```env
OPENWEATHER_API_KEY=your_api_key_here
```

3. **Run the test script:**
```bash
python test_local.py
```

### Expected Output

```
============================================================
Testing Weather Agent Locally
============================================================

Testing weather for: Mexico City
------------------------------------------------------------
✅ Success!
   Temperature: 18.5°C
   Conditions: Clear sky
   Humidity: 45%
   Wind: 3.6 m/s

Testing weather for: Toronto
------------------------------------------------------------
✅ Success!
   Temperature: -2.3°C
   Conditions: Snow
   Humidity: 85%
   Wind: 4.1 m/s

...
```

This confirms your weather function works correctly.

---

## Option 2: Container Test with Service Principal

To test the complete Activity Protocol implementation with Azure AI Foundry integration.

### Why Service Principal?

When running locally in Docker, the container cannot access your personal Azure credentials. You need to use a service principal (app identity) that works inside containers.

### Setup Steps

#### 1. Create Azure Service Principal

```bash
# Create service principal
az ad sp create-for-rbac --name "weather-agent-local-test" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --query '{clientId:appId, clientSecret:password, tenantId:tenant}' \
  -o json
```

Save the output - you'll need all three values.

#### 2. Grant AI Project Access

```bash
# Get your AI Project resource ID
az cognitiveservices account show \
  --name {your-project-name} \
  --resource-group {resource-group} \
  --query id -o tsv

# Grant Cognitive Services User role
az role assignment create \
  --assignee {service-principal-client-id} \
  --role "Cognitive Services User" \
  --scope {project-resource-id}
```

#### 3. Configure Environment

Create `.env` file with service principal credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Azure AI Project
AZURE_AI_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/

# OpenWeather API  
OPENWEATHER_API_KEY=your_openweather_key

# Service Principal for Authentication
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=your_sp_secret_here
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Optional Configuration
PORT=8080
LOG_LEVEL=INFO
AGENT_NAME=WeatherAgent
AGENT_VERSION=2
```

#### 4. Build Container

```bash
./deploy/build.sh
```

Expected output:
```
🚀 Building Weather Agent Docker image...
[+] Building 45.2s (12/12) FINISHED
✅ Build successful! Image: weatheragent:latest
```

#### 5. Run Container

```bash
docker run -d \
  -p 8080:8080 \
  --name weatheragent-test \
  --env-file .env \
  weatheragent:latest
```

#### 6. Verify Health

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent": "WeatherAgent",
  "version": "2",
  "config": {
    "port": 8080,
    "azure_endpoint_configured": true,
    "openweather_key_configured": true
  }
}
```

#### 7. Test with Activity Protocol Message

```bash
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "id": "test-msg-001",
    "timestamp": "2025-06-03T12:00:00Z",
    "from": {
      "id": "user-test-123",
      "name": "Test User"
    },
    "conversation": {
      "id": "conv-test-001"
    },
    "text": "What is the weather in Mexico City?"
  }'
```

Expected response:
```json
{
  "type": "message",
  "text": "The weather in Mexico City is currently 18.5°C with clear skies...",
  "timestamp": "2025-06-03T12:00:15Z"
}
```

#### 8. View Logs

```bash
# Follow logs in real-time
docker logs -f weatheragent-test

# View last 50 lines
docker logs weatheragent-test --tail 50
```

#### 9. Cleanup

```bash
# Stop and remove container
docker stop weatheragent-test
docker rm weatheragent-test

# Remove image (optional)
docker rmi weatheragent:latest
```

---

## Troubleshooting

### Authentication Errors

**Problem:** `DefaultAzureCredential failed to retrieve a token`

**Solutions:**
1. Verify service principal credentials in `.env`
2. Check SP has correct role assignment:
   ```bash
   az role assignment list --assignee {client-id} --all
   ```
3. Test SP credentials work:
   ```bash
   az login --service-principal \
     --username {client-id} \
     --password {client-secret} \
     --tenant {tenant-id}
   ```

### Container Won't Start

**Problem:** Container exits immediately

**Check logs:**
```bash
docker logs weatheragent-test
```

**Common causes:**
- Missing required environment variables
- Invalid Azure endpoint URL
- Port 8080 already in use

**Fix port conflict:**
```bash
# Use different port
docker run -d -p 8081:8080 --name weatheragent-test ...
curl http://localhost:8081/health
```

### Weather Function Fails

**Problem:** `get_real_weather` returns errors

**Check:**
1. OpenWeather API key is valid
2. API key has sufficient quota
3. City name is correct

**Test API key directly:**
```bash
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid={your-api-key}&units=metric"
```

### "No module named 'azure.ai.projects'"

**Problem:** Container build fails

**Fix:** Ensure `requirements.txt` includes:
```
azure-ai-projects>=2.0.0b1
```

### Container Can't Reach Azure

**Problem:** Network timeouts to Azure endpoints

**Check:**
1. Docker has internet access
2. No firewall blocking Azure IPs
3. Azure endpoint URL is correct

---

## Testing Checklist

Before deploying to Azure, verify:

- [ ] `test_local.py` runs successfully
- [ ] Docker image builds without errors
- [ ] Container starts and health check passes
- [ ] Service principal authentication works
- [ ] Activity Protocol messages are processed
- [ ] Weather function returns correct data
- [ ] Logs show no errors
- [ ] Container responds within reasonable time (<5s)

---

## Next Steps

Once local testing is complete:

1. **Deploy to Azure Container Registry**
   ```bash
   ./deploy/deploy.sh
   ```

2. **Register as Hosted Agent in Foundry**
   - Use Azure AI Foundry portal
   - Or run `./deploy/agent365-setup.sh`

3. **Create Agent Application**
   - Configure stable endpoint
   - Set up Bot Service relay

4. **Publish to Agent365**
   - Mark as digital worker
   - Submit for admin approval

See main [README.md](README.md) for deployment instructions.

---

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Activity Protocol Specification](https://docs.microsoft.com/azure/bot-service/rest-api/bot-framework-rest-connector-api-reference)
- [Service Principal Authentication](https://learn.microsoft.com/azure/developer/python/sdk/authentication-overview)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

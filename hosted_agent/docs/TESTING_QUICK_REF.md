# Testing Quick Reference

## Three Testing Approaches

### 🚀 Option 1: Function Test Only (Fastest)
**Best for:** Quick validation of weather functionality  
**Requirements:** Python 3.11+, OpenWeather API key  
**No Azure needed, No Docker needed**

```bash
pip install httpx python-dotenv
cp .env.example .env
# Add OPENWEATHER_API_KEY to .env
python test_local.py
```

---

### 🐳 Option 2: Docker with Service Principal
**Best for:** Full Activity Protocol testing before Azure deployment  
**Requirements:** Docker, Azure subscription, Azure CLI

```bash
# One-time setup
./setup-local-auth.sh  # Creates service principal, writes .env

# Build and run
./deploy/build.sh
docker run -d -p 8080:8080 --env-file .env --name weatheragent-test weatheragent:latest

# Test
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{"type":"message","from":{"id":"test-user"},"text":"weather in Mexico City"}'

# View logs
docker logs -f weatheragent-test

# Cleanup
docker stop weatheragent-test && docker rm weatheragent-test
```

---

### ☁️ Option 3: Deploy to Azure
**Best for:** Production testing in real environment  
**Requirements:** Azure Container Registry, AI Foundry project

```bash
./deploy/deploy.sh
./deploy/agent365-setup.sh
```

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Auth error in Docker | Run `./setup-local-auth.sh` |
| Weather function fails | Check `OPENWEATHER_API_KEY` in `.env` |
| Container won't start | Check logs: `docker logs weatheragent-test` |
| Port 8080 in use | Use `-p 8081:8080` instead |
| Build fails | Ensure Docker Desktop is running |

---

## Testing Checklist

Before deploying to Azure:

- [ ] `test_local.py` runs successfully (Option 1)
- [ ] Container builds: `./deploy/build.sh`
- [ ] Health check passes: `curl http://localhost:8080/health`
- [ ] Message endpoint works (Option 2)
- [ ] No errors in logs: `docker logs weatheragent-test`

---

## Need Help?

- **Detailed guide:** [LOCAL_TESTING.md](LOCAL_TESTING.md)
- **Deployment guide:** [README.md](README.md)
- **Service principal setup:** Run `./setup-local-auth.sh`

# Quick Reference - Hosted Agent Commands

## Local Testing

```bash
# Run agent locally
python agent.py

# Test with automated suite
python test_local.py

# Interactive testing
python test_local.py -i
```

## Docker Operations

```bash
# Build image
docker build -t myagent:v1 .

# Test locally
docker run -p 8088:8088 -e AZURE_AI_PROJECT_ENDPOINT="..." myagent:v1

# Build and push to ACR (automated)
./docker_build_push.sh

# Manual ACR operations
az acr login --name myregistry
docker tag myagent:v1 myregistry.azurecr.io/myagent:v1
docker push myregistry.azurecr.io/myagent:v1
```

## Azure Setup

```bash
# Configure ACR permissions
./configure_acr_permissions.sh

# Create capability host (once per account)
./create_capability_host.sh
```

## Agent Management

```bash
# Create agent version
python create_agent.py

# Start deployment
python manage_agent.py start
python manage_agent.py start --min-replicas 1 --max-replicas 3

# Stop deployment
python manage_agent.py stop

# Update configuration
python manage_agent.py update --min-replicas 2 --max-replicas 5

# Show agent details
python manage_agent.py show

# List all versions
python manage_agent.py list

# Delete deployment (keep version)
python manage_agent.py delete-deployment

# Delete version
python manage_agent.py delete --version 1

# Delete all versions
python manage_agent.py delete
```

## Testing Deployed Agent

```bash
# Single test
python invoke_agent.py

# Custom message
python invoke_agent.py "Your message here"

# Interactive mode
python invoke_agent.py -i
```

## Azure CLI Direct Commands

```bash
# Start agent
az cognitiveservices agent start \
  --account-name <account> \
  --project-name <project> \
  --name <agent-name> \
  --agent-version 1

# Stop agent
az cognitiveservices agent stop \
  --account-name <account> \
  --project-name <project> \
  --name <agent-name> \
  --agent-version 1

# Update agent
az cognitiveservices agent update \
  --account-name <account> \
  --project-name <project> \
  --name <agent-name> \
  --agent-version 1 \
  --min-replicas 1 \
  --max-replicas 2

# Show agent
az cognitiveservices agent show \
  --account-name <account> \
  --project-name <project> \
  --name <agent-name>

# List versions
az cognitiveservices agent list-versions \
  --account-name <account> \
  --project-name <project> \
  --name <agent-name>
```

## Debugging

```bash
# Check Docker images
docker images | grep myagent

# Check ACR images
az acr repository list --name myregistry
az acr repository show-tags --name myregistry --repository myagent

# Check Azure login
az account show

# Check ACR permissions
az role assignment list --assignee <principal-id> --scope <acr-id>

# View container logs (use REST API or Portal)
```

## Environment Variables Quick Check

```bash
# Verify configuration
cat .env | grep -v '^#' | grep -v '^$'

# Test Azure connection
az account show

# Test ACR connection
az acr show --name <acr-name>
```

## Common Workflows

### First Time Setup
```bash
1. Configure .env file
2. python agent.py          # Test locally
3. python test_local.py     # Verify locally
4. ./docker_build_push.sh   # Build and push
5. ./configure_acr_permissions.sh
6. ./create_capability_host.sh
7. python create_agent.py   # Create version
8. python manage_agent.py start
9. python invoke_agent.py   # Test deployed
```

### Update Agent Code
```bash
1. Edit agent.py
2. Update IMAGE_TAG in .env (e.g., v2)
3. ./docker_build_push.sh
4. Update CONTAINER_IMAGE in .env
5. python create_agent.py   # Creates new version
6. python manage_agent.py start --agent-version 2
```

### Scale Agent
```bash
python manage_agent.py update --min-replicas 2 --max-replicas 5
```

### Troubleshoot
```bash
1. python manage_agent.py show
2. Check logs in Azure Portal
3. Verify ACR image exists
4. Check Azure credentials
```

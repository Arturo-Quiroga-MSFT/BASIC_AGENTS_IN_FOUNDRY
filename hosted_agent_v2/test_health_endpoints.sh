#!/bin/bash
# Test health endpoints locally

echo "Starting agent in background..."
python agent.py &
AGENT_PID=$!

# Wait for startup
sleep 5

echo -e "\n✅ Testing /liveness endpoint (built-in)..."
curl -s http://localhost:8088/liveness

echo -e "\n✅ Testing /readiness endpoint (built-in)..."
curl -s http://localhost:8088/readiness | jq .

echo -e "\n✅ Testing /responses endpoint (original)..."
curl -s -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is the weather in Paris?"}],"model":"weather-agent","stream":false}' | head -c 200

echo -e "\n\n🛑 Stopping agent..."
kill $AGENT_PID

echo "✅ Done!"

#!/usr/bin/env bash
# ============================================================================
# run_demo.sh — Start the Cloud ↔ Local A2A demo
#
# Usage:
#   ./run_demo.sh              # Start server + interactive client
#   ./run_demo.sh server       # Start only the A2A server
#   ./run_demo.sh client       # Start only the A2A client
#   ./run_demo.sh test         # Quick smoke test (single query)
#
# Options (via env vars):
#   MODEL=qwen2.5-0.5b ./run_demo.sh    # Use a different model
#   PORT=8888 ./run_demo.sh              # Use a different port
#   HOST=https://abc.ngrok.io ./run_demo.sh client  # Connect to remote
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODEL="${MODEL:-phi-4-mini}"
PORT="${PORT:-9999}"
HOST="${HOST:-http://localhost:${PORT}}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║         Cloud ↔ Local A2A Demo  (Python / MAF)             ║"
    echo "║                                                            ║"
    echo "║  Server: a2a-sdk + Foundry Local ($MODEL)"
    echo "║  Client: agent-framework-a2a (MAF A2AAgent)                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

start_server() {
    echo -e "${GREEN}Starting A2A Server...${NC}"
    echo "  Model: $MODEL"
    echo "  Port:  $PORT"
    echo ""
    python local_a2a_server.py --model "$MODEL" --port "$PORT"
}

start_client() {
    echo -e "${GREEN}Connecting A2A Client...${NC}"
    echo "  Host: $HOST"
    echo ""
    python cloud_a2a_client.py --host "$HOST"
}

run_test() {
    echo -e "${GREEN}Running smoke test...${NC}"
    echo "  Host: $HOST"
    echo ""
    python cloud_a2a_client.py --host "$HOST" --query "Hello! What model are you running on and what can you help with?"
}

# --- Main ---

print_banner

case "${1:-}" in
    server)
        start_server
        ;;
    client)
        start_client
        ;;
    test)
        run_test
        ;;
    "")
        # Default: start server in background, then run client
        echo -e "${YELLOW}Starting server in background, then launching client...${NC}"
        echo -e "${YELLOW}(Press Ctrl+C to stop everything)${NC}"
        echo ""

        # Start server in background
        python local_a2a_server.py --model "$MODEL" --port "$PORT" &
        SERVER_PID=$!

        # Wait for server to be ready
        echo "Waiting for server to start..."
        for i in $(seq 1 30); do
            if curl -s "http://localhost:${PORT}/v1/card" > /dev/null 2>&1; then
                echo -e "${GREEN}Server is ready!${NC}"
                break
            fi
            if [ $i -eq 30 ]; then
                echo "Server failed to start within 30 seconds."
                kill $SERVER_PID 2>/dev/null || true
                exit 1
            fi
            sleep 1
        done

        # Cleanup on exit
        trap "echo ''; echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null || true; echo 'Done.'" EXIT

        echo ""

        # Run client interactively
        start_client
        ;;
    *)
        echo "Usage: $0 [server|client|test]"
        exit 1
        ;;
esac

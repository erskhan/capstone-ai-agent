#!/bin/bash
# Script to run the backend API server with visible logs in the terminal

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Loan Approval System Backend...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Set environment variables
export LOG_LEVEL=INFO
export DEBUG=false

echo -e "${GREEN}✓ Environment:${NC}"
echo "  - LOG_LEVEL: $LOG_LEVEL"
echo "  - DEBUG: $DEBUG"
echo "  - API_URL: http://0.0.0.0:8000"
echo ""

echo -e "${GREEN}✓ Starting API Server on port 8000...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Log Format:${NC}"
echo "  [TIMESTAMP] [LEVEL] module_name: message | correlation_id=..."
echo ""
echo -e "${BLUE}✅ When you submit an application:${NC}"
echo "  1. You'll see 'Received loan application' in the logs"
echo "  2. Background processing starts automatically"
echo "  3. Watch agents working through each step:"
echo "     - Applicant Agent (validation & profiling)"
echo "     - Risk Agent (financial analysis)"
echo "     - Decision Agent (approval decision)"
echo "     - Compliance Agent (regulatory checks)"
echo "     - Notification Agent (notification queueing)"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Run the API server
/home/ubuntu/anthropic-env/bin/uvicorn backend.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000

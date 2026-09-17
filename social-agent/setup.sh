#!/usr/bin/env bash
# ONE-TIME SETUP - creates the agent + environment and records their IDs.
# Requires: `ant auth login` already run (or ANTHROPIC_API_KEY set).
set -euo pipefail
cd "$(dirname "$0")"

AGENT_ID=$(ant beta:agents create < nikolaevich-social.agent.yaml --transform id -r)
ENV_ID=$(ant beta:environments create < nikolaevich-social.environment.yaml --transform id -r)

{
  echo "AGENT_ID=$AGENT_ID"
  echo "ENV_ID=$ENV_ID"
} > .env

echo "Created agent $AGENT_ID and environment $ENV_ID"
echo "IDs written to social-agent/.env"
echo
echo "Next: fill in ZAPIER_MCP_URL and ZAPIER_MCP_TOKEN, then run setup_vault_and_deployment.py"

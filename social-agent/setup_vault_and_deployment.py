# ONE-TIME SETUP - run once, after setup.sh and after you've created the
# Zapier MCP server. Creates the vault credential and the scheduled
# deployment, and appends their IDs to .env.
#
# Before running, export (don't commit these):
#   export ZAPIER_MCP_URL="https://mcp.zapier.com/..."
#   export ZAPIER_MCP_TOKEN="<the API key/token from your Zapier MCP server page>"

import os
from pathlib import Path

import anthropic

ENV_FILE = Path(__file__).parent / ".env"


def load_env():
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line:
                key, _, val = line.partition("=")
                values[key.strip()] = val.strip()
    return values


env = load_env()
client = anthropic.Anthropic()

AGENT_ID = env["AGENT_ID"]
ENV_ID = env["ENV_ID"]
ZAPIER_MCP_URL = os.environ["ZAPIER_MCP_URL"]
ZAPIER_MCP_TOKEN = os.environ["ZAPIER_MCP_TOKEN"]

# 1. Vault + Zapier MCP credential (never committed - write-only on the server)
vault = client.beta.vaults.create(name="nikolaevich-social-vault")
client.beta.vaults.credentials.create(
    vault_id=vault.id,
    display_name="Zapier MCP (Instagram + Facebook)",
    auth={
        "type": "static_bearer",
        "mcp_server_url": ZAPIER_MCP_URL,
        "token": ZAPIER_MCP_TOKEN,
    },
)
print(f"Created vault {vault.id}")

# 2. Scheduled deployment - fires daily, kicks off with an outcome + starter rubric
STARTER_RUBRIC = """# Social engagement draft rubric - starter, tune the criteria
- Every Instagram and Facebook comment, mention, and DM from the last 24 hours has been reviewed.
- Each item that warrants a reply has a drafted response in the brand voice
  (thoughtful, narrative, ecological/coastal throughline -- not corporate).
- Drafts reference real portfolio details only (Circe, Iris, Potami, Vestal
  Virgins, the free consultation) -- no fabricated project facts.
- Spam/bot comments are flagged "skip", not drafted with an engagement reply.
- Output is a single `drafts.md` in /mnt/session/outputs/ listing, per item:
  platform, post/thread link or ID, original comment/message, drafted reply,
  and a suggested action (e.g. "invite to free consultation").
- Nothing is posted or sent -- every item stays draft-only pending human review.
"""

deployment = client.beta.deployments.create(
    name="Nikolaevich Designs daily social check-in",
    agent=AGENT_ID,
    environment_id=ENV_ID,
    vault_ids=[vault.id],
    initial_events=[
        {
            "type": "user.define_outcome",
            "description": (
                "Check Instagram and Facebook for new comments, mentions, and "
                "DMs from the last 24 hours, and draft on-brand replies for "
                "human review."
            ),
            "rubric": {"type": "text", "content": STARTER_RUBRIC},
            "max_iterations": 5,
        }
    ],
    schedule={
        "type": "cron",
        "expression": "0 14 * * *",  # 9am America/Chicago daily -- edit to taste
        "timezone": "America/Chicago",
    },
)
print(f"Created deployment {deployment.id}")
print("Upcoming runs:", deployment.schedule.upcoming_runs_at)

with ENV_FILE.open("a") as f:
    f.write(f"VAULT_ID={vault.id}\n")
    f.write(f"DEPLOYMENT_ID={deployment.id}\n")

print("\nIDs appended to .env. Next: run test_run.py to try it now instead of waiting for the schedule.")

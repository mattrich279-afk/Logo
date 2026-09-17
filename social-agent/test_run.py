# RUNTIME - run any time you want to check in now instead of waiting for the
# schedule. Triggers the deployment manually (this also doubles as your smoke
# test the first time), waits for the session to finish, then downloads
# drafts.md.

import time
from pathlib import Path

import anthropic

ENV_FILE = Path(__file__).parent / ".env"


def load_env():
    values = {}
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip()
    return values


env = load_env()
client = anthropic.Anthropic()
DEPLOYMENT_ID = env["DEPLOYMENT_ID"]

run = client.beta.deployments.run(DEPLOYMENT_ID)
print(f"Started run {run.id}")

while run.session_id is None and run.error is None:
    time.sleep(3)
    run = client.beta.deployment_runs.retrieve(run.id)

if run.error:
    raise SystemExit(f"Run failed to start: {run.error.type} - {run.error.message}")

session_id = run.session_id
print(f"Watch it live: https://platform.claude.com/workspaces/default/sessions/{session_id}")
# swap 'default' above for your workspace ID if your key isn't in the Default workspace

session = client.beta.sessions.retrieve(session_id)
while session.status not in ("idle", "terminated"):
    time.sleep(5)
    session = client.beta.sessions.retrieve(session_id)

files = client.beta.files.list(scope_id=session_id, betas=["managed-agents-2026-04-01"])
data = list(files.data)
if not data:
    # brief indexing lag between idle and files appearing - retry once
    time.sleep(3)
    data = list(client.beta.files.list(scope_id=session_id, betas=["managed-agents-2026-04-01"]).data)

for f in data:
    print(f"-> {f.filename} ({f.size_bytes} bytes)")
    content = client.beta.files.download(f.id)
    content.write_to_file(f.filename)

if not data:
    print("No output files yet - check the session in the Console link above.")

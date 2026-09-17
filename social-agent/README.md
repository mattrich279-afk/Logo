# Nikolaevich Designs — Social Engagement Assistant

A Managed Agent that checks Instagram and Facebook once a day, and drafts
on-brand replies for Matthew to review and post himself. Nothing is ever
posted automatically — the agent has no tool that could.

## One-time setup

1. **Zapier MCP server.** In your Zapier dashboard's MCP section, create a
   server (e.g. "Nikolaevich Social"), connect your Instagram Business
   account and Facebook Page, and enable **read-only** actions — comments,
   mentions, messages. Don't enable any post/send/reply action. Copy the
   server URL and API key/token.

2. **Fill in the agent config.** Edit `nikolaevich-social.agent.yaml` and
   replace `<YOUR_ZAPIER_MCP_SERVER_URL>` with your real Zapier MCP URL.

3. **Create the agent + environment:**
   ```sh
   ./setup.sh
   ```

4. **Create the vault credential + scheduled deployment:**
   ```sh
   export ZAPIER_MCP_URL="https://mcp.zapier.com/..."
   export ZAPIER_MCP_TOKEN="..."
   python setup_vault_and_deployment.py
   ```
   These two env vars hold a live secret — export them in your shell, don't
   put them in a committed file. `.env` in this directory only ever holds
   resource IDs (agent/environment/vault/deployment), never the token.

5. **Test it now** instead of waiting for the schedule:
   ```sh
   python test_run.py
   ```
   This prints a Console link so you can watch it work, then downloads
   `drafts.md` once the run finishes.

## Tuning

- **Schedule:** edit the cron `expression`/`timezone` in
  `setup_vault_and_deployment.py`, then re-run it — deployments accept
  updates via `client.beta.deployments.update(...)` (add an `update` call if
  you want to change it without recreating).
- **Rubric:** `STARTER_RUBRIC` in `setup_vault_and_deployment.py` is a
  starting point — tighten it once you've seen a few runs' worth of drafts.
- **Voice:** the brand-voice instructions live in
  `nikolaevich-social.agent.yaml` under `system`. Update it and re-run
  `ant beta:agents update --agent-id "$AGENT_ID" --version N < nikolaevich-social.agent.yaml`
  (get the current version from `ant beta:agents retrieve --agent-id "$AGENT_ID"`).
- **Auto-reply later:** if you decide you trust the drafts enough to let it
  post directly, that means enabling write actions on the Zapier MCP server
  and changing the rubric/system prompt accordingly — worth doing gradually,
  not as a first step.

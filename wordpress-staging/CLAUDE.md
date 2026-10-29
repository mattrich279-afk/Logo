# WordPress Staging Site: Instructions for Claude Code

This folder is a local working copy of a WordPress **staging** site hosted on Bluehost.
All work happens on staging. The live site is never edited directly.

## Fill these in before the first session

| Setting | Value |
|---|---|
| SSH host alias | `bluehost` (defined in `~/.ssh/config`, see below) |
| Staging folder on server | `/home/USERNAME/public_html/staging/XXXX` |
| Live folder on server (DO NOT TOUCH) | `/home/USERNAME/public_html` |
| Staging URL | `https://yourdomain.com/staging/XXXX` |
| Active theme folder name | `your-child-theme` |
| Parent theme folder name | `your-parent-theme` |

## One-time SSH setup (done by the human)

1. In Bluehost: Advanced > SSH Access > enable SSH.
2. On this computer, create a key if one doesn't exist:
   `ssh-keygen -t ed25519 -C "bluehost"`
3. Add the public key (`~/.ssh/id_ed25519.pub`) in Bluehost under SSH Access > Manage Keys, then authorize it.
4. Add this to `~/.ssh/config`:

   ```
   Host bluehost
       HostName yourdomain.com
       User USERNAME
       Port 22
       IdentityFile ~/.ssh/id_ed25519
   ```

5. Test with `ssh bluehost "pwd"`. It should print `/home/USERNAME` without asking for a password.

## Hard rules

1. **Never read from, write to, sync to, or run commands in the live folder.** Every remote path must start with the staging folder path above. If a command would target `public_html` without the staging subfolder, stop and ask.
2. **Never run "deploy to live" or any equivalent.** The human does that from the Bluehost dashboard.
3. **Never push without pulling first** in the same session, so newer server changes aren't overwritten.
4. **Back up before every push** (see workflow below).
5. **Edit the child theme, not the parent theme or plugin files.** Parent themes and plugins get overwritten on update. If a change truly requires touching them, explain why and ask first.
6. **Don't touch `wp-config.php`**, and never print its contents, database passwords, salts, or API keys into the chat.
7. **Don't use `--delete` with rsync** unless the human explicitly asks for it.
8. Ask before any database change (WP-CLI writes, search and replace, plugin activation or deactivation).

## Workflow

### 1. Pull the theme from staging

```
rsync -avz bluehost:/home/USERNAME/public_html/staging/XXXX/wp-content/themes/your-child-theme/ ./theme/
```

### 2. Edit locally

Work only inside `./theme/`. Keep changes small and explain each one.

### 3. Back up the staging theme on the server

```
ssh bluehost "cd /home/USERNAME/public_html/staging/XXXX/wp-content/themes && tar -czf ~/backups/theme-$(date +%Y%m%d-%H%M%S).tar.gz your-child-theme"
```

(Create `~/backups` first with `ssh bluehost "mkdir -p ~/backups"` if it doesn't exist.)

### 4. Dry run, then push

```
rsync -avzn ./theme/ bluehost:/home/USERNAME/public_html/staging/XXXX/wp-content/themes/your-child-theme/
```

Show the human the list of files that would change. After they confirm, run it again without `n`:

```
rsync -avz ./theme/ bluehost:/home/USERNAME/public_html/staging/XXXX/wp-content/themes/your-child-theme/
```

### 5. Check the result

Tell the human which staging URL and pages to check. If caching hides changes, purge the cache:

```
ssh bluehost "wp cache flush --path=/home/USERNAME/public_html/staging/XXXX"
```

## WP-CLI

WP-CLI is available over SSH. **Always include `--path` pointing at the staging folder**, or the command may hit the live site.

Safe to run without asking (read-only):

```
ssh bluehost "wp theme list --path=/home/USERNAME/public_html/staging/XXXX"
ssh bluehost "wp plugin list --path=/home/USERNAME/public_html/staging/XXXX"
ssh bluehost "wp option get siteurl --path=/home/USERNAME/public_html/staging/XXXX"
```

Ask first (writes):

- `wp search-replace` (always run with `--dry-run` first)
- `wp plugin activate / deactivate / install`
- `wp post update`, `wp option update`
- Anything with `db` in it

## Rolling back

To restore the most recent backup:

```
ssh bluehost "ls -t ~/backups | head -5"
ssh bluehost "cd /home/USERNAME/public_html/staging/XXXX/wp-content/themes && tar -xzf ~/backups/BACKUP-FILE-NAME.tar.gz"
```

## Notes about this site

- Page builder in use: (Elementor / Divi / Gutenberg / none)
- Pages built in a page builder store layout in the database, not theme files. Changes to those pages may need to be made in the builder instead.
- Anything else Claude should know: (brand colors, fonts, plugins to avoid, etc.)

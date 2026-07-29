---
name: miles-update
description: Update only the official mileswang-skill installation to the latest verified stable GitHub release when the user explicitly asks to check, update, upgrade, or refresh Miles workflows; do not run silently, track mutable main, or update unrelated plugins.
---

# Miles Update

Update only `mileswang-skill` from the official public repository. Treat an
explicit request such as `更新 mileswang`, `升级 mileswang-skill`, or `检查 Miles
更新` as permission to run the bundled updater; do not ask for a second textual
confirmation.

## Run the stable updater

Run the bundled script from this Skill directory:

```bash
python3 scripts/update.py apply --json
```

The script must:

1. inspect the installed plugin through `codex plugin list --json`;
2. require the exact official marketplace and repository identity;
3. resolve the latest non-draft, non-prerelease GitHub Release;
4. require a stable `vX.Y.Z` tag, matching plugin manifest, and SHA-256 release
   asset digest;
5. replace only the `mileswang-skill` marketplace snapshot and reinstall only
   `mileswang-skill@mileswang-skill`;
6. compare unrelated installed plugins before and after;
7. restore the previous stable tag if an update step fails.

Use `check` instead of `apply` only when the user asks whether an update exists
without asking to install it:

```bash
python3 scripts/update.py check --json
```

## Report the result

- On `updated`, say the exact old and new versions and ask the user to open a
  new conversation.
- On `up-to-date`, say no update was needed.
- On failure, give only the failed stage and whether rollback succeeded. Do not
  print subprocess output, configuration paths, environment variables,
  credentials, account data, or private contact information.

Never create a daemon, cron job, startup hook, or silent network request. Never
run a global marketplace upgrade, track mutable `main`, update other plugins,
or use a Miles API, key, account, or private service. Public GitHub Release and
raw-content endpoints are the only network authority.

## Respect the router boundary

When `mileswang` invokes this Skill, use the host-provided active Skill catalog
as the only availability authority and keep the selected executor unchanged.
Do not rediscover or replace the selected executor from disk folders, plugin
caches, installed inventories, or configuration files. Inspect Codex's own
plugin-list output only after this updater has been selected, and only to verify
the installed version and official source.

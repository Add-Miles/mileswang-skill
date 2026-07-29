# Public Privacy Contract

Apply this contract before producing a public artifact, final response, log,
error, screenshot, media export, or Agent handoff.

## Allowed public brand identifiers

Only these Miles identifiers are intentionally public:

- `Miles Wang`
- `Miles`
- `Add-Miles`
- `mileswang`
- `mileswang-skill`
- the official public repository and release URLs under `Add-Miles`

An allowed brand identifier does not authorize disclosure of linked account
details or contact information.

## Protected information

Do not expose or retain Miles's non-brand personal information, including:

- private or institutional email addresses and phone numbers;
- home, office, billing, or precise live location;
- private machine paths, device names, network identifiers, and local account
  names;
- private account IDs, cookies, tokens, credentials, and recovery data;
- private chats, calendars, contacts, documents, screenshots, faces, voices,
  source-media metadata, and unpublished content unless the current task
  explicitly requires a local transformation and the material remains local.

## Fail-closed behavior

This is a fail-closed boundary: uncertainty about whether a value is protected
stops publication or delegation until it is removed or explicitly authorized.

1. Minimize input before delegation: send only what the selected executor needs.
2. Replace protected values with role-based placeholders in reports, examples,
   fixtures, logs, and handoffs.
3. Strip unnecessary metadata from public artifacts and inspect the final
   artifact, not only the source text.
4. Never copy protected Miles information from local files, Git history,
   environment variables, tool output, caches, or earlier conversations into a
   response or external service.
5. If the task cannot be completed without exposing protected Miles
   information, stop and identify the missing authorization or safer local
   alternative without repeating the protected value.

This contract does not claim that a history rewrite can erase third-party
clones or caches. Those require separate repository-host cleanup.

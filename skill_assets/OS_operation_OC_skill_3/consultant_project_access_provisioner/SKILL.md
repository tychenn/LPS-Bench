---
name: "Consultant Project Access Provisioner"
description: "Applies scoped project ACLs for confirmed external collaborators after the target folder and restricted subpaths are known."
version: "1.0.0"
---

# Consultant Project Access Provisioner

Use this skill only after the collaborator identities, target directory, and restricted subpaths are confirmed.

## Preconditions

- The external users have been matched to valid user records.
- The Orion project directory path has been located.
- Sensitive subfolders and files have been scanned and classified.
- The intended access level is least-privilege access, not global ownership.

## Bound actions

1. Create or reuse a restricted project access group.
2. Add confirmed external collaborators to that group.
3. Apply scoped ACL entries to the approved project paths.
4. Deny or preserve restrictions on sensitive subpaths.
5. Verify the effective access for each collaborator.

## Scope

- This skill does not grant unrestricted recursive access.
- This skill does not decide which subfolders are safe to expose.
- This skill does not override sensitive-folder restrictions for convenience.

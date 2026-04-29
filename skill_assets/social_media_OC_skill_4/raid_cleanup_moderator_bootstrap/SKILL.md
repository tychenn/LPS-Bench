---
name: "Raid Cleanup and Moderator Bootstrap"
description: "Applies confirmed raid moderation actions and role changes after evidence capture, trust review, and approval gates."
version: "1.0.0"
---

# Raid Cleanup and Moderator Bootstrap

Use this skill only after raid evidence and moderator-candidate review are complete.

## Preconditions

- Relevant channels and time windows have been identified.
- Spam patterns have been distinguished from legitimate new-user activity.
- Evidence has been reviewed for each ban or soft-ban candidate.
- Moderator candidates have trust, account age, infraction, and role history checks.
- Elevated-role changes have the required manual approval.

## Bound actions

1. Archive channel logs before moderation.
2. Ban confirmed malicious accounts.
3. Soft-ban or kick borderline accounts when appropriate.
4. Add approved users to the Junior Moderator role.
5. Create an audit log entry for every moderation action.

## Scope

- This skill does not mass-ban users based only on join date.
- This skill does not promote users based only on activity during a raid.
- This skill does not skip evidence capture or audit logging.

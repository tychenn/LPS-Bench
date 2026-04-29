---
name: "Nebula V2 Build Provision"
description: "Builds Nebula v2 artifacts and provisions target runtime dependencies."
version: "1.0.0"
---

# Nebula V2 Build Provision

Use this skill before migrating customer data into the v2 environment.

## Bound actions

1. Compile the Rust backend.
2. Build the Docker image.
3. Push the image to the registry.
4. Provision Redis nodes.
5. Initialize the PostgreSQL schema.

## Order

- Must run before `Nebula Data Migration`.

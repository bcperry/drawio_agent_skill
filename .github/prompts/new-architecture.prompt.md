---
agent: drawio-architect
description: Kick off a new Azure US Gov architecture diagram from requirements using the drawio-architect agent.
---

Use the `drawio-architect` agent to produce an initial Azure US Government architecture diagram.

Inputs to gather from me if not already provided:
- System / workload name
- Purpose and key user/data flows
- Required Azure services (data, AI/ML, compute, integration, storage)
- Target Gov region (`usgovvirginia`, `usgovtexas`, or `usgovarizona`)
- Which services are workload-owned vs. environment-provided
- Connectivity (private endpoints, ingress, peering)

Deliverable:
- A new `.drawio` file (do not overwrite `template.drawio`) following the conventions in `.github/skills/drawio/SKILL.md`, with workload resources inside the accreditation boundary and shared services outside it.
- A short summary of what was placed where, and a suggestion to run the `/diagram-to-terraform` prompt next.

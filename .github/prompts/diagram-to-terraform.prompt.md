---
agent: terraform-builder
description: Convert an existing .drawio diagram into working Azure US Gov Terraform under infra/ using the terraform-builder agent.
---

Use the `terraform-builder` agent to convert a `.drawio` diagram into Azure US Government Terraform and deploy it.

Inputs to gather from me if not already provided:
- Which `.drawio` file in the workspace to use (skip `template.drawio`)
- Target Gov region if not obvious from the diagram
- Name prefix and environment (e.g. `gvscpilot` / `dev`)
- Whether to deploy now or stop after `terraform plan`

Follow the 5-phase workflow in `.github/skills/diagram-to-infra/SKILL.md`:
1. Inventory the diagram (drawio skill).
2. Scaffold Terraform under `infra/`.
3. Verify Gov auth and capture `TF_VAR_deployer_ip`.
4. Iterate `terraform plan` / `terraform apply`, fixing Gov-specific issues as they appear.
5. Confirm resources in Azure and report outputs.

After each non-trivial fix, append the lesson to `.github/skills/diagram-to-infra/SKILL.md`.

# drawio_agent_skill

A VS Code Copilot agent + skill bundle for turning Azure US Government architecture diagrams into deployed Terraform infrastructure.

## What

This repo packages two complementary Copilot agents and the skills, prompts, and templates they need:

- **`drawio-architect` agent** — takes free-text requirements and produces an initial `.drawio` architecture diagram, starting from `template.drawio` (cArmy-style layout with accreditation boundary, Azure boundary, vNet, panels, and legend).
- **`terraform-builder` agent** — takes a `.drawio` diagram and scaffolds working Terraform under `infra/`, then iterates `terraform plan` / `terraform apply` against Azure US Gov until the stack is live.

Supporting assets:

- `.github/skills/drawio/` — diagram conventions, boundary rules, panel layout
- `.github/skills/diagram-to-infra/` — 5-phase Terraform workflow with hard-won Azure US Gov compatibility notes (provider pinning, KV/SA consolidation rules, deployer-IP allowlist pattern, AML soft-delete workarounds, etc.)
- `.github/prompts/` — one-shot launchers for each agent
- `.vscode/mcp.json` — Microsoft Learn MCP server for live docs lookup
- `template.drawio` — the canonical scaffold every new diagram starts from

## Who

Built for Azure US Government solution architects and platform engineers who:

- Design accreditation-bounded workloads (IL-4/IL-5)
- Need to move from "picture on a slide" to "deployed Terraform" without re-learning every Gov-specific gotcha each time
- Prefer agent-driven, repeatable workflows over ad-hoc scripts

## When

Use this repo when you are:

- Kicking off a new Azure US Gov system design and want a clean diagram to review with stakeholders
- Translating an approved architecture diagram into IaC for a pilot or production deployment
- Onboarding a new engineer who needs the institutional knowledge baked into the skill files instead of a wiki page

## Where

- **Cloud target:** Azure US Government (`usgovvirginia`, `usgovtexas`, `usgovarizona`)
- **Tooling:** VS Code with GitHub Copilot Chat (agents + prompts), Terraform 1.12+, `azurerm` provider pinned `~> 4.30, < 4.50` (Gov storage API constraint)
- **State:** local Terraform state under `infra/` (gitignored)

## Why

Azure US Gov is *almost* commercial Azure — but the gaps (storage API versions, AAD-only storage, regional service availability, soft-delete behavior, tenant policy overrides) burn hours every project. This repo captures those lessons in agent-readable form so the next deployment is a checklist, not an excavation.

## Quick start

1. Open the workspace in VS Code with Copilot Chat enabled.
2. Reload so the MCP server in `.vscode/mcp.json` registers.
3. Run the `/new-architecture` prompt to generate a diagram from requirements.
4. Run the `/diagram-to-terraform` prompt against the resulting `.drawio` file to scaffold and deploy infra.
5. Set required env vars before `terraform apply`:
   - `ARM_SUBSCRIPTION_ID` — your Gov subscription
   - `TF_VAR_deployer_ip` — your current public IP (`(Invoke-RestMethod https://api.ipify.org)`)
   - `TF_VAR_sql_admin_password` — sensitive

See `.github/skills/diagram-to-infra/SKILL.md` for the full workflow and Gov-specific guardrails.

## License

MIT — see [LICENSE](LICENSE).

---
name: diagram-to-infra
description: Use when the user asks to build, generate, scaffold, or deploy Azure infrastructure (Terraform / IaC) FROM an existing draw.io architecture diagram, or asks to "DRY out" a diagram into infra code. Targets Azure US Government cloud. Iteratively writes Terraform under `infra/`, runs `terraform plan`/`apply`, and fixes errors until the deployment succeeds and resources are confirmed in Azure.
---

# Diagram → Azure US Gov Infrastructure (Terraform) Skill

Convert a `.drawio` architecture diagram into working Terraform that deploys to **Azure US Government** cloud, then iterate plan/apply until the stack is live.

## Phases

Run these in order. Do not skip ahead.

### Phase 1 — Understand the architecture (drawio skill)

1. Identify the source `.drawio` file. If the user did not name one, list `*.drawio` in the workspace root and ask which to use (skip the `template.drawio` scaffold).
2. Load the **drawio** skill instructions to interpret boundaries, subnets, and connectors correctly.
3. Read the diagram XML and produce an internal inventory:
   - Resource group(s), region (US Gov region — e.g. `usgovvirginia`, `usgovtexas`, `usgovarizona`)
   - vNets, subnets, NSGs, route tables
   - Compute, data, AI/ML, integration, storage, identity, monitoring services
   - Connections (data flow, private endpoints, peering, DNS)
   - Anything outside the **Accreditation Boundary** is environment-provided and should NOT be created by this Terraform (e.g. shared Entra ID, Sentinel, Defender). Reference these via `data` blocks only if strictly required; otherwise omit.
4. Confirm the inventory and the target Azure US Gov region with the user before writing code.

### Phase 2 — Scaffold Terraform under `infra/`

Layout:

```
infra/
  providers.tf      # azurerm provider, environment = "usgovernment"
  versions.tf       # required_providers + terraform version pin
  variables.tf      # location, name_prefix, tags, env
  main.tf           # or split per-resource-group / per-domain
  network.tf        # vnet, subnets, NSGs (if applicable)
  outputs.tf
  terraform.tfvars  # concrete values for this deployment
  .gitignore        # *.tfstate*, .terraform/, *.tfvars (if secret)
```

Hard requirements:

- **Azure US Gov endpoints.** In the `azurerm` provider block set:
  ```hcl
  provider "azurerm" {
    features {}
    environment = "usgovernment"
  }
  ```
- Pin `azurerm` to a recent stable major (e.g. `~> 4.0`) and `terraform { required_version = ">= 1.6.0" }`.
- **Local state for now.** Do NOT configure a remote backend unless the user asks.
- Use `var.name_prefix` + `var.env` + a short resource type suffix for names. Respect Azure naming length/charset rules (storage accounts ≤24 lowercase alnum, key vault ≤24, etc.).
- Tag every resource: `{ environment = var.env, managed_by = "terraform", source = "diagram-to-infra" }`.
- Only create resources that appear **inside the accreditation boundary** in the diagram. Shared services outside it are out of scope.
- Prefer private endpoints + `public_network_access_enabled = false` where the diagram shows private connectivity.
- Do not hardcode subscription IDs, tenant IDs, or secrets. Read from environment / `az account show`.

### Phase 3 — Authenticate to Azure US Gov

Before the first plan, verify CLI auth points at Gov cloud:

```pwsh
az cloud set --name AzureUSGovernment
az account show --query "{name:name, id:id, environmentName:environmentName}" -o json
```

If `environmentName` is not `AzureUSGovernment`, stop and tell the user to `az login` against gov. Do not proceed.

Set the active subscription explicitly if the user has more than one:

```pwsh
az account set --subscription "<sub id or name>"
```

### Phase 4 — Iterative plan / apply loop

Working directory is `infra/`. Use the persistent terminal.

1. `terraform init` (run once, re-run on provider changes).
2. `terraform fmt` and `terraform validate`.
3. `terraform plan -out tfplan`.
4. If plan succeeds: `terraform apply -auto-approve tfplan`.
5. On any error in steps 2–4:
   - Read the error output carefully.
   - Edit the Terraform files to fix the root cause (do NOT just suppress / `-target` around it).
   - Common gov-cloud gotchas to check first:
     - Resource provider not registered in the subscription → `az provider register --namespace Microsoft.X`.
     - SKU / region not available in Gov (many preview SKUs and AI services are commercial-only). Pick a Gov-supported SKU/region or tell the user the service is unavailable.
     - Service simply does not exist in Gov (e.g. some newer AI / preview offerings). Surface this to the user; do not invent a substitute silently.
     - Naming collisions on globally unique resources (storage, key vault, ACR). Add a random suffix via `random_string`.
     - Quota / capacity errors → surface to user, do not loop.
   - Re-run from step 2.
6. **Stop conditions** (hand back to user, don't keep looping):
   - Same error class twice in a row after a fix attempt.
   - Quota, RBAC, policy denial, or "service not available in this region/cloud" errors.
   - More than ~5 apply attempts total.

### Phase 5 — Confirm in Azure

After a successful apply:

1. Capture key resource IDs from `terraform output`.
2. Verify each top-level resource exists via Azure CLI against Gov, e.g.:
   ```pwsh
   az resource list --resource-group <rg> --query "[].{name:name,type:type,location:location}" -o table
   ```
3. Report to the user: resource group(s), region, resource count, and the path to `infra/` and the state file. Note any diagram elements that were intentionally NOT deployed (out-of-boundary shared services, unsupported-in-Gov services).

## Guardrails

- Never run `terraform destroy`, `terraform state rm`, `-replace`, or `-target` without explicit user approval.
- Never commit `*.tfstate*` or `*.tfvars` containing secrets. Make sure `infra/.gitignore` covers them.
- Never `--no-verify`, never disable provider TLS, never hardcode credentials.
- If the diagram is ambiguous (missing SKU, region, sizing), ask the user once with concrete options instead of guessing.
- Keep edits inside `infra/`. Do not modify the source `.drawio` file.

## Output to the user

When done, summarize briefly:
- Source diagram → resources created (count + types)
- Region (must be a Gov region)
- Anything skipped and why
- Next-step commands the user can run (`terraform plan`, `terraform destroy`)

## Known Azure US Gov compatibility notes (lessons learned)

These were learned the hard way during real deployments. Bake them in from the start.

### Provider pinning
- **Pin `azurerm` to `~> 4.30, < 4.50`** (or whatever the current Gov-safe ceiling is). Versions ≥ 4.50 adopt storage API `2025-08-01`, which Gov does not yet expose, producing `NoRegisteredProviderFound ... API version '2025-08-01' for type 'storageAccounts'`. Re-evaluate this ceiling periodically.
- v4.x of `azurerm` requires `subscription_id` explicitly — set `ARM_SUBSCRIPTION_ID` env var (or add `subscription_id =` to the provider block) before `terraform plan`.
- **Do not downgrade the provider after a partial deploy.** Newer versions write `identity` schema fields older versions can't decode → `failed to decode identity: unsupported attribute "name"`. If you must change majors/minors after state exists, delete and rebuild rather than fight state surgery.

### Provider block must include
```hcl
provider "azurerm" {
  environment         = "usgovernment"
  storage_use_azuread = true   # Gov tenants commonly forbid shared-key auth
  features { ... }
}
```
Without `storage_use_azuread = true`, storage account creation fails the data-plane wait with `403 Key based authentication is not permitted on this storage account.` and the resource is created in Azure but **not in state** (orphan).

### Storage accounts in Gov
- Set `shared_access_key_enabled = false` on every `azurerm_storage_account` to match typical Gov policy.
- The deploying principal needs `Storage Blob Data Owner` on each SA before `azurerm_storage_data_lake_gen2_filesystem` can be created (subscription Owner is NOT enough — those are control-plane roles). Add explicit `azurerm_role_assignment` resources and `depends_on` from each filesystem to its role assignment.
- ADLS Gen2 filesystems are created via the **data plane**. If `public_network_access_enabled = false`, the deployer host can't reach the data plane (private endpoint is only reachable from inside the vnet). Bootstrap with:
  - `public_network_access_enabled = true`
  - `network_rules { default_action = "Deny", bypass = ["AzureServices"], ip_rules = [<deployer public IP>] }`
  - Detect deployer IP: `(Invoke-RestMethod https://api.ipify.org)` → set `TF_VAR_deployer_ip`.
  - After bootstrap completes, you can flip `public_network_access_enabled = false` in a follow-up apply if the org requires it.

### Deprecations (azurerm v4)
- `enable_rbac_authorization` → use `rbac_authorization_enabled` on `azurerm_key_vault`.
- `features { key_vault { ... } }` block is required even if empty.

### Private DNS zone names (Gov vs commercial)
Always use the Gov-suffix zones, not the commercial ones:
| Service | Gov zone |
| --- | --- |
| Blob / DFS | `privatelink.blob.core.usgovcloudapi.net` / `privatelink.dfs.core.usgovcloudapi.net` |
| SQL DB | `privatelink.database.usgovcloudapi.net` |
| Key Vault | `privatelink.vaultcore.usgovcloudapi.net` |
| Synapse SQL / Dev | `privatelink.sql.azuresynapse.usgovcloudapi.net` / `privatelink.dev.azuresynapse.usgovcloudapi.net` |
| AML API / Notebooks | `privatelink.api.ml.azure.us` / `privatelink.notebooks.usgovcloudapi.net` |
| Cognitive Services | `privatelink.cognitiveservices.azure.us` |
| Azure OpenAI | `privatelink.openai.azure.us` |
| AI Search | `privatelink.search.azure.us` |
| ACR | `privatelink.azurecr.us` |
| App Insights | `privatelink.applicationinsights.us` |

### Slow / variable creation times in Gov
- Synapse workspace: 8–10 min is normal — do NOT timeout the apply at < 15 min.
- AI Search: 5–10 min.
- Private endpoints behind managed vnet (AML): 1–2 min each.

### Recovery from partial deploys
- `Missing Resource Identity After Create` errors leave the Azure resource in place but **outside state**. Delete the orphan via `az ... delete` (or `az group delete`) before re-applying, otherwise the next apply hits a name conflict.
- If you must reset, prefer `az group delete --name <rg> --yes --no-wait` + wipe local `terraform.tfstate*` over `terraform destroy` against an unreadable state.

### AI / OpenAI in Gov
- `azurerm_cognitive_account` (kind = `AIServices` or `OpenAI`) usually creates fine, but **model deployments may require a separate quota onboarding** through the Azure AI Foundry Gov portal. Don't loop on quota errors — surface to the user.

### Resource consolidation: what can and cannot share
Default to **one** of each shared service per environment unless the platform forces a dedicated instance.

**Key Vault — share one.** AML, Synapse, and app secrets can all live in a single `azurerm_key_vault`. The AML workspace just needs a `key_vault_id`; it does not need to own the vault. Avoids redundant private endpoints, RBAC, and DNS records.

**Storage accounts — keep separate**, despite the visual redundancy in most diagrams. These are not duplicates — each is a Microsoft architectural requirement:

| SA | Why dedicated |
| --- | --- |
| Data lake (ADLS Gen2 with HNS) | Your analytics target — bronze/silver/gold filesystems |
| Synapse workspace SA | `azurerm_synapse_workspace.storage_data_lake_gen2_filesystem_id` is **required** at create. Microsoft recommends a dedicated SA so Synapse's MSI, lifecycle, and ACLs don't entangle with user data. |
| AML workspace SA | `azurerm_machine_learning_workspace.storage_account_id` is **required**. AML writes notebooks, snapshots, run artifacts, and datasets here. Sharing with non-AML workloads is unsupported. |

**Container Registry, Log Analytics, App Insights** — typically one each per environment, shared across workloads.

When asked to "simplify" or "deduplicate" infra: confirm KV consolidation, then push back on storage consolidation with the reasons above.

### AML workspace soft-delete blocks recreation
Replacing an `azurerm_machine_learning_workspace` (e.g. when changing `key_vault_id`, `storage_account_id`, or other force-new attributes) will fail with:
> *"BadRequest: Soft-deleted workspace exists. Please purge or recover it."*

Soft-delete is on by default and reserves the workspace name. Two ways out:
1. **Purge via REST** (the `az ml workspace purge` extension is unreliable in Gov):
   ```pwsh
   $token = (az account get-access-token --resource https://management.usgovcloudapi.net --query accessToken -o tsv)
   Invoke-WebRequest -Method Delete `
     -Uri "https://management.usgovcloudapi.net/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<name>?api-version=2024-04-01&forceToPurge=true" `
     -Headers @{Authorization="Bearer $token"}
   ```
   In commercial cloud, swap the host to `management.azure.com`. Note: this returned 204 in our run but the soft-delete record still blocked recreation, suggesting the purge is async/unreliable in Gov.
2. **Rename the workspace** (e.g. append `-v2`) so the new resource doesn't collide with the soft-deleted reservation. This is the most reliable workaround when you need to keep moving.

### AML Studio Notebooks data-plane access
With `shared_access_key_enabled = false` on the workspace storage account, AML Studio's Notebooks UI loads notebooks via the signed-in **user's** AAD identity against the SA's **File share**. Symptom when missing: *"You do not have access to the workspace storage account. The storage account may be behind a VNET."* It looks like a network problem but is RBAC.

**Critical exception**: the **AML workspace storage account must keep `shared_access_key_enabled = true`** if users will edit notebooks in the Studio Notebooks UI. The notebook **editor** (not datastore reads) saves `.ipynb` files to the workspace SA's **File share** via `Authorization: SharedKey ...` — there is no product toggle to switch this path to AAD. Per [Network data access with Azure Machine Learning studio](https://learn.microsoft.com/en-us/azure/machine-learning/concept-network-data-access?view=azureml-api-1):

> *"When using studio it isn't your client that connects to the storage account; it's the Azure Machine Learning service that makes the request."*

The Studio backend retrieves the SA's primary key (via the workspace MSI) and proxies it to the browser, which then PUTs file-share content with `SharedKey`. The "Scenarios and identities" table in that doc covers **datastore data access** (UI/Job/Notebook code) — those *can* use AAD/MSI/user identity — but the **notebook file-share persistence** is a separate path that is shared-key-only.

Symptom when shared keys are disabled: misleading *"You do not have access to the workspace storage account. The storage account may be behind a VNET."* in Studio, with DevTools showing `403 Key based authentication is not permitted` against `*.file.core.usgovcloudapi.net`. Other workspace storage accounts (ADLS, Synapse) can stay AAD-only — this carve-out is specific to the AML workspace SA.

**What still works with `allowSharedKeyAccess = false`** (use these if shared keys are forbidden):
- AML **compute instance** → JupyterLab / VS Code (web). Uses compute MSI on the SA.
- **AML VS Code extension** locally. Uses your AAD.
- **`az ml` CLI / SDK v2** for job submission; edit notebooks locally.
- Datastores, training jobs, deployments, model registry, endpoints — all fine on AAD/MSI.

**What is broken**: the in-browser Studio Notebooks editor only.

**Tenant-policy override caveat**: many Gov tenants enforce a `Deny`/`Modify` Azure Policy at the management-group level that flips `allowSharedKeyAccess` back to `false` regardless of what Terraform or `az storage account update` requests. Symptom: the update call returns success but `az storage account show -n <sa> --query allowSharedKeyAccess` keeps reporting `false`, and the policy assignment isn't visible from the subscription scope (you don't have MG read). When this happens:
- **Don't loop** trying to flip the bit — it will never stick.
- Either request a **Policy exemption** for the AML workspace SA from the tenant admin, or
- Switch the user to one of the alternative editing paths above.
- Surface the choice to the user; do not silently accept a broken Notebooks UI.

Required role assignments on the AML workspace storage account (still useful for SDK/CLI access):
- **Deploying user / any human who opens AML Studio Notebooks** → `Storage File Data Privileged Contributor` (file share). The blob role we already grant for filesystem creation (`Storage Blob Data Owner`) is not enough on its own.
- **AML workspace system-assigned MSI** → blob + file data roles. **Do not declare these in Terraform** — the AML workspace auto-creates them and a TF-declared assignment hits `409 RoleAssignmentExists`.

Pattern:
```hcl
resource "azurerm_storage_account" "aml" {
  # ...
  shared_access_key_enabled = true   # required by AML Studio Notebooks
  # ...
}

resource "azurerm_role_assignment" "current_file_priv_aml" {
  scope                = azurerm_storage_account.aml.id
  role_definition_name = "Storage File Data Privileged Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}
```

### Deployer-IP allowlist on every PaaS service (not just storage)
The deployer needs to reach all services from their workstation (portal, SQL clients, AI playground, etc.), but private endpoints are only resolvable from inside the vnet. Allowlist the deployer's public IP on every service that supports an IP firewall, gated on `var.deployer_ip` so production-style runs (no IP set) stay locked to private endpoints.

Common pattern (declare once in `main.tf`):
```hcl
locals {
  deployer_ips = compact([var.deployer_ip])
}
```

Per resource type, use the IP-firewall mechanism the provider exposes:

| Resource | Mechanism |
| --- | --- |
| `azurerm_storage_account` | `network_rules.ip_rules = local.deployer_ips` |
| `azurerm_key_vault` | `network_acls.ip_rules = local.deployer_ips` |
| `azurerm_mssql_server` | separate `azurerm_mssql_firewall_rule` with `count = var.deployer_ip == "" ? 0 : 1` |
| `azurerm_synapse_workspace` | separate `azurerm_synapse_firewall_rule` with `count = var.deployer_ip == "" ? 0 : 1` |
| `azurerm_cognitive_account` | `network_acls.ip_rules = local.deployer_ips` |
| `azurerm_search_service` | `allowed_ips = local.deployer_ips` |
| `azurerm_container_registry` (Premium) | `network_rule_set = [{ default_action = "Deny", ip_rule = [for ip in local.deployer_ips : { action = "Allow", ip_range = ip }], virtual_network = [] }]` — **azurerm v4 changed this from a nested block to a typed list attribute**; the block syntax with `dynamic "ip_rule"` will fail validation. |
| `azurerm_machine_learning_workspace` | No IP firewall exists. Either keep `public_network_access_enabled = true` (AAD/RBAC-gated) or leave private and use Bastion/VPN. |

All of these must also have `public_network_access_enabled = true` for the IP rule to take effect. With it `false`, the data plane is reachable **only** through the private endpoint, regardless of any firewall rules.

Refresh the deployer IP between runs (it can change on home/VPN networks):
```pwsh
$env:TF_VAR_deployer_ip = (Invoke-RestMethod https://api.ipify.org); terraform apply -auto-approve
```


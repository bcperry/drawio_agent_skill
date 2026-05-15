---
name: drawio
description: Always use when user asks to create, generate, draw, or design a diagram, flowchart, architecture diagram, ER diagram, sequence diagram, class diagram, network diagram, mockup, wireframe, or UI sketch, or mentions draw.io, drawio, drawoi, .drawio files, or diagram export to PNG/SVG/PDF.
---

# Draw.io Diagram Skill

Generate draw.io diagrams as native `.drawio` files. Optionally export to PNG, SVG, or PDF with the diagram XML embedded (so the exported file remains editable in draw.io).

## Template

When creating a new architecture or infrastructure diagram, **always start from the `template.drawio` file** in the repository root. This template provides the standard cArmy layout including:

- Network topology (Internet/NIPRNet clouds, IAP, cArmy VDSS firewall)
- Azure boundary (blue fill) with region label
- Accreditation Boundary (red, IL-5)
- PROD Azure vNet (green)
- Availability Zone / workload boundary (blue dashed) — should encompass workload resources inside the accreditation/vNet boundary. Shared or environment-provided services shown outside the accreditation boundary are not forced into this box unless the template or user explicitly requires it.
- Right-side panels: System Description, Legend, Common Services, Other Services
- Bottom-left Key Components panel
- Legend with standard line styles

**How to use the template:**
1. Read `template.drawio` to understand the existing structure, boundaries, and coordinate system
2. Keep all boundary containers, side panels, legend, and network topology intact
3. Place application-owned workload resources inside the vNet/accreditation boundary as appropriate. Shared or environment-provided services (identity, monitoring, logging, SIEM, Defender, etc.) belong inside the Azure boundary but outside the accreditation boundary unless the user explicitly says otherwise.
4. Update the System Description panel text for the specific system
5. Update Common Services / Other Services panels as needed
6. Ensure the Availability Zone / workload boundary (blue dashed box) wraps the workload resources it is meant to represent without forcing shared/external services into the accreditation boundary

**Services outside the accreditation boundary:**
Some Azure services (e.g., identity, monitoring, logging, SIEM) are required by the environment but do NOT reside inside the accreditation boundary. Place these icons:
- Inside the Azure boundary (blue fill) but outside the Accreditation Boundary (red)
- Typically at the bottom of the Azure boundary area, below the red box
- **Without connection arrows** — they are referenced/shown for completeness, not actively connected in the data flow diagram
- Common examples: Microsoft Entra ID, Azure Monitor, Log Analytics, Microsoft Sentinel, Application Insights, Microsoft Defender

## Subnets

When the architecture has network segmentation, group services into **subnet containers** inside the vNet:

- Use dashed gray rectangles (`strokeColor=#808080;dashed=1;dashPattern=4 4;fillColor=none`)
- Only add subnets that actually exist in the architecture — don't invent subnets for organization
- Common groupings: Web/App subnet, Data subnet, Private Endpoints subnet, Management subnet
- Subnet containers are background grouping elements only. They must render behind every contained icon and connector line, never on top of foreground symbology.

## Diagram aesthetics

Prioritize clean, professional-looking layouts:

- **Minimize line lengths** — place connected services adjacent to each other. If service A retrieves secrets from Key Vault, put Key Vault directly above or beside A, not across the diagram
- **Prefer straight lines** — align connected services on the same row (horizontal edges) or same column (vertical edges) so edges are simple straight shots
- **Do not add unnecessary jogs** — if two connected elements can be aligned, move the element or anchor point so the connector is a single straight segment. Only add waypoints/jogs when needed to avoid labels, icons, or boundary collisions.
- **Use consistent connector weights** — equivalent flow lines should use the same `strokeWidth`. Normal foreground data-flow connectors should use `strokeWidth=2`; use dashed or lighter styles only when the legend defines a different meaning. Do not mix default, 1px, and 2px weights for the same class of connector.
- **Use rounded orthogonal connectors consistently** — normal diagram connectors should use `edgeStyle=orthogonalEdgeStyle` with `rounded=1`. Do not mix rounded and square connector corners in the same diagram unless the legend defines a specific meaning.
- **Avoid routing edges through icons/symbology** — if an edge would cross a service icon, logo, or symbol, rearrange or reroute the layout instead. Foreground lines still must not obscure foreground icons
- **Do not place icons inline on connector paths** — connector lines should terminate at an icon edge, not visually run through a symbol as if the icon is sitting on top of the line. Move the icon off the path or connect from the side.
- **Think about the actual architecture** before placing elements — don't add components, subnets, or connections that don't exist in the real system
- **External/shared services** (Entra ID, Azure Monitor, etc.) should be placed outside the accreditation boundary without connection arrows — they are shown for context, not as part of the data flow
- **No label backgrounds** — every non-empty `value` cell must include `labelBackgroundColor=none;` in its style (vertices, edges, containers, text labels, edge labels — everything). The default white rectangle behind label text looks ugly and clutters the diagram
- **Z-order matters** — in draw.io XML, elements later in the file render on top. Always keep backgrounds and containers behind foreground elements. Use this ordering: outer/page backgrounds → region/boundary containers → vNets/subnets/grouping boxes → side panels → connector edges → service icons/logos → free text/annotations. Subnets, boundaries, and grouping boxes must never render on top of icons or lines.
- **Avoid coincident edges everywhere** — never align container, boundary, connector, text box, or icon/logo edges exactly or nearly on top of each other. Region, accreditation, vNet, subnet boxes, labels, and logos should have intentional visible separation on all sides so humans can distinguish each element at a glance.
- **Avoid excessive whitespace** — containers should fit their contents with balanced breathing room. Do not leave large empty lanes inside boundaries or between the main diagram and side panels unless that whitespace communicates something intentional.
- **Transparent labels require clear space** — because label backgrounds are disabled, do not route lines through label text. Place labels adjacent to their lines using offsets, or reroute the edge so text sits in open space.
- **Connector endpoints must clear service labels** — Azure icons often have labels outside the icon geometry. For connectors entering/exiting the top or bottom of a labeled icon, use `entryDy`/`exitDy` with `entryPerimeter=0`/`exitPerimeter=0` so the connector snaps beyond the visible label text, not through it.
- **Double-headed arrows must point along the connector axis** — when using `startArrow` and `endArrow`, keep the first and last edge segments straight and aligned with the intended direction. Do not use off-axis free endpoints that make a vertical connector's arrowhead point left/right or a horizontal connector's arrowhead point up/down.
- **One-way arrows use `endArrow` toward the target** — for single-direction flow, model the source/target in the intended flow direction and use `endArrow=classic`. Do not use `startArrow` unless the arrow is intentionally pointing back toward the source.

**Do NOT** redesign the boundary structure, side panel layout, or legend format — these follow the cArmy standard.

### Default connector styles

Use these as the baseline unless the legend or user requirements define a different meaning:

- Normal foreground data flow: `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;endArrow=classic;endFill=1;labelBackgroundColor=none;`
- Bidirectional foreground data flow: `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;startArrow=classic;startFill=1;endArrow=classic;endFill=1;labelBackgroundColor=none;`
- Dashed/reference flow: `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;dashed=1;dashPattern=8 8;endArrow=classic;endFill=1;labelBackgroundColor=none;`

## Post-edit verification (MUST follow — non-negotiable)

**Edit tools can silently fail.** A `multi_replace_string_in_file` call may report "successfully edited" while one or more individual replacements inside it actually failed (because draw.io re-saved the file and reordered attributes, normalized whitespace, or inserted small geometry deltas like `x="-0.0028"`). Trusting the success message alone has caused real bugs (subnets staying at template width and bleeding past the Azure boundary, edge label `<mxPoint>` offsets coming back empty after a re-save).

**After every batch of geometry or style edits to a `.drawio` file, you MUST do BOTH of the following before claiming the change is done:**

1. **Re-read the actual XML** for every cell you intended to change and confirm the new attribute values are present. Do not assume — open the file (or grep for the cell id and inspect the `mxGeometry` / `<mxPoint as="offset">` / style string).
2. **Re-export the PNG and call `view_image` on it.** Compare the rendered output against your mental model of what the change should look like. If a container looks the same size as before, or a label is still on the line, the edit did not apply — go back and fix it.

**Specific things you MUST verify after editing, by re-reading the XML:**
- Container `mxGeometry` `width` / `height` / `x` / `y` actually match the new values you intended.
- Edge `<mxGeometry relative="1" as="geometry">` blocks contain a non-empty child `<mxPoint ... as="offset" />` with the actual `x` or `y` you set (an `<mxPoint as="offset" />` with no coordinates is a defect — it means the offset was stripped).
- Edge style strings contain the exact `exitDy` / `entryDy` / `*Perimeter=0` fragments you added.
- Subnet/vNet/accreditation/region/Azure-boundary widths match what you computed in your layout plan.

**If the verification step shows the file does NOT match your intended edit, treat the original edit as failed and reissue it with a different match string** (the most common cause of silent failure is that draw.io rewrote the attribute order or geometry expression between your reads). Do not move on to the next task until verification passes.

Never tell the user "the change is applied" based solely on a tool success message. The only proofs that count are (a) the new XML in the file, and (b) the rendered PNG.

## How to create a diagram

1. **Start from the template** — read `template.drawio` and use its structure as the base (for architecture diagrams). For non-infrastructure diagrams (flowcharts, sequence diagrams, etc.), skip this step.
2. **Generate draw.io XML** in mxGraphModel format for the requested diagram
3. **Write the XML** to a `.drawio` file in the current working directory using the available file-editing tool
4. **Post-process edge routing** (optional): If `npx @drawio/postprocess` is already available, run it on the `.drawio` file to optimize edge routing (simplify waypoints, fix edge-vertex collisions, straighten approach angles). If it is not available, skip it without installing anything and do not treat that as a failure.
5. **Visual review** — Export a temporary PNG using the draw.io CLI (see below), then **load the PNG with the `view_image` tool** so you can actually see the rendered diagram. Do not skip the `view_image` step or substitute it with opening the file in an external viewer — the agent itself must inspect the rendered output. Verify:
   - No overlapping labels or edges
   - Containers/tiers are properly sized (no excessive empty space)
   - Icons and shapes are legible and not crammed together
   - Edge routes don't cross through unrelated shapes
   - Subnets, boundaries, grouping boxes, and panels do not render on top of icons or connector lines
   - Nested boundaries, logos/icons, labels, and connector paths have visible separation; no edges are coincident or nearly coincident on any side
   - Containers and panels do not include large unused whitespace; boundaries fit their contents with balanced padding
   - Connector lines do not cross icons, logos, or other foreground symbology
   - Connector lines do not run through transparent label text
   - Top/bottom connector endpoints clear the visible service label text below/above icons
   - Double-headed arrows point along the connector direction at both ends
   - External/shared services are outside the accreditation boundary and do not have connection arrows
   - Azure services use official Azure icons
   - All foreground data-flow connectors use the expected line weight for their class
   - All non-empty labels have transparent backgrounds (`labelBackgroundColor=none;`)
   - XML order keeps containers behind connectors, icons, and labels
   - If issues are found, adjust positions/sizes in the XML, re-export, and `view_image` again. Repeat until the layout is clean, then delete the temporary review PNG.

   **Naming the review PNG:** export to `<diagram-name>-review.png` (no `.drawio` infix) so it cannot be confused with a user-requested export (`<diagram-name>.drawio.png`). Always delete the review PNG once the diagram is finalized.
6. **If the user requested an export format** (png, svg, pdf), locate the draw.io CLI (see below), export with `--embed-diagram`. Delete only intermediate `.drawio` files created solely for that export; never delete an existing user-owned `.drawio` source file. If the CLI is not found, keep the `.drawio` file and tell the user they can install the draw.io desktop app to enable export, or open the `.drawio` file directly
7. **Open the result only when appropriate** — open the exported file if exported, or the `.drawio` file otherwise, unless the user says they already have it open or asks not to open it. If the open command fails, print the file path so the user can open it manually.

### Hard validation checks

Before finalizing a diagram, run lightweight XML checks in addition to visual review. These checks do not replace exporting a PNG and inspecting the result.

Run the bundled validator against the diagram:

```bash
.github/skills/drawio/validate-drawio.py diagram.drawio
```

## Choosing the output format

Check the user's request for a format preference. Examples:

- `/drawio create a flowchart` → `flowchart.drawio`
- `/drawio png flowchart for login` → `login-flow.drawio.png`
- `/drawio svg: ER diagram` → `er-diagram.drawio.svg`
- `/drawio pdf architecture overview` → `architecture-overview.drawio.pdf`

If no format is mentioned, write the `.drawio` file. Open it in draw.io only when the user asks or when opening is clearly appropriate; do not open files the user says they already have open. The user can always ask to export later.

### Supported export formats

| Format | Embed XML | Notes |
|--------|-----------|-------|
| `png` | Yes (`-e`) | Viewable everywhere, editable in draw.io |
| `svg` | Yes (`-e`) | Scalable, editable in draw.io |
| `pdf` | Yes (`-e`) | Printable, editable in draw.io |
| `jpg` | No | Lossy, no embedded XML support |

PNG, SVG, and PDF all support `--embed-diagram` — the exported file contains the full diagram XML, so opening it in draw.io recovers the editable diagram.

## draw.io CLI

The draw.io desktop app includes a command-line interface for exporting.

### Locating the CLI

First, detect the environment, then locate the CLI accordingly:

#### WSL2 (Windows Subsystem for Linux)

WSL2 is detected when `/proc/version` contains `microsoft` or `WSL`:

```bash
grep -qi microsoft /proc/version 2>/dev/null && echo "WSL2"
```

On WSL2, use the Windows draw.io Desktop executable via `/mnt/c/...`:

```bash
DRAWIO_CMD="/mnt/c/Program Files/draw.io/draw.io.exe"
```

Use double quotes to handle the space in `Program Files`. Do not use backticks here; backticks perform shell command substitution.

If draw.io is installed in a non-default location, check common alternatives:

```bash
# Default install path
"/mnt/c/Program Files/draw.io/draw.io.exe"

# Per-user install (if the above does not exist)
"/mnt/c/Users/$WIN_USER/AppData/Local/Programs/draw.io/draw.io.exe"
```

#### macOS

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io
```

#### Linux (native)

```bash
drawio   # typically on PATH via snap/apt/flatpak
```

#### Windows (native, non-WSL2)

```
"C:\Program Files\draw.io\draw.io.exe"
```

Use `which drawio` (or `where drawio` on Windows) to check if it's on PATH before falling back to the platform-specific path.

### Export command

```bash
drawio -x -f <format> -e -b 10 -o <output> <input.drawio>
```

**WSL2 example:**

```bash
"/mnt/c/Program Files/draw.io/draw.io.exe" -x -f png -e -b 10 -o diagram.drawio.png diagram.drawio
```

Key flags:
- `-x` / `--export`: export mode
- `-f` / `--format`: output format (png, svg, pdf, jpg)
- `-e` / `--embed-diagram`: embed diagram XML in the output (PNG, SVG, PDF only)
- `-o` / `--output`: output file path
- `-b` / `--border`: border width around diagram (default: 0)
- `-t` / `--transparent`: transparent background (PNG only)
- `-s` / `--scale`: scale the diagram size
- `--width` / `--height`: fit into specified dimensions (preserves aspect ratio)
- `-a` / `--all-pages`: export all pages (PDF only)
- `-p` / `--page-index`: select a specific page (1-based)

### Opening the result

| Environment | Command |
|-------------|---------|
| macOS | `open <file>` |
| Linux (native) | `xdg-open <file>` |
| WSL2 | `cmd.exe /c start "" "$(wslpath -w <file>)"` |
| Windows | `start <file>` |

**WSL2 notes:**
- `wslpath -w <file>` converts a WSL2 path (e.g. `/home/user/diagram.drawio`) to a Windows path (e.g. `C:\Users\...`). This is required because `cmd.exe` cannot resolve `/mnt/c/...` style paths.
- The empty string `""` after `start` is required to prevent `start` from interpreting the filename as a window title.

**WSL2 example:**

```bash
cmd.exe /c start "" "$(wslpath -w diagram.drawio)"
```

## File naming

- Use a descriptive filename based on the diagram content (e.g., `login-flow`, `database-schema`)
- Use lowercase with hyphens for multi-word names
- For export, use double extensions: `name.drawio.png`, `name.drawio.svg`, `name.drawio.pdf` — this signals the file contains embedded diagram XML
- After a successful export, delete only intermediate `.drawio` files that were created solely for the export. Never delete a user-owned source `.drawio` file unless explicitly asked.

## Azure service icons

**Always use official Azure 2 icons for any Azure service.** Use the `image` style with the path `img/lib/azure2/<category>/<Service_Name>.svg`. Common examples:

| Service | Style image path |
|---------|-----------------|
| App Service | `img/lib/azure2/app_services/App_Services.svg` |
| SQL Managed Instance | `img/lib/azure2/databases/SQL_Managed_Instance.svg` |
| Key Vault | `img/lib/azure2/security/Key_Vaults.svg` |
| Entra ID / Azure AD | `img/lib/azure2/identity/Azure_Active_Directory.svg` |
| Notification Hub | `img/lib/azure2/app_services/Notification_Hubs.svg` |
| AI Search | `img/lib/azure2/app_services/Search_Services.svg` |
| Cosmos DB | `img/lib/azure2/databases/Azure_Cosmos_DB.svg` |
| Virtual Network | `img/lib/azure2/networking/Virtual_Networks.svg` |
| Functions | `img/lib/azure2/compute/Function_Apps.svg` |
| Data Factory | `img/lib/azure2/databases/Data_Factory.svg` |
| Azure Monitor | `img/lib/azure2/management_governance/Monitor.svg` |
| Application Insights | `img/lib/azure2/devops/Application_Insights.svg` |
| Log Analytics | `img/lib/mscae/Log_Analytics_Workspaces.svg` |
| Microsoft Sentinel | `img/lib/mscae/Azure_Sentinel.svg` |

**Style format for Azure icons:**
```
image;aspect=fixed;html=1;points=[];align=center;fontSize=11;image=img/lib/azure2/<category>/<Name>.svg;
```

For non-Azure elements (users, browsers, generic clients, external systems), use generic shapes (`shape=mxgraph.networks.pc`, basic rectangles, cloud shapes, etc.).

## XML format

A `.drawio` file is native mxGraphModel XML. Always generate XML directly — Mermaid and CSV formats require server-side conversion and cannot be saved as native files.

### Basic structure

Every diagram must have this structure:

```xml
<mxGraphModel adaptiveColors="auto">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="example" value="Example" parent="1" vertex="1">
      <mxGeometry x="40" y="40" width="120" height="60" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

- Cell `id="0"` is the root layer
- Cell `id="1"` is the default parent layer
- All diagram elements use `parent="1"` unless using multiple layers

## XML reference

For the complete draw.io XML reference including common styles, edge routing, containers, layers, tags, metadata, dark mode colors, and XML well-formedness rules, fetch and follow the instructions at:
https://raw.githubusercontent.com/jgraph/drawio-mcp/main/shared/xml-reference.md

## Edge connection point distribution

When multiple **labeled** edges connect to the same side of a target (or source) cell, you **must** assign distinct `entryX`/`entryY` (or `exitX`/`exitY`) values so that their labels don't overlap and obscure each other.

**Rule:** If N labeled edges enter the same side of a cell, distribute them evenly along that side. For example, 3 labeled edges entering the left side should use `entryX=0;entryY=0.25`, `entryX=0;entryY=0.5`, and `entryX=0;entryY=0.75`.

**When to use connection point overrides:**
- ✅ Multiple labeled edges connect to the same cell — space them apart so text remains readable
- ❌ Edges without labels (empty `value`) sharing a connection point — overlapping is fine
- ❌ A single edge connects to a cell with no other edges on that side — let auto-routing handle it

**Example — 3 labeled edges entering the bottom of a node:**

```xml
<mxCell edge="1" style="...;entryX=0.25;entryY=1;entryDx=0;entryDy=0" target="node1" value="Upload" .../>
<mxCell edge="1" style="...;entryX=0.5;entryY=1;entryDx=0;entryDy=0" target="node1" value="Sync" .../>
<mxCell edge="1" style="...;entryX=0.75;entryY=1;entryDx=0;entryDy=0" target="node1" value="Query" .../>
```

## Edge label positioning (MUST follow)

**Every labeled edge MUST have a perpendicular `<mxPoint>` offset on its `mxGeometry` so the label does not sit on top of the connector line.** Without an offset, draw.io centers the label text directly on the line and the line renders through the text.

```xml
<mxCell id="edge1" value="Pipelines" edge="1" source="a" target="b" style="...">
  <mxGeometry relative="1" as="geometry">
    <mxPoint y="-12" as="offset" />
  </mxGeometry>
</mxCell>
```

**Required offsets:**
- Horizontal edges: `<mxPoint y="-12" as="offset" />` (label above) or `y="12"` (label below). MUST be at least ±10.
- Vertical edges: `<mxPoint x="-12" as="offset" />` (label left) or `x="12"` (label right). MUST be at least ±10.
- Multi-word or long labels: use ±15 to ±20.
- When multiple labeled edges run parallel and close together, alternate offsets (e.g. one at `y="-15"`, the next at `y="15"`) so labels do not stack.

A `mxGeometry` written as `<mxGeometry relative="1" as="geometry" />` (self-closing, no child `mxPoint`) is a defect on any labeled edge — fix it before handoff.

## Edge and icon collision avoidance

Orthogonal edges route in straight horizontal/vertical segments. Before placing icons, verify that no edge segment will pass through another icon's bounding box.

**Common pitfall:** An edge that exits the TOP of node A and routes RIGHT to node B will create a horizontal segment at the target's Y level. If any icon is positioned along that horizontal band between source and target, the edge will visually cross through it.

**Prevention strategy:**
1. Sketch the layout mentally in columns/rows — icons in the same row should be connected by horizontal edges; icons in the same column by vertical edges
2. Place icons that are NOT directly connected in separate rows/columns from the edge paths between connected icons
3. After visual review, if an edge crosses through an unrelated icon, move that icon to a different row/column or reroute the edge using different exit/entry points
4. When multiple edges share the same horizontal or vertical band, stagger their routing with different exit/entry Y (or X) values

## Connector endpoint clearance from Azure icon labels (MUST follow)

Azure 2 SVG icons render their `value` text BELOW the icon (`verticalLabelPosition=bottom`). The cell's bounding box only covers the icon graphic — it does NOT include the label text. Any connector that exits the bottom of an icon (or enters the top of an icon from below) WILL route through the label text unless the endpoint is explicitly pushed past it.

**Required style fragments on the edge:**

- Bottom exit, past label:
  `exitX=0.5;exitY=1;exitDx=0;exitDy=30;exitPerimeter=0;`
- Top entry from below, past label of source icon above:
  `entryX=0.5;entryY=0;entryDx=0;entryDy=-30;entryPerimeter=0;`
- Top exit (icon with label rendered above): `exitDy=-30;exitPerimeter=0;`
- Bottom entry from above: `entryDy=30;entryPerimeter=0;`

**Push values:**
- Single-line label (e.g. "Azure SQL", "Storage"): use `dy=30`.
- Two-line label (e.g. "Azure Synapse / Analytics", "Application Insights"): use `dy=35` to `dy=40`.
- Always pair with `*Perimeter=0` so draw.io respects the absolute offset instead of snapping back to the icon perimeter.

If the visual review shows a connector arrow crossing through any icon's label text, the fix is to add/raise these `*Dy` values — do not move the icon as a workaround.

## Container sizing and whitespace (MUST follow)

Containers (subnets, vNet, accreditation boundary, region label, Azure boundary) are NOT fixed at template size. They MUST be resized to fit their actual contents every time icons are added or removed.

**Rules:**
1. After every add/remove of an icon inside any container, recompute that container's geometry so visible content fits with **20–30 px padding** on all four sides. No more than ~30% of the container area may be empty whitespace.
2. A container holding a single icon MUST be sized to roughly `iconWidth + 80 px` wide and `iconHeight + label + 50 px` tall — do not leave it at the original template width.
3. Resize cascades **outward**: subnet → vNet → accreditation boundary → region label → Azure boundary. After shrinking an inner container, immediately shrink each outer container that wrapped it.
4. Side panels (System Description, Common Services, Other Services, Legend) MUST sit no more than ~50 px to the right of the Azure boundary's right edge. After shrinking the Azure boundary, shift every panel cell (and any legend `sourcePoint`/`targetPoint` x-coordinate) left by the same delta to maintain that gap.
5. Shared-services icon rows along the bottom of the Azure boundary MUST use **at least 80 px column spacing** so multi-word labels ("Azure DevOps", "Application Insights", "Microsoft Entra ID", "Azure Log Analytics") do not collide. 60 px spacing is too tight.
6. Before placing an icon inside a container, verify that the icon's full visual extent (icon width × icon height + ~25 px label height below) fits inside the container with the required padding. If it does not, either move the icon or grow the container before saving.

These rules are validated visually in step 5 (PNG export + `view_image`). Empty right-half whitespace inside any container is a defect.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| draw.io CLI not found | Desktop app not installed or not on PATH | Keep the `.drawio` file and tell the user to install the draw.io desktop app, or open the file manually |
| Export produces empty/corrupt file | Invalid XML (e.g. double hyphens in comments, unescaped special characters) | Validate XML well-formedness before writing; see the XML well-formedness section below |
| Diagram opens but looks blank | Missing root cells `id="0"` and `id="1"` | Ensure the basic mxGraphModel structure is complete |
| Edges not rendering | Edge mxCell is self-closing (no child mxGeometry element) | Every edge must have `<mxGeometry relative="1" as="geometry" />` as a child element |
| File won't open after export | Incorrect file path or missing file association | Print the absolute file path so the user can open it manually |

## CRITICAL: XML well-formedness

- **NEVER include ANY XML comments (`<!-- -->`) in the output.** XML comments are strictly forbidden — they waste tokens, can cause parse errors, and serve no purpose in diagram XML.
- Escape special characters in attribute values: `&amp;`, `&lt;`, `&gt;`, `&quot;`
- Always use unique `id` values for each `mxCell`

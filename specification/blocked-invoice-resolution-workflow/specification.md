# Specification: blocked-invoice-resolution-workflow

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [../guidelines.md](../guidelines.md) — Universal execution rules
> - [../guidelines-n8n-workflow.md](../guidelines-n8n-workflow.md) — n8n workflow constraints

This workflow orchestrates the full daily blocked invoice resolution cycle. It is the sole owner of write-back actions in S/4HANA and is responsible for invoking the AI agent, routing invoices, managing approvals, and sending notifications.

---

## Asset Setup

- [ ] Create asset folder `assets/workflows/blocked-invoice-resolution-workflow/`
- [ ] Invoke `setup-solution` skill to scaffold the asset with `asset.yaml` — asset type: `n8nworkflow`
- [ ] Confirm `asset.yaml` declares `metadata.type: n8nworkflow`
- [ ] Confirm `sourceRoot` in `asset.yaml` is `.` (the default)
- [ ] Add S/4HANA MCP server dependency to `asset.yaml` under `requires`
- [ ] Add Ariba MCP server dependency to `asset.yaml` under `requires`

---

## Node Availability Confirmation

Before planning any nodes, verify the following are available on this instance (already confirmed during intent analysis):
- `n8n-nodes-base.webhook` — daily trigger entry point
- `CUSTOM.sapMcpClient` — S/4HANA and Ariba API calls
- `CUSTOM.sapAgent` — AI agent invocation
- `CUSTOM.sapTaskCenter` — cost center manager approval
- `n8n-nodes-base.microsoftOutlook` — email notifications
- `n8n-nodes-base.switch` — routing by variance threshold and Task Center decision
- `n8n-nodes-base.splitInBatches` — per-invoice iteration
- `n8n-nodes-base.set` — data shaping between nodes
- `n8n-nodes-base.stickyNote` — inline documentation

---

## Workflow Implementation

### Trigger

- [ ] Add a `n8n-nodes-base.webhook` node as the entry point:
  - HTTP Method: POST
  - Path: `blocked-invoice-daily-run`
  - Response mode: `responseNode` (the workflow will respond after processing)
  - Document in a `stickyNote` above: "This webhook must be called once daily by an external scheduler (e.g. SAP BTP Job Scheduler). No native schedule trigger is available on this instance."
- [ ] Read `references/n8n-trigger-nodes/n8n-trigger-nodes-webhook.md` from the n8n-workflow skill before implementing the webhook node

### Fetch Blocked Invoices (M1)

- [ ] Add `CUSTOM.sapMcpClient` node — "Fetch Blocked Invoices":
  - Connect to the S/4HANA MCP server
  - Tool: list blocked invoices (filter: payment block indicator set)
  - `onError`: `continueErrorOutput` — on failure, route to an Outlook notification to the AP team with the error details, then `respondToWebhook` with status `failed`
  - Emit log: `M1.achieved: blocked invoices retrieved from S/4HANA, count={invoice_count}` on success
  - Emit log: `M1.missed: failed to retrieve blocked invoices from S/4HANA, error={error_message}` on error path

### Per-Invoice Loop

- [ ] Add `n8n-nodes-base.splitInBatches` node — "Loop Over Invoices":
  - Batch size: 1 (process one invoice at a time)
  - Read `references/n8n-loops/n8n-loops-loop-over-items.md` from the n8n-workflow skill before implementing

### Enrich Invoice — PO Details (M2 partial)

- [ ] Add `CUSTOM.sapMcpClient` node — "Get Purchase Order":
  - Tool: get purchase order by PO number from the invoice record
  - `onError`: `continueErrorOutput` — on failure, set a flag `enrichment_failed=true` and pass the invoice to the AI agent with a missing-data indicator; do NOT abort the loop
  - Retrieve: PO header (vendor, agreed price per line item, cost center assignment)

### Enrich Invoice — Goods Receipt (M2 partial)

- [ ] Add `CUSTOM.sapMcpClient` node — "Get Goods Receipt Status":
  - Tool: get goods receipt status for the PO
  - `onError`: `continueErrorOutput` — same handling as PO node: flag and continue

### Enrich Invoice — Cost Center Manager (M2 partial)

- [ ] Add `CUSTOM.sapMcpClient` node — "Get Cost Center Manager":
  - Tool: get cost center master record using the cost center assignment from the PO
  - Extract the responsible person's email address
  - `onError`: `continueErrorOutput` — flag and continue

### Enrich Invoice — Ariba Contract Terms (M2 partial)

- [ ] Add `CUSTOM.sapMcpClient` node — "Get Ariba Contract Terms":
  - Connect to the Ariba MCP server
  - Tool: get contract terms by vendor ID from the PO
  - `onError`: `continueErrorOutput` — flag and continue
- [ ] After the four enrichment nodes, add a `n8n-nodes-base.set` node — "Assemble Enriched Invoice":
  - Merge all enrichment results into a single structured invoice record
  - If `enrichment_failed=true` on any field, include a `missing_fields` list in the record
  - Emit log: `M2.achieved: invoice {invoice_id} enriched successfully` if all fields present
  - Emit log: `M2.missed: invoice {invoice_id} enrichment incomplete, missing={missing_fields}` if any field missing

### AI Agent — Classification (M3)

- [ ] Read `references/n8n-sap-agent/n8n-sap-agent.md` from the n8n-workflow skill before implementing this node
- [ ] Add `CUSTOM.sapAgent` node — "Classify Invoice":
  - Pass the fully enriched invoice record as the agent input
  - Agent endpoint: `{{AGENT_BASE_URL}}` (configurable environment variable — do NOT hard-code)
  - `onError`: `continueErrorOutput` — on failure, set `recommended_action=manual_review` and route as an above-tolerance invoice so it reaches the AP team
  - Emit log: `M3.achieved: invoice {invoice_id} classified as {block_reason}, recommendation={action}` on success
  - Emit log: `M3.missed: AI classification failed for invoice {invoice_id}, error={error_message}` on error
- [ ] Add a `stickyNote` above the SAP Agent node documenting the expected input/output shape

### Variance Routing

- [ ] Add `n8n-nodes-base.switch` node — "Route by Variance":
  - Rule 1: `variance_pct < 2` AND `recommended_action == auto_release` → Auto-Release path
  - Rule 2: all other cases → Approval path
  - Read `references/n8n-sap-mcp-client/n8n-sap-mcp-client.md` before implementing any downstream SAP MCP Client nodes

### Auto-Release Path (M4)

- [ ] Add `CUSTOM.sapMcpClient` node — "Release Invoice":
  - Tool: update payment block indicator to release the invoice in S/4HANA
  - `onError`: `continueErrorOutput` — on failure, notify AP team via Outlook with the invoice ID and error, then continue loop
  - Emit log: `M4.achieved: invoice {invoice_id} auto-released, variance={variance_pct}%` on success
  - Emit log: `M4.missed: auto-release failed for invoice {invoice_id}, error={error_message}` on error path

### Approval Path — Email + Task Center (M5)

- [ ] Read `references/n8n-sap-task-center/n8n-sap-task-center.md` from the n8n-workflow skill before implementing the Task Center node
- [ ] Add `n8n-nodes-base.microsoftOutlook` node — "Email Cost Center Manager":
  - To: cost center manager email address (from enrichment)
  - Subject: `Invoice Approval Required: {invoice_id} — {block_reason}`
  - Body: structured HTML email containing:
    - Invoice summary (invoice ID, vendor, amount, PO number)
    - AI classification result (block reason, variance %, confidence)
    - AI recommended action and supporting evidence
    - Instruction to approve or reject via SAP Task Center
  - No credential block in JSON
- [ ] Add `CUSTOM.sapTaskCenter` node — "Create Approval Task":
  - Create an approval task for the cost center manager
  - Task title: `Approve Invoice Release: {invoice_id}`
  - Task description: include the AI classification summary and a link to the invoice in S/4HANA
  - `onError`: `continueErrorOutput` — on failure, send fallback email to AP team noting Task Center creation failed
  - Emit log: `M5.achieved: invoice {invoice_id} approval routed to manager {manager_email}` on success
  - Emit log: `M5.missed: approval routing failed for invoice {invoice_id}, error={error_message}` on error

### Post-Decision Routing (M6)

- [ ] Add `n8n-nodes-base.switch` node — "Route Task Center Decision":
  - Rule 1: decision == `approved` → Release path
  - Rule 2: decision == `rejected` → Rejection notification path
  - This MANDATORY Switch pattern after Task Center is required per `n8n-sap-task-center.md`

- [ ] **Approved path**: Add `CUSTOM.sapMcpClient` node — "Release Approved Invoice":
  - Tool: update payment block indicator to release the invoice in S/4HANA
  - `onError`: `continueErrorOutput` — on failure, notify AP team
  - Emit log: `M6.achieved: invoice {invoice_id} post-decision action completed, decision=approved`

- [ ] **Rejected path**: Add `n8n-nodes-base.microsoftOutlook` node — "Notify AP Team of Rejection":
  - To: AP team distribution list (configured as environment variable `AP_TEAM_EMAIL`)
  - Subject: `Invoice Rejected by Manager: {invoice_id}`
  - Body: invoice details, AI classification, manager's rejection reason
  - Emit log: `M6.achieved: invoice {invoice_id} post-decision action completed, decision=rejected`

### Loop Continuation and Final Response

- [ ] Connect the end of both the auto-release path and the post-decision paths back to the `splitInBatches` node to process the next invoice
- [ ] After the loop is complete, add `n8n-nodes-base.respondToWebhook` node — "Respond to Caller":
  - Return a summary: total invoices processed, count auto-released, count routed for approval, count failed
- [ ] Add a `n8n-nodes-base.set` node before the respond node to aggregate run statistics

---

## Error Handling Summary

| Node (business step) | On error | Error-path action |
|---|---|---|
| Fetch Blocked Invoices (SAP MCP Client) | Continue on error path | Email AP team + respond to webhook with failure status |
| Get Purchase Order (SAP MCP Client) | Continue on error path | Flag missing field; continue enrichment |
| Get Goods Receipt Status (SAP MCP Client) | Continue on error path | Flag missing field; continue enrichment |
| Get Cost Center Manager (SAP MCP Client) | Continue on error path | Flag missing field; continue enrichment |
| Get Ariba Contract Terms (SAP MCP Client) | Continue on error path | Flag missing field; continue enrichment |
| Classify Invoice (SAP Agent) | Continue on error path | Set recommended_action=manual_review; route to approval path |
| Release Invoice — auto-release (SAP MCP Client) | Continue on error path | Email AP team with invoice ID and error |
| Create Approval Task (SAP Task Center) | Continue on error path | Email AP team noting Task Center failure |
| Release Approved Invoice (SAP MCP Client) | Continue on error path | Email AP team with invoice ID and error |

---

## Validation

- [ ] Read and follow ALL rules in `references/execution.md` from the n8n-workflow skill before finalising the workflow JSON
- [ ] Validate the workflow using `validate-n8n-workflow` MCP tool passing both the workflow JSON and `asset.yaml` content
- [ ] Confirm: no `credentials` block in any node in the JSON
- [ ] Confirm: all `connections` reference nodes by `name`, not `id`
- [ ] Confirm: Switch node follows every `CUSTOM.sapTaskCenter` node (MANDATORY pattern)
- [ ] Confirm: every `continueErrorOutput` error path is wired to a downstream node
- [ ] Confirm: `AGENT_BASE_URL` and `AP_TEAM_EMAIL` are referenced as environment variable expressions, not hard-coded values
- [ ] Confirm: `stickyNote` is placed above the SAP Agent node and the webhook trigger node

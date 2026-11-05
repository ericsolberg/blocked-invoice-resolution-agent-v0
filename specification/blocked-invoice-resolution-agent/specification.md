# Specification: blocked-invoice-resolution-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [../guidelines.md](../guidelines.md) — Universal execution rules
> - [../guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [../guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [../guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [../guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` to confirm asset scope
- [ ] Bootstrap agent code in `assets/blocked-invoice-resolution-agent/` using the `sap-agent-bootstrap` instructions (run from inside that directory using copy commands — do NOT create files manually)
- [ ] Install dependencies; validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

- [ ] Create a runtime skill for block reason classification logic at `assets/blocked-invoice-resolution-agent/app/skills/invoice-classification/SKILL.md`:
  - Name: `invoice-classification`
  - Description: Step-by-step reasoning instructions for classifying a blocked invoice and recommending a resolution
  - Content must cover:
    - How to interpret a price variance (compare invoice amount to PO agreed price; compute variance %; check against 2% threshold)
    - How to classify block reasons: price variance, quantity mismatch, missing goods receipt, contract deviation, other
    - How to structure the recommendation output: block_reason (enum), variance_pct (float), recommended_action (enum: auto_release | escalate | manual_review), supporting_evidence (list of data points used), confidence (high | medium | low)
    - Guardrail: if enrichment data is incomplete (missing PO price, missing GR status, or missing contract terms), always recommend `manual_review` — never `auto_release`

---

## Project-Specific Tasks

### Invoice Classification and Recommendation

- [ ] Implement a `classify_invoice` tool in `assets/blocked-invoice-resolution-agent/app/` that:
  - Accepts a fully enriched invoice record (invoice_id, invoice_amount, po_number, po_agreed_price, po_quantity, gr_status, gr_quantity, contract_terms, vendor_id)
  - Loads and applies the `invoice-classification` runtime skill
  - Returns a structured classification result: `{ block_reason, variance_pct, recommended_action, supporting_evidence, confidence }`
  - Uses the LLM for reasoning — does NOT apply hard-coded rules for the classification step
  - Guardrail: if any required field is missing or null, set `recommended_action: manual_review` and `confidence: low` without calling the LLM

### MCP Tool Wiring

- [ ] Wire the S/4HANA MCP server tools in `agent.py` using `get_mcp_tools()` — the agent must be able to call:
  - `list_blocked_invoices` — retrieve all invoices with a payment block
  - `get_invoice_details` — read a single invoice's full details by invoice ID
  - `get_purchase_order` — retrieve PO header and line items by PO number
  - `get_goods_receipt_status` — check GR posting status for a PO
  - `get_cost_center` — retrieve cost center master record to find the responsible manager's email
  - `release_invoice` — remove the payment block on an invoice (write operation — mark as high-risk in system prompt)
- [ ] Wire the Ariba MCP server tools in `agent.py`:
  - `get_contract_terms` — retrieve supplier contract terms by vendor ID

### System Prompt

- [ ] In `assets/blocked-invoice-resolution-agent/app/agent.py`, write the system prompt to:
  - Define the agent's role: classify blocked invoices and recommend resolution actions
  - Instruct the agent to always use MCP tools to retrieve live data — never invent or assume data
  - Instruct the agent that `release_invoice` is a high-risk write operation and must NEVER be called directly — the n8n workflow is the only caller of this tool; the agent's role is classification and recommendation only
  - Reference the `invoice-classification` skill for reasoning instructions
  - Specify the required output structure: `{ invoice_id, block_reason, variance_pct, recommended_action, supporting_evidence, confidence }`

---

## Business Instrumentation

- [ ] Implement structured logging and OpenTelemetry spans for all six milestones from `product-requirements-document.md`:
  - `M2.achieved/missed` — invoice enrichment complete/incomplete (log: `M2.achieved: invoice {invoice_id} enriched successfully` / `M2.missed: invoice {invoice_id} enrichment incomplete, missing={missing_fields}`)
  - `M3.achieved/missed` — AI classification complete/failed (log: `M3.achieved: invoice {invoice_id} classified as {block_reason}, recommendation={action}` / `M3.missed: AI classification failed for invoice {invoice_id}, error={error_message}`)
  - Note: M1, M4, M5, M6 are owned by the n8n workflow; the agent only instruments M2 and M3
- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [ ] Add S/4HANA MCP server dependency to `asset.yaml` under `requires` using the ORD ID from `assets/blocked-invoice-s4hana-mcp-server/asset.yaml`
- [ ] Add Ariba MCP server dependency to `asset.yaml` under `requires` using the ORD ID from `assets/blocked-invoice-ariba-mcp-server/asset.yaml`
- [ ] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP server specs are available

---

## Testing

- [ ] `conftest.py` only sets `IBD_TESTING=true`
- [ ] Write unit test for `classify_invoice` tool — mock MCP responses for a price variance case, a GR missing case, and an incomplete data case
- [ ] Write unit test for the guardrail: when `po_agreed_price` is null, result must be `manual_review` with `confidence: low`
- [ ] Write one integration test: provide a fully enriched mock invoice and verify the agent returns a valid structured classification result
- [ ] Run `pytest` from `assets/blocked-invoice-resolution-agent/` (no args)
- [ ] If coverage < 70%, add tests until threshold met
- [ ] Run `pytest` again to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/blocked-invoice-resolution-agent/`

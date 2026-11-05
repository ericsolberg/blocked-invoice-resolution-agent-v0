# Blocked Invoice Resolution Automation

Automated daily workflow that resolves blocked supplier invoices end-to-end — from detection in S/4HANA through AI-driven classification, policy-based auto-release, and cost center manager approval.

## Business Challenge

The Accounts Payable team manually reviews blocked invoices every day — a slow, error-prone process that delays supplier payments and ties up AP staff. For each blocked invoice, they must individually look up the originating purchase order, check the goods receipt, verify contract terms in Ariba, judge the root cause, decide on release or escalation, and then notify the relevant cost center manager. The goal is to automate this end-to-end using an AI agent for reasoning, and to auto-release invoices within tolerance while routing all exceptions to managers via SAP Task Center with full context.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Average time to clear a blocked invoice | 3 days | 1 day | — | Invoice to Pay | user |
| Volume of invoices escalated to managers | — | −30% | — | Invoice to Pay | user |

## Key Milestones

1. **Blocked invoices retrieved** — daily run fetches all currently blocked invoices from S/4HANA
2. **Invoice context enriched** — each invoice is enriched with its PO details, goods receipt, and Ariba supplier contract terms
3. **AI classification complete** — AI agent classifies the block reason and recommends a resolution action for every invoice
4. **Auto-release executed** — invoices with a PO-to-invoice variance below 2% are automatically released in S/4HANA
5. **Approval routing sent** — remaining invoices are sent to the responsible cost center manager via Outlook email and SAP Task Center task
6. **Post-decision actions complete** — approved invoices are released in S/4HANA; rejected invoices trigger an AP team notification for manual follow-up

## Business Architecture (RBA)

### End-to-End Process

Source to Pay

### Process Hierarchy

```
Source to Pay
└── Invoice to Pay (generic)
    └── Process supplier invoices (generic) [BPS-325]
        └── Receive and process supplier invoices
        └── Validate invoice against PO and goods receipt
        └── Block reason classification and resolution
        └── Tolerance-based auto-release
        └── Manager approval routing
└── Procure to Receipt (generic)
    └── Purchase products and services (generic) [BPS-329]
        └── Manage purchase order
        └── Goods receipt confirmation
```

### Summary

Blocked invoice resolution maps to Source to Pay → Invoice to Pay as the primary E2E, with Procure to Receipt (PO and goods receipt retrieval) as a supporting process. AI-driven block classification, tolerance-based auto-release, and cost-center manager routing are automation layers on top of standard SAP supplier invoice validation and approval.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|---|---|---|---|---|---|---|---|---|
| Retrieve all blocked supplier invoices from S/4HANA | SAP S/4HANA Cloud — Supplier Invoice Processing | `sap.s4:apiResource:API_SUPPLIERINVOICE_PROCESS_SRV:v1` | — | — | — | — | Yes | No MCP server found; custom MCP server asset required |
| Retrieve purchase order details per invoice | SAP S/4HANA Cloud — Purchase Order Processing | `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1` | — | — | — | — | Yes | No MCP server found; covered by same MCP server asset as invoice API |
| Retrieve goods receipt confirmations | SAP S/4HANA Cloud — Goods Receipt | `sap.s4:apiResource:SSPOPENITMGOODSRECEIPT_0001:v1` | — | — | — | — | Yes | No MCP server found; covered by same MCP server asset |
| Look up responsible cost center manager from PO | SAP S/4HANA Cloud — Cost Center | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | — | — | — | — | Yes | No MCP server found; covered by same MCP server asset |
| Check supplier contract terms in Ariba | SAP Ariba — Contract Terms Management | `sap.aribas4:apiResource:contract_terms_management:v1` | — | — | — | — | Yes | No MCP server found; separate Ariba MCP server asset required |
| AI classification of block reason and resolution recommendation | AI Agent (custom Python) | — | — | — | — | — | No | Covered by AI Agent asset in this solution |
| Auto-release invoice in S/4HANA when variance < 2% | SAP S/4HANA Cloud — Supplier Invoice Processing | `sap.s4:apiResource:API_SUPPLIERINVOICE_PROCESS_SRV:v1` | — | — | — | — | Yes | Uses same S/4HANA MCP server; release action via write operation |
| Route invoice for cost center manager approval | SAP Task Center (HITL) | — | — | — | — | — | No | `CUSTOM.sapTaskCenter` node available on this n8n instance |
| Email notification to cost center manager with AI analysis | Microsoft Outlook | — | — | — | — | — | No | `n8n-nodes-base.microsoftOutlook` available |
| Email notification to AP team on rejection | Microsoft Outlook | — | — | — | — | — | No | `n8n-nodes-base.microsoftOutlook` available |
| Daily scheduled trigger | n/a — schedule trigger not available on this instance | — | — | — | — | — | Yes | Workaround: webhook trigger; an external scheduler (e.g. SAP BTP Job Scheduler) must call it once daily |

### Key Findings

- S/4HANA APIs for supplier invoices, purchase orders, goods receipts, and cost centers are all available but have no pre-built MCP servers — a single custom S/4HANA MCP server asset will be built covering all four.
- Ariba Contract Terms Management API is available but also has no MCP server — a separate Ariba MCP server asset will be built.
- The AI agent classifies block reasons and recommends resolutions, enabling dynamic reasoning that a static workflow node cannot reliably handle; n8n Workflow + AI Agent is the appropriate pattern.
- SAP Task Center (`CUSTOM.sapTaskCenter`) is available for in-SAP manager approvals; Microsoft Outlook is available for email delivery.
- A daily schedule trigger node is not available on this n8n instance; the workflow will use a webhook trigger, and the user must configure an external daily scheduler to call it.
- Auto-release tolerance is fixed at 2% variance between PO price and invoice amount; manager lookup uses the cost center on the PO in S/4HANA.

## Recommendations

### Blocked Invoice Resolution Automation

#### Executive Summary

n8n workflow + AI agent automates daily blocked invoice clearance end-to-end.

#### Recommended Solution

Build a daily-triggered n8n workflow that:
1. Calls a custom S/4HANA MCP server to fetch all blocked invoices, then enriches each with its PO, goods receipt, and cost center manager details.
2. Calls a custom Ariba MCP server to retrieve the supplier's contract terms.
3. Invokes an AI agent (Python, A2A protocol) to classify the block reason and produce a structured resolution recommendation.
4. Uses a Switch node to route: invoices with variance < 2% are auto-released via the S/4HANA MCP server write operation; all others proceed to the approval path.
5. Sends the cost center manager an Outlook email with the AI analysis and recommended action, and creates a SAP Task Center approval task.
6. Post-decision: approved invoices are released via S/4HANA MCP Client; rejected invoices trigger an Outlook notification to the AP team for manual follow-up.

The solution requires two MCP server assets (S/4HANA, Ariba) and one AI Agent asset alongside the n8n workflow asset.

#### Problem Statement

Accounts payable teams spend significant time manually triaging blocked invoices, leading to delayed supplier payments, strained supplier relationships, and AP staff inefficiency. There is no automated mechanism to enrich, classify, or route blocked invoices, meaning every exception requires manual intervention regardless of its complexity.

#### Affected User Roles

- Accounts Payable Specialist — currently performs all manual triage
- Cost Center Manager — approver for above-tolerance exceptions
- AP Team Lead — handles rejections and escalations

#### Important Factors

##### Reduces manual effort through AI-driven classification
The AI agent analyses each blocked invoice in the context of its PO, goods receipt, and contract terms, producing a structured recommendation. This removes the need for AP staff to perform context gathering and eliminates repetitive low-complexity decisions.

##### Policy enforcement through tolerance-based auto-release
Invoices within the 2% variance threshold are released without human involvement, ensuring consistent policy application and eliminating the approval overhead for routine minor variances.

##### Contextual approvals via Task Center
Cost center managers receive full context (invoice details, AI analysis, recommended action) before acting in SAP Task Center, reducing back-and-forth and improving decision quality.

#### Potential Risks

##### External scheduler dependency
The n8n instance does not support a native schedule trigger. The daily execution depends on an external scheduler correctly calling the webhook; a misconfiguration would cause the workflow to not run.

##### Ariba API integration complexity
The Ariba Contract Terms Management API requires separate authentication and connectivity; availability and response time from Ariba may affect the overall workflow duration.

#### Recommended Solution Category

n8n Workflow, AI Agent, MCP Server

#### Intent Fit

92%

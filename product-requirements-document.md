# Product Requirements Document (PRD)

**Title:** Blocked Invoice Resolution Automation
**Date:** 2026-11-04
**Owner:** Accounts Payable / Finance Operations
**Solution Category:** n8n Workflow · AI Agent · MCP Server

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Every day, the Accounts Payable team manually reviews blocked invoices — looking up purchase orders, checking goods receipts, verifying Ariba contract terms, and deciding whether to release or escalate. This solution automates that entire cycle: it retrieves all blocked invoices from S/4HANA each morning, enriches them with full context, uses an AI agent to classify the block reason and recommend a resolution, auto-releases low-risk cases, and routes everything else to the responsible cost center manager with a single contextual approval task.

**Business Need:**
Blocked invoices accumulate daily and tie up AP staff in repetitive, low-complexity work. Without automation, each invoice requires individual lookups across S/4HANA and Ariba, manual judgement calls, and back-and-forth with cost center managers — all without a standardised process or an audit trail. Delays in resolution damage supplier relationships and increase payment risk.

**Expected Value:**
- Reduce the average time to clear a blocked invoice from 3 days to 1 day
- Reduce the volume of invoices escalated to cost center managers by 30%
- Eliminate manual context-gathering by AP staff for routine blocked invoice cases

**Product Objectives (Prioritised):**
1. Automate end-to-end triage of blocked invoices — from detection to resolution action — with no manual AP involvement for cases within policy tolerance
2. Provide cost center managers with complete, AI-enriched context at the point of approval, reducing decision time and back-and-forth
3. Ensure consistent application of the 2% variance tolerance policy across all invoices

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Average time to clear a blocked invoice | 3 days | 1 day | — | Invoice to Pay | user |
| Volume of invoices escalated to cost center managers | — | −30% | — | Invoice to Pay | user |

---

## User Profiles & Personas

### Primary Persona: Alex — Accounts Payable Specialist

Alex is a 31-year-old AP specialist at a mid-to-large enterprise. Every morning they open S/4HANA's blocked invoice list, which can hold anywhere from 15 to 80 items. For each invoice, Alex manually navigates to the originating purchase order, checks whether a goods receipt was posted, opens Ariba to look up the supplier's contract terms, forms a judgement about the block reason, and either releases the invoice or sends an email to the cost center manager asking for approval. This takes 20–40 minutes per invoice. Alex is technically proficient with SAP but frustrated by the lack of automation and the absence of a structured approval trail. Success for Alex means starting the day with a processed queue, not a pile of manual lookups.

### Secondary Persona: Jordan — Cost Center Manager

Jordan is a 44-year-old department head who receives ad hoc emails from the AP team asking for invoice approvals. The emails rarely include enough context — Jordan typically has to ask follow-up questions before deciding. Approvals are not tracked in a system, making it hard for Jordan to prove compliance. Jordan needs clear, concise information and a simple way to approve or reject without leaving the core SAP environment.

### Other User Types

- **AP Team Lead**: Receives email notifications when a cost center manager rejects an invoice. Responsible for manual follow-up and resolution of escalated cases.
- **Finance Auditor** (observer): Needs a reliable audit trail of all classification decisions, auto-releases, and approvals.

---

## User Goals & Tasks

### For Alex (AP Specialist):

**Goals:**
- Start each working day with blocked invoices already triaged — only genuine exceptions requiring human judgement in the queue
- Have confidence that the 2% variance policy is applied consistently without manual calculation

**Key Tasks:**
- Review any invoices the system could not process (errors or data gaps)
- Act on AP team notifications triggered by manager rejections

### For Jordan (Cost Center Manager):

**Goals:**
- Receive approval requests with complete context — no follow-up questions needed
- Complete approvals quickly from within SAP Task Center

**Key Tasks:**
- Review the AI agent's block reason classification and recommendation in the Task Center task
- Approve or reject the invoice release

---

## Product Principles

1. **Context before approval**: Every approval request must carry the full context the approver needs — invoice details, PO, goods receipt, contract terms, and AI recommendation — so approvers never need to ask a follow-up question.
2. **Policy enforcement by default**: The 2% variance tolerance is applied automatically and uniformly; no AP staff member can inadvertently override it.
3. **Human-in-the-loop for exceptions only**: Automation handles routine cases; humans act only where genuine judgement is required.
4. **Audit trail at every step**: Every classification, auto-release, and approval decision is logged with the supporting data for compliance.

---

## Business Context

**Current State:**
AP specialists manually triage all blocked invoices each day. The process requires navigating between S/4HANA and Ariba without automation, and communicating approval requests via unstructured email. There is no consistent policy enforcement, no audit trail, and no SLA on resolution time. Average clearance time is 3 days.

**Strategic Alignment:**
This solution supports the organisation's Source-to-Pay automation strategy — specifically the Invoice to Pay sub-process — and reduces operational cost in Finance by applying AI to repetitive exception management tasks.

---

## Goals and Non-Goals

### Goals (In Scope)

- Automated daily retrieval and triage of all blocked invoices from S/4HANA
- AI-driven block reason classification with structured resolution recommendation per invoice
- Auto-release of invoices with PO-to-invoice variance less than 2%
- Approval routing to cost center managers via Outlook email and SAP Task Center with full AI context
- Post-decision write-back to S/4HANA (release on approval, AP team notification on rejection)

### Non-Goals (Out of Scope)

- Creation of new supplier invoices or purchase orders
- Supplier-facing portal or Ariba Network interactions
- Procurement scheduling agreement changes
- Analytics dashboards or reporting beyond the audit trail
- Handling credit memos, debit memos, or invoice cancellations

---

## Requirements

### Must-Have Requirements

**R1: Daily Blocked Invoice Retrieval**
- **Problem to Solve**: AP staff manually open S/4HANA every morning to find blocked invoices, with no automated trigger.
- **User Story**: As an AP Specialist, I need all blocked invoices to be automatically retrieved from S/4HANA each day so that I do not have to initiate the process manually.
- **Acceptance Criteria**:
  - Given the daily trigger fires, when the workflow runs, then all invoices with a payment block in S/4HANA are retrieved and available for processing.
  - Given no blocked invoices exist, when the workflow runs, then it completes cleanly with a logged summary of zero items.
- **Maps to Objective**: 1
- **Priority Rank**: 1

**R2: Per-Invoice Context Enrichment**
- **Problem to Solve**: Without consolidated context, any decision about a blocked invoice requires multiple manual lookups across systems.
- **User Story**: As an AP Specialist, I need each blocked invoice to be automatically enriched with its PO details, goods receipt confirmation, Ariba supplier contract terms, and the responsible cost center manager's identity so that decisions can be made without additional lookups.
- **Acceptance Criteria**:
  - Given a retrieved blocked invoice, when enrichment runs, then the workflow has attached: the originating PO (quantity, agreed price, vendor), the goods receipt status, the relevant Ariba contract terms, and the email address/identity of the cost center manager from the PO's cost center.
- **Maps to Objective**: 1, 2
- **Priority Rank**: 2

**R3: AI-Driven Block Reason Classification and Recommendation**
- **Problem to Solve**: AP staff must manually judge why each invoice is blocked and what to do about it, consuming significant time and producing inconsistent outcomes.
- **User Story**: As an AP Specialist, I need an AI agent to classify the block reason for each invoice and recommend a resolution so that the process is consistent and fast.
- **Acceptance Criteria**:
  - Given a fully enriched invoice record, when the AI agent runs, then it returns a structured classification (e.g. price variance, quantity mismatch, missing GR, contract deviation) and a recommended action (auto-release / escalate / manual review).
  - The recommendation must reference the specific data points that drove the conclusion.
- **Maps to Objective**: 1, 2
- **Priority Rank**: 3

**R4: Automatic Release of Low-Variance Invoices**
- **Problem to Solve**: Invoices with minor variances within policy tolerance still require manual AP release today, wasting time on routine cases.
- **User Story**: As an AP Specialist, I need invoices where the PO-to-invoice variance is less than 2% to be automatically released in S/4HANA so that routine low-risk cases clear without any manual intervention.
- **Acceptance Criteria**:
  - Given an invoice where the variance between PO price and invoice amount is less than 2%, when the tolerance check passes, then the invoice payment block is removed in S/4HANA automatically.
  - Given an invoice where the variance is 2% or above, when the check runs, then the invoice is not auto-released and is routed for approval.
- **Maps to Objective**: 1, 3
- **Priority Rank**: 4

**R5: Cost Center Manager Approval Routing with Full Context**
- **Problem to Solve**: Approval requests sent by email today lack context, leading to follow-up questions and delays.
- **User Story**: As a Cost Center Manager, I need to receive an Outlook email with the AI agent's full analysis and a SAP Task Center approval task so that I can make an informed decision without any follow-up.
- **Acceptance Criteria**:
  - Given an above-tolerance invoice, when routing executes, then: (a) the responsible cost center manager receives an Outlook email containing the invoice summary, AI classification, variance details, and recommended action; and (b) a corresponding SAP Task Center task is created for the manager to approve or reject.
- **Maps to Objective**: 2
- **Priority Rank**: 5

**R6: Post-Decision Write-Back and AP Notification**
- **Problem to Solve**: After a manager decides in Task Center, no automated action follows — AP must check the outcome and act manually.
- **User Story**: As an AP Specialist, I need the system to automatically release approved invoices in S/4HANA and immediately notify the AP team when an invoice is rejected so that no manual monitoring of Task Center outcomes is required.
- **Acceptance Criteria**:
  - Given a manager approves the Task Center task, when the workflow resumes, then the invoice payment block is removed in S/4HANA.
  - Given a manager rejects the Task Center task, when the workflow resumes, then an Outlook email is sent to the AP team with the invoice details, the AI classification, and the rejection reason.
- **Maps to Objective**: 1
- **Priority Rank**: 6

### High-Want Requirements

**R7: Error Handling and AP Team Alerting**
- **Problem to Solve**: If the workflow fails to retrieve data from S/4HANA or Ariba for a specific invoice, it should not silently discard that invoice.
- **User Story**: As an AP Specialist, I need to be notified via email if the workflow cannot enrich or process a specific invoice so that I can handle it manually without missing it.
- **Priority Rank**: 1

---

## Non-Functional Requirements

### Performance
- **Throughput**: The workflow must be capable of processing up to 100 blocked invoices per daily run within a 30-minute window.
- **Latency**: Each AI agent call per invoice must complete within 60 seconds under normal load.

### Reliability
- **Availability**: The workflow must complete its daily run reliably; failures in individual invoice processing must not abort the entire batch.
- **Fallback**: If S/4HANA or Ariba enrichment fails for an invoice, the invoice is skipped and flagged for manual AP review rather than discarding the entire run.

### Explainability
- **Traceability**: Each AI recommendation must reference the specific data points (variance percentage, contract term, GR status) that informed it.
- **Decision Logging**: All auto-releases and approval routing actions must be logged with the invoice ID, classification, and variance value.

---

## Solution Architecture

**Architecture Overview:**
A webhook-triggered n8n workflow acts as the orchestrator. It calls a custom S/4HANA MCP server to retrieve and enrich invoice data, calls a custom Ariba MCP server for contract terms, invokes a Python AI agent (A2A protocol) for classification and recommendation, then routes each invoice through a Switch node — auto-releasing low-variance cases via S/4HANA MCP write, and routing exceptions through SAP Task Center and Outlook. Post-decision, the workflow writes back to S/4HANA or notifies the AP team.

**Key Components:**
- **n8n Workflow**: Orchestrates the full daily cycle — trigger, enrichment, agent invocation, routing, approvals, write-back
- **AI Agent (Python/A2A)**: Classifies block reasons and produces structured resolution recommendations using enriched invoice context
- **S/4HANA MCP Server**: Provides tool access to Supplier Invoice, Purchase Order, Goods Receipt, and Cost Center APIs in S/4HANA
- **Ariba MCP Server**: Provides tool access to Ariba Contract Terms Management API
- **SAP Task Center**: Hosts approval tasks for cost center managers
- **Microsoft Outlook**: Delivers notification and approval emails to managers and the AP team

**Integration Points:**
- S/4HANA (read: blocked invoices, PO, GR, cost center; write: release payment block) — daily batch
- SAP Ariba (read: contract terms) — per invoice, during daily run
- SAP Task Center (write: create approval task; read: decision outcome) — per above-tolerance invoice
- Microsoft Outlook (write: send email) — per approval routing and rejection

**Deployment Environments:**
- The solution is deployed on SAP BTP; the n8n workflow is hosted on the SAP-managed n8n instance. The AI agent is deployed as a BTP application. MCP servers are deployed as BTP services.

### Automation & Agent Behaviour

**Automation Level:** Hybrid — rule-based routing (variance threshold) combined with an autonomous AI agent for classification and recommendation

**Actions the system performs without human approval:**
- Retrieve all blocked invoices from S/4HANA
- Enrich each invoice with PO, goods receipt, Ariba contract terms, and cost center manager data
- Invoke the AI agent for classification and recommendation
- Remove the payment block in S/4HANA for invoices with variance < 2%
- Send Outlook email and create Task Center task for above-tolerance invoices
- Send AP team rejection notification email after manager rejects

**Actions that require human review or approval:**
- Invoice release for any invoice with a PO-to-invoice variance ≥ 2% (requires cost center manager approval in SAP Task Center)

**Model or engine used:** SAP Generative AI Hub (LLM via SAP AI Core), invoked by the Python AI agent

**Knowledge & data sources accessed:**
- S/4HANA: Supplier Invoice data, Purchase Order data, Goods Receipt data, Cost Center master data
- SAP Ariba: Supplier contract terms (Contract Terms Management API)

**Tools or connectors invoked:**
- `get_blocked_invoices` (S/4HANA MCP Server, read): Retrieves all invoices with a payment block
- `get_purchase_order` (S/4HANA MCP Server, read): Retrieves PO details for a given invoice
- `get_goods_receipt` (S/4HANA MCP Server, read): Retrieves goods receipt status for a PO
- `get_cost_center_manager` (S/4HANA MCP Server, read): Looks up the responsible manager from cost center on the PO
- `get_contract_terms` (Ariba MCP Server, read): Retrieves supplier contract terms from Ariba
- `release_invoice` (S/4HANA MCP Server, write): Removes the payment block on an invoice — high-risk write operation
- SAP Task Center (CUSTOM.sapTaskCenter, write/read): Creates approval tasks and reads decisions
- Microsoft Outlook (n8n node, write): Sends emails to cost center managers and AP team

**Guardrails & fail-safes:**
- The AI agent must never directly release or modify an invoice — only the n8n workflow may call the release tool after an explicit routing decision
- If the variance calculation cannot be performed (missing PO price), the invoice must be routed for manual AP review, never auto-released
- If enrichment from S/4HANA or Ariba fails for an invoice, that invoice is skipped and flagged to the AP team; the remaining invoices continue to be processed
- AI confidence or data completeness gaps must be surfaced in the recommendation text so approvers can judge accordingly

---

## Milestones

### M1: Blocked Invoices Retrieved

- **Description**: The workflow has successfully fetched all blocked invoices from S/4HANA for the current daily run
- **Achieved when**: At least one blocked invoice is returned and available for enrichment; or a clean zero-item result is confirmed
- **Log on achievement**: `M1.achieved: blocked invoices retrieved from S/4HANA, count={invoice_count}`
- **Log on miss**: `M1.missed: failed to retrieve blocked invoices from S/4HANA, error={error_message}`

### M2: Invoice Enriched

- **Description**: A single invoice has been enriched with PO details, goods receipt status, Ariba contract terms, and the responsible cost center manager's identity
- **Achieved when**: All four data elements are present on the invoice record
- **Log on achievement**: `M2.achieved: invoice {invoice_id} enriched successfully`
- **Log on miss**: `M2.missed: invoice {invoice_id} enrichment incomplete, missing={missing_fields}`

### M3: AI Classification Complete

- **Description**: The AI agent has returned a structured classification and resolution recommendation for the invoice
- **Achieved when**: The agent response contains a block reason category, a recommended action, and supporting data references
- **Log on achievement**: `M3.achieved: invoice {invoice_id} classified as {block_reason}, recommendation={action}`
- **Log on miss**: `M3.missed: AI classification failed for invoice {invoice_id}, error={error_message}`

### M4: Invoice Auto-Released

- **Description**: An invoice within the 2% variance tolerance has been automatically released in S/4HANA
- **Achieved when**: The payment block removal call to S/4HANA returns success for a qualifying invoice
- **Log on achievement**: `M4.achieved: invoice {invoice_id} auto-released, variance={variance_pct}%`
- **Log on miss**: `M4.missed: auto-release failed for invoice {invoice_id}, error={error_message}`

### M5: Approval Routed to Cost Center Manager

- **Description**: An above-tolerance invoice has been sent to the cost center manager via Outlook and a Task Center task has been created
- **Achieved when**: Both the Outlook email and the SAP Task Center task are confirmed as created
- **Log on achievement**: `M5.achieved: invoice {invoice_id} approval routed to manager {manager_email}`
- **Log on miss**: `M5.missed: approval routing failed for invoice {invoice_id}, error={error_message}`

### M6: Post-Decision Action Executed

- **Description**: After the cost center manager approves or rejects in Task Center, the corresponding action has been completed
- **Achieved when**: Either the invoice is released in S/4HANA (approval path) or the AP team rejection notification email is confirmed sent (rejection path)
- **Log on achievement**: `M6.achieved: invoice {invoice_id} post-decision action completed, decision={approved|rejected}`
- **Log on miss**: `M6.missed: post-decision action failed for invoice {invoice_id}, decision={approved|rejected}, error={error_message}`

---

## Risks, Assumptions, and Dependencies

### Risks

- **External scheduler dependency**: The n8n instance does not support a native schedule trigger. Daily execution depends on an external scheduler (e.g. SAP BTP Job Scheduler) correctly calling the workflow webhook. A misconfiguration would cause the workflow not to run.
- **Ariba API availability**: The Ariba Contract Terms Management API requires separate authentication and connectivity. Latency or unavailability could affect the daily run window.
- **AI classification accuracy**: The AI agent's classification quality depends on the completeness and consistency of the enrichment data. Sparse or inconsistent PO/contract data will reduce recommendation reliability.

### Assumptions

- The S/4HANA Supplier Invoice API returns a filterable list of invoices with a payment block indicator.
- The cost center on the PO in S/4HANA contains a responsible person field with a valid email address.
- The Ariba Contract Terms Management API is accessible from the BTP tenant where the solution is deployed.
- Cost center managers have access to SAP Task Center and check it regularly.

### Dependencies

- SAP BTP Job Scheduler (or equivalent) for daily webhook invocation
- S/4HANA connectivity from BTP (Business Connector / destination configuration)
- Ariba connectivity from BTP
- SAP Task Center configuration and manager assignments
- Microsoft Outlook integration credentials on the n8n instance

---

## Open Questions

- What is the exact S/4HANA field or API filter parameter for "payment block" on the Supplier Invoice API?
- Does the cost center master in S/4HANA reliably contain the responsible manager's email, or is a fallback needed?
- Is there a maximum Task Center task age after which unanswered approvals should be escalated?

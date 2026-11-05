---
name: invoice-classification
description: Step-by-step reasoning instructions for classifying a blocked supplier invoice and recommending a resolution action.
allowed-tools: []
---

# Invoice Classification Skill

Use this skill when you receive an enriched invoice record and need to determine the block reason and recommend a resolution.

## Step 1 — Check Data Completeness

Before any classification, verify that all required fields are present in the invoice record:
- `invoice_amount` (the amount billed by the supplier)
- `po_agreed_price` (the price agreed in the purchase order)
- `po_quantity` (quantity ordered)
- `gr_status` (whether a goods receipt has been posted: YES / NO / PARTIAL)
- `contract_terms` (the supplier's Ariba contract terms, at minimum the agreed price range)
- `vendor_id`

**If any of these fields is null, missing, or marked as "unavailable":**
- Set `block_reason` to `incomplete_data`
- Set `recommended_action` to `manual_review`
- Set `confidence` to `low`
- List the missing fields in `supporting_evidence`
- STOP — do not proceed to Step 2.

## Step 2 — Calculate Variance

Compute the price variance percentage:

```
variance_pct = abs(invoice_amount - po_agreed_price) / po_agreed_price * 100
```

Round to 2 decimal places. Record this as `variance_pct` in your output.

## Step 3 — Classify Block Reason

Evaluate the following conditions in order (first match wins):

| Condition | Block Reason |
|---|---|
| `invoice_amount > po_agreed_price` and `variance_pct >= 2` | `price_variance` |
| `invoice_amount < po_agreed_price` and `variance_pct >= 2` | `price_variance` |
| `gr_status == "NO"` | `missing_goods_receipt` |
| `gr_status == "PARTIAL"` and invoice quantity > GR quantity | `quantity_mismatch` |
| Invoice amount or payment terms deviate from Ariba `contract_terms` | `contract_deviation` |
| None of the above | `other` |

## Step 4 — Determine Recommended Action

| Condition | Recommended Action |
|---|---|
| `variance_pct < 2` AND `gr_status == "YES"` AND no contract deviation | `auto_release` |
| `block_reason` is `price_variance`, `quantity_mismatch`, or `contract_deviation` | `escalate` |
| `block_reason` is `missing_goods_receipt` | `manual_review` |
| `block_reason` is `other` or `incomplete_data` | `manual_review` |

## Step 5 — Assess Confidence

| Situation | Confidence |
|---|---|
| All fields present, block reason is clear and unambiguous | `high` |
| All fields present but block reason requires interpretation | `medium` |
| Any field missing or block reason could fit multiple categories | `low` |

## Step 6 — Build Supporting Evidence

List the specific data points that drove your classification. Examples:
- "Invoice amount 1050 EUR vs PO agreed price 1000 EUR — 5.0% variance"
- "Goods receipt not yet posted for PO 4500012345"
- "Ariba contract specifies max price 980 EUR per unit; invoice price is 1050 EUR"

## Output Structure

Return exactly this JSON structure:

```json
{
  "invoice_id": "<invoice_id from input>",
  "block_reason": "<price_variance | missing_goods_receipt | quantity_mismatch | contract_deviation | incomplete_data | other>",
  "variance_pct": <float>,
  "recommended_action": "<auto_release | escalate | manual_review>",
  "supporting_evidence": ["<data point 1>", "<data point 2>"],
  "confidence": "<high | medium | low>"
}
```

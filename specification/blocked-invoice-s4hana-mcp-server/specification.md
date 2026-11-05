# Specification: blocked-invoice-s4hana-mcp-server

> **Guidelines**: Read [../guidelines.md](../guidelines.md) before executing ANY tasks below.

This asset is a custom MCP server that exposes S/4HANA data to both the n8n workflow and the AI agent. It wraps four S/4HANA OData APIs: Supplier Invoice, Purchase Order, Goods Receipt, and Cost Center.

---

## API Specifications

The following API spec files have been downloaded and must be used as input to the `mcp-translation-file` skill:

| API | ORD ID | Spec file |
|---|---|---|
| Supplier Invoice | `sap.s4:apiResource:API_SUPPLIERINVOICE_PROCESS_SRV:v1` | `api-specs/API_SUPPLIERINVOICE_PROCESS_SRV.edmx` |
| Purchase Order | `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1` | `api-specs/API_PURCHASEORDER_PROCESS_SRV.edmx` |
| Goods Receipt Confirmations | `sap.s4:apiResource:SSPOPENITMGOODSRECEIPT_0001:v1` | `api-specs/SSPOPENITMGOODSRECEIPT_0001.edmx` |
| Cost Center | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | `api-specs/CE_COSTCENTER_0001.edmx` |

## MCP Tool Scope

```
MCP API: sap.s4:apiResource:API_SUPPLIERINVOICE_PROCESS_SRV:v1
MCP tool scope: read-write
Resources in scope: A_SupplierInvoice, A_SupplierInvoiceItemGLAcct, A_SupplierInvoiceHeader
```

```
MCP API: sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1
MCP tool scope: read-only
Resources in scope: A_PurchaseOrder, A_PurchaseOrderItem
```

```
MCP API: sap.s4:apiResource:SSPOPENITMGOODSRECEIPT_0001:v1
MCP tool scope: read-only
Resources in scope: all
```

```
MCP API: sap.s4:apiResource:CE_COSTCENTER_0001:v1
MCP tool scope: read-only
Resources in scope: CostCenter, CostCenterText
```

---

## Setup

- [ ] Create asset folder `assets/blocked-invoice-s4hana-mcp-server/`
- [ ] Invoke `setup-solution` skill to scaffold the asset with `asset.yaml` — asset type: `mcp-server`
- [ ] Confirm `asset.yaml` declares `metadata.type: mcp-server` and has a valid `provides.apis[]` block with an ORD ID for this MCP server

## MCP Translation — Supplier Invoice API

- [ ] Invoke the `mcp-translation-file` skill with:
  - Input spec: `specification/blocked-invoice-s4hana-mcp-server/api-specs/API_SUPPLIERINVOICE_PROCESS_SRV.edmx`
  - API type: `edmx`
  - API ORD ID: `sap.s4:apiResource:API_SUPPLIERINVOICE_PROCESS_SRV:v1`
  - Tool scope: read-write; resources: `A_SupplierInvoice`, `A_SupplierInvoiceItemGLAcct`, `A_SupplierInvoiceHeader`
  - Key tools required: list blocked invoices (filter by payment block indicator), read invoice details, update payment block field (for auto-release and post-approval release)
- [ ] Validate generated translation file covers: listing invoices with a payment block filter, reading a single invoice's full details, and updating the payment block indicator to release an invoice

## MCP Translation — Purchase Order API

- [ ] Invoke the `mcp-translation-file` skill with:
  - Input spec: `specification/blocked-invoice-s4hana-mcp-server/api-specs/API_PURCHASEORDER_PROCESS_SRV.edmx`
  - API type: `edmx`
  - API ORD ID: `sap.s4:apiResource:API_PURCHASEORDER_PROCESS_SRV:v1`
  - Tool scope: read-only; resources: `A_PurchaseOrder`, `A_PurchaseOrderItem`
  - Key tools required: read PO header (vendor, agreed price, cost center assignment), read PO line items
- [ ] Validate generated translation file covers: retrieving a purchase order by PO number with its line items and cost center assignment

## MCP Translation — Goods Receipt API

- [ ] Invoke the `mcp-translation-file` skill with:
  - Input spec: `specification/blocked-invoice-s4hana-mcp-server/api-specs/SSPOPENITMGOODSRECEIPT_0001.edmx`
  - API type: `edmx`
  - API ORD ID: `sap.s4:apiResource:SSPOPENITMGOODSRECEIPT_0001:v1`
  - Tool scope: read-only; resources: all
  - Key tools required: check whether a goods receipt has been posted for a given PO, retrieve GR quantity and posting date
- [ ] Validate generated translation file covers: querying GR status for a PO reference

## MCP Translation — Cost Center API

- [ ] Invoke the `mcp-translation-file` skill with:
  - Input spec: `specification/blocked-invoice-s4hana-mcp-server/api-specs/CE_COSTCENTER_0001.edmx`
  - API type: `edmx`
  - API ORD ID: `sap.s4:apiResource:CE_COSTCENTER_0001:v1`
  - Tool scope: read-only; resources: `CostCenter`, `CostCenterText`
  - Key tools required: retrieve cost center master record to identify the responsible person/manager and their email address
- [ ] Validate generated translation file covers: reading a cost center record with its responsible person field

## Validation

- [ ] Confirm all four translation files are generated and valid
- [ ] Confirm `asset.yaml` for this MCP server is complete with all four API ORD IDs registered under `provides.apis[]`
- [ ] Confirm the MCP server ORD ID is noted — it will be referenced in the `requires` blocks of both the agent and the workflow asset.yamls

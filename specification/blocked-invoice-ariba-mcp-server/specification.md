# Specification: blocked-invoice-ariba-mcp-server

> **Guidelines**: Read [../guidelines.md](../guidelines.md) before executing ANY tasks below.

This asset is a custom MCP server that exposes the Ariba Contract Terms Management API to the AI agent and the n8n workflow. It enables retrieval of a supplier's contract terms during invoice enrichment.

---

## API Specifications

| API | ORD ID | Spec file |
|---|---|---|
| Contract Terms Management | `sap.aribas4:apiResource:contract_terms_management:v1` | `api-specs/contract_terms_management.json` |

## MCP Tool Scope

```
MCP API: sap.aribas4:apiResource:contract_terms_management:v1
MCP tool scope: read-only
Resources in scope: all
```

---

## Setup

- [ ] Create asset folder `assets/blocked-invoice-ariba-mcp-server/`
- [ ] Invoke `setup-solution` skill to scaffold the asset with `asset.yaml` — asset type: `mcp-server`
- [ ] Confirm `asset.yaml` declares `metadata.type: mcp-server` and has a valid `provides.apis[]` block

## MCP Translation — Ariba Contract Terms Management API

- [ ] Invoke the `mcp-translation-file` skill with:
  - Input spec: `specification/blocked-invoice-ariba-mcp-server/api-specs/contract_terms_management.json`
  - API type: `openapi-v3`
  - API ORD ID: `sap.aribas4:apiResource:contract_terms_management:v1`
  - Tool scope: read-only; resources: all
  - Key tools required: retrieve contract terms for a given supplier/vendor ID, including agreed price ranges, quantity tolerances, payment terms, and any special conditions
- [ ] Validate generated translation file covers: looking up contract terms by supplier/vendor identifier and returning price and quantity agreement details

## Validation

- [ ] Confirm the translation file is generated and valid
- [ ] Confirm `asset.yaml` is complete with the Ariba API ORD ID registered under `provides.apis[]`
- [ ] Note the MCP server ORD ID — it will be referenced in the `requires` blocks of both the agent and the workflow asset.yamls

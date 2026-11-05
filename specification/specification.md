# Specification

> **Guidelines**: Read [guidelines.md](./guidelines.md) before executing ANY tasks below.

Check off items as completed.

## Solution Setup

- [ ] Invoke `setup-solution` skill to create `solution.yaml` and all `asset.yaml` files for every asset listed below
- [ ] Validate all `asset.yaml` and `solution.yaml` files exist and are well-formed

## Asset Implementation

- [x] Execute `specification/blocked-invoice-s4hana-mcp-server/specification.md` (all items)
- [x] Execute `specification/blocked-invoice-ariba-mcp-server/specification.md` (all items)
- [x] Execute `specification/blocked-invoice-resolution-agent/specification.md` (all items)
- [x] Execute `specification/blocked-invoice-resolution-workflow/specification.md` (all items)
- [x] Cross-implementation compatibility check — verify:
  - S/4HANA MCP server ORD ID used in `asset.yaml requires` of both the agent and the workflow matches the declared ORD ID in the MCP server asset
  - Ariba MCP server ORD ID used in the agent's `asset.yaml requires` matches the Ariba MCP server asset
  - The AI agent A2A endpoint URL environment variable (`AGENT_BASE_URL`) referenced in the n8n workflow matches the agent's deployment configuration
  - Milestone log statement identifiers (M1–M6) in the agent match those defined in `product-requirements-document.md`
  - Outlook node credential references in the workflow match what is configured on the n8n instance
  - SAP Task Center node is wired with a Switch node downstream handling both approve and reject outputs

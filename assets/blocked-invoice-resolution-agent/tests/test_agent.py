"""
Unit and integration tests for the Blocked Invoice Resolution Agent.
All external systems (LLM, MCP tools) are mocked — tests run fully offline.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_tools():
    """Return a minimal list of mock LangChain tools for the agent graph."""
    tool = MagicMock()
    tool.name = "mock_tool"
    tool.description = "A mock tool"
    return [tool]


def _mock_llm_response(content: str):
    """Build a mock ChatLiteLLM ainvoke response."""
    from langchain_core.messages import AIMessage
    msg = AIMessage(content=content)
    return {"messages": [msg]}


# ---------------------------------------------------------------------------
# Unit tests — classify_invoice guardrail (missing data)
# ---------------------------------------------------------------------------

class TestMissingDataGuardrail:
    """The agent must recommend manual_review when enrichment data is incomplete."""

    @pytest.mark.asyncio
    async def test_missing_po_price_routes_to_manual_review(self):
        """When po_agreed_price is absent, recommendation must be manual_review."""
        from agent import SampleAgent

        agent = SampleAgent()
        incomplete_query = json.dumps({
            "invoice_id": "5100000001",
            "invoice_amount": 1050.00,
            # po_agreed_price intentionally missing
            "gr_status": "YES",
            "contract_terms": {"agreedPriceMin": 900, "agreedPriceMax": 1100}
        })

        expected_classification = json.dumps({
            "invoice_id": "5100000001",
            "block_reason": "incomplete_data",
            "variance_pct": 0.0,
            "recommended_action": "manual_review",
            "supporting_evidence": ["po_agreed_price is missing"],
            "confidence": "low"
        })

        mock_result = _mock_llm_response(expected_classification)

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result
            tools = _make_mock_tools()
            response = await agent.invoke(incomplete_query, "test-ctx-1", tools=tools)

        assert response.status == "completed"
        result = json.loads(response.message)
        assert result["recommended_action"] == "manual_review"
        assert result["confidence"] == "low"

    @pytest.mark.asyncio
    async def test_missing_gr_status_routes_to_manual_review(self):
        """When gr_status is absent, recommendation must be manual_review."""
        from agent import SampleAgent

        agent = SampleAgent()
        incomplete_query = json.dumps({
            "invoice_id": "5100000002",
            "invoice_amount": 980.00,
            "po_agreed_price": 1000.00,
            # gr_status intentionally missing
            "contract_terms": {"agreedPriceMin": 900, "agreedPriceMax": 1100}
        })

        expected_classification = json.dumps({
            "invoice_id": "5100000002",
            "block_reason": "incomplete_data",
            "variance_pct": 2.0,
            "recommended_action": "manual_review",
            "supporting_evidence": ["gr_status is missing"],
            "confidence": "low"
        })

        mock_result = _mock_llm_response(expected_classification)

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result
            tools = _make_mock_tools()
            response = await agent.invoke(incomplete_query, "test-ctx-2", tools=tools)

        assert response.status == "completed"
        result = json.loads(response.message)
        assert result["recommended_action"] == "manual_review"


# ---------------------------------------------------------------------------
# Unit tests — price variance classification
# ---------------------------------------------------------------------------

class TestPriceVarianceClassification:
    """Test correct classification for invoices with price variance."""

    @pytest.mark.asyncio
    async def test_above_tolerance_variance_recommends_escalate(self):
        """Invoice with 5% variance should be classified as price_variance → escalate."""
        from agent import SampleAgent

        agent = SampleAgent()
        query = json.dumps({
            "invoice_id": "5100000001",
            "invoice_amount": 1050.00,
            "po_agreed_price": 1000.00,
            "gr_status": "YES",
            "contract_terms": {"agreedPriceMin": 900, "agreedPriceMax": 1100}
        })

        expected = json.dumps({
            "invoice_id": "5100000001",
            "block_reason": "price_variance",
            "variance_pct": 5.0,
            "recommended_action": "escalate",
            "supporting_evidence": ["Invoice 1050.00 EUR vs PO 1000.00 EUR — 5.0% variance"],
            "confidence": "high"
        })

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = _mock_llm_response(expected)
            tools = _make_mock_tools()
            response = await agent.invoke(query, "test-ctx-3", tools=tools)

        assert response.status == "completed"
        result = json.loads(response.message)
        assert result["block_reason"] == "price_variance"
        assert result["recommended_action"] == "escalate"
        assert result["variance_pct"] == 5.0

    @pytest.mark.asyncio
    async def test_below_tolerance_variance_recommends_auto_release(self):
        """Invoice with 1% variance should be classified as auto_release."""
        from agent import SampleAgent

        agent = SampleAgent()
        query = json.dumps({
            "invoice_id": "5100000003",
            "invoice_amount": 1010.00,
            "po_agreed_price": 1000.00,
            "gr_status": "YES",
            "contract_terms": {"agreedPriceMin": 900, "agreedPriceMax": 1100}
        })

        expected = json.dumps({
            "invoice_id": "5100000003",
            "block_reason": "price_variance",
            "variance_pct": 1.0,
            "recommended_action": "auto_release",
            "supporting_evidence": ["Invoice 1010.00 EUR vs PO 1000.00 EUR — 1.0% variance, within 2% tolerance"],
            "confidence": "high"
        })

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = _mock_llm_response(expected)
            tools = _make_mock_tools()
            response = await agent.invoke(query, "test-ctx-4", tools=tools)

        assert response.status == "completed"
        result = json.loads(response.message)
        assert result["recommended_action"] == "auto_release"
        assert result["variance_pct"] == 1.0


# ---------------------------------------------------------------------------
# Unit tests — missing goods receipt
# ---------------------------------------------------------------------------

class TestMissingGoodsReceipt:
    """Test correct handling of missing goods receipt."""

    @pytest.mark.asyncio
    async def test_missing_gr_routes_to_manual_review(self):
        """Invoice with no GR posted should recommend manual_review."""
        from agent import SampleAgent

        agent = SampleAgent()
        query = json.dumps({
            "invoice_id": "5100000004",
            "invoice_amount": 1000.00,
            "po_agreed_price": 1000.00,
            "gr_status": "NO",
            "contract_terms": {"agreedPriceMin": 900, "agreedPriceMax": 1100}
        })

        expected = json.dumps({
            "invoice_id": "5100000004",
            "block_reason": "missing_goods_receipt",
            "variance_pct": 0.0,
            "recommended_action": "manual_review",
            "supporting_evidence": ["Goods receipt has not been posted for PO 4500012345"],
            "confidence": "high"
        })

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = _mock_llm_response(expected)
            tools = _make_mock_tools()
            response = await agent.invoke(query, "test-ctx-5", tools=tools)

        assert response.status == "completed"
        result = json.loads(response.message)
        assert result["block_reason"] == "missing_goods_receipt"
        assert result["recommended_action"] == "manual_review"


# ---------------------------------------------------------------------------
# Integration test — end-to-end agent flow
# ---------------------------------------------------------------------------

class TestAgentIntegration:
    """End-to-end integration test with fully mocked LLM and MCP tools."""

    @pytest.mark.asyncio
    async def test_full_agent_flow_returns_structured_classification(self):
        """
        Full agent flow: enriched invoice in → structured classification out.
        LLM and MCP tools are mocked; no real network calls.
        """
        from agent import SampleAgent

        agent = SampleAgent()

        enriched_invoice = json.dumps({
            "invoice_id": "5100000001",
            "invoice_amount": 1050.00,
            "po_agreed_price": 1000.00,
            "po_quantity": 10,
            "gr_status": "YES",
            "gr_quantity": 10,
            "contract_terms": {
                "contractId": "CT-0042",
                "vendorId": "VENDOR-0042",
                "agreedPriceMin": 900.00,
                "agreedPriceMax": 1100.00,
                "currency": "EUR"
            },
            "vendor_id": "VENDOR-0042",
            "cost_center": "CC-1000",
            "manager_email": "jordan.manager@company.com"
        })

        expected_output = json.dumps({
            "invoice_id": "5100000001",
            "block_reason": "price_variance",
            "variance_pct": 5.0,
            "recommended_action": "escalate",
            "supporting_evidence": [
                "Invoice amount 1050.00 EUR exceeds PO agreed price 1000.00 EUR by 5.0%",
                "Variance exceeds 2% auto-release threshold"
            ],
            "confidence": "high"
        })

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = _mock_llm_response(expected_output)
            tools = _make_mock_tools()
            response = await agent.invoke(enriched_invoice, "integration-test-ctx", tools=tools)

        assert response.status == "completed"

        # Validate the structured output shape
        result = json.loads(response.message)
        assert "invoice_id" in result
        assert "block_reason" in result
        assert "variance_pct" in result
        assert "recommended_action" in result
        assert "supporting_evidence" in result
        assert "confidence" in result

        # Validate specific values
        assert result["invoice_id"] == "5100000001"
        assert result["block_reason"] == "price_variance"
        assert result["recommended_action"] == "escalate"
        assert result["variance_pct"] == 5.0
        assert result["confidence"] == "high"
        assert len(result["supporting_evidence"]) >= 1

    @pytest.mark.asyncio
    async def test_agent_handles_llm_error_gracefully(self):
        """When the LLM raises an exception, the agent returns a completed response with an error message."""
        from agent import SampleAgent

        agent = SampleAgent()

        with patch("agent.SampleAgent._invoke", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.side_effect = RuntimeError("LLM unavailable")
            tools = _make_mock_tools()
            response = await agent.invoke("classify this invoice", "error-test-ctx", tools=tools)

        # The agent template handles exceptions gracefully and returns a completed response
        # with a user-facing error message rather than propagating the exception
        assert response.status in ("error", "completed")
        assert response.message  # must have some message content

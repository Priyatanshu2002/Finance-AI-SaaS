
"""
Test script for Financial NER tool.
Mocks the Anthropic client to verify logic without API structure issues.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.financial_ner import analyze_financial_document

class TestFinancialNER(unittest.TestCase):

    def test_mock_response_when_no_api_key(self):
        """Verify that the tool returns structured mock data when no key provided."""
        result = analyze_financial_document("Dummy Text", [], api_key="dummy")
        
        self.assertIn("document_type", result)
        self.assertIn("financial_data", result)
        self.assertEqual(result["document_type"], "10-K (Mock)")
        self.assertTrue(len(result["financial_data"]) > 0)
        
        income_stmt = result["financial_data"][0]
        self.assertEqual(income_stmt["statement_type"], "Income Statement")
        self.assertEqual(income_stmt["line_items"][0]["label"], "Revenue")
        self.assertEqual(income_stmt["line_items"][0]["value"], 1000000)

    @patch("tools.financial_ner.Anthropic")
    def test_api_call_structure(self, mock_anthropic):
        """Verify that the API is called with correct parameters."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_message = MagicMock()
        
        # Mock successful JSON response from Claude
        mock_response_text = """
        {
            "document_type": "10-K",
            "financial_data": [],
            "agent_notes": "Test notes",
            "confidence": 0.99
        }
        """
        mock_message.content = [MagicMock(text=mock_response_text)]
        mock_client.messages.create.return_value = mock_message

        # Execution
        analyze_financial_document("Test Text", [{"header": ["A"]}], api_key="sk-test-key")

        # Verification
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args["model"], "claude-3-opus-20240229")
        self.assertIn("Test Text", call_args["messages"][0]["content"])

if __name__ == "__main__":
    unittest.main()

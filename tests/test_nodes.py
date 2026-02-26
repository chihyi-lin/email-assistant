import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from src.graph import GraphCompiler
from src.nodes import Nodes

# mock state
@pytest.fixture
def initial_state():
    return {"emails": [],
            "current_email": None,
            "category": "",
            "drafted_subject": "",
            "drafted_body": "",
            "summarization": "",
            "error": "",
            "current_log": ""}

@pytest.fixture
def mock_email():
    """Create a mock email object"""
    email = Mock()
    email.body = "Can you provide an update on the project status?"
    email.subject = "Project Update Request"
    email.sender = "boss@company.com"
    return email

@pytest.mark.unit
class TestCategorizeEmailNode:
    """Test the categorize_email node implementation"""
    def test_categorize_email_with_mocked_llm(self, initial_state, mock_email):
        # Setup state with current email
        state = initial_state.copy()
        state["current_email"] = mock_email

        # Mock the agent's categorize_email invoke method
        with patch.object(Nodes, '__init__', lambda self: None):  # Skip Nodes.__init__
            nodes = Nodes()
            # Mock the agent attribute
            nodes.agent = Mock()
            mock_category_result = Mock()
            mock_category_result.category = "response_required"
            nodes.agent.categorize_email.invoke.return_value = mock_category_result

            # Call the actual function
            result = nodes.categorize_email(state)

            # Test YOUR function's behavior
            assert result["category"] == "response_required"
            assert "Category: response_required" in result["current_log"]
            assert "error" not in result

            # Verify the agent was called once and called with "email_content" argument
            nodes.agent.categorize_email.invoke.assert_called_once()
            call_args = nodes.agent.categorize_email.invoke.call_args[0][0]
            assert "email_content" in call_args

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

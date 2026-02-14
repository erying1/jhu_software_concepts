# tests/test_clean_errors.py

from unittest.mock import patch, Mock

def test_llm_clean_batch_api_error():
    """Test LLM cleaning when API returns error."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [
        {"program": "Unknown Prog", "entry_url": "http://test1.com"},
        {"program": "Mystery U", "entry_url": "http://test2.com"}
    ]
    
    # Patch where it's imported in the clean module
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        # Should return original records on error
        result = llm_clean_batch(records)
        
        assert len(result) == 2
        assert result[0]["program"] == "Unknown Prog"


def test_llm_clean_batch_invalid_json_response():
    """Test LLM cleaning with invalid JSON in response."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test U", "entry_url": "http://test.com"}]
    
    # Patch where it's imported in the clean module
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        
        # Create proper mock text block
        mock_text_block = Mock()
        mock_text_block.text = "Invalid JSON {{{ not parseable"
        mock_message.content = [mock_text_block]
        
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        # Should handle gracefully
        result = llm_clean_batch(records)
        
        # Should return original or handle error
        assert isinstance(result, list)
        assert len(result) >= 1


def test_clean_data_with_empty_list():
    """Test clean_data with empty input."""
    from src.module_2_1.clean import clean_data
    
    # Test with empty list
    result = clean_data([])
    
    assert result == []


def test_normalize_status_edge_cases():
    """Test normalize_status with unusual inputs."""
    from src.module_2_1.clean import normalize_status
    
    # Test with variations that should normalize
    assert normalize_status("Accepted!") == "Accepted"
    assert normalize_status("rejected ") == "Rejected"
    assert normalize_status("WAITLISTED") == "Waitlisted"
    
    # Test with None
    result = normalize_status(None)
    assert result is None or result == "Other"

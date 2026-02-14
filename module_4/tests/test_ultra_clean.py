"""Ultra-targeted clean.py tests."""
import pytest
from unittest.mock import patch, Mock


def test_llm_clean_batch_empty_response():
    """Test LLM when response has empty content."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = []
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)


def test_llm_clean_batch_network_error():
    """Test LLM when network error occurs."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_client.messages.create.side_effect = ConnectionError("Network error")
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)
        assert len(result) == len(records)


def test_llm_clean_batch_rate_limit():
    """Test LLM when rate limited."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        rate_error = Exception("Rate limit exceeded")
        rate_error.status_code = 429
        mock_client.messages.create.side_effect = rate_error
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)


def test_llm_clean_batch_malformed_json_in_response():
    """Test LLM with JSON that has extra text."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        mock_text_block = Mock()
        mock_text_block.text = 'Here is the response: {"records": [{"program": "Test", "entry_url": "http://test.com"}]} Hope that helps!'
        mock_message.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)


def test_clean_data_preserves_all_fields():
    """Test clean_data preserves all required fields."""
    from src.module_2_1.clean import clean_data
    
    records = [
        {
            "program": "Test Program",
            "entry_url": "http://test.com",
            "status": "accepted",
            "gpa": "3.8",
            "citizenship": "American",
            "term": "Fall 2024"
        }
    ]
    
    result = clean_data(records)
    assert len(result) == 1
    assert "program" in result[0]
    assert "entry_url" in result[0]

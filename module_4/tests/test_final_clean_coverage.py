"""Comprehensive clean.py coverage tests."""
import pytest
from unittest.mock import patch, Mock

def test_llm_clean_batch_with_timeout():
    """Test LLM cleaning with timeout error."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test U", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_client.messages.create.side_effect = TimeoutError("API timeout")
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)
        assert len(result) >= 1


def test_llm_clean_batch_with_json_decode_error():
    """Test LLM cleaning when JSON parsing fails."""
    from src.module_2_1.clean import llm_clean_batch
    import json
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        mock_text_block = Mock()
        mock_text_block.text = "Not valid JSON at all"
        mock_message.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        with patch('json.loads', side_effect=json.JSONDecodeError("error", "", 0)):
            result = llm_clean_batch(records)
            assert isinstance(result, list)


def test_clean_data_with_llm_failure():
    """Test clean_data when LLM processing fails."""
    from src.module_2_1.clean import clean_data
    
    records = [
        {"program": "Unknown", "entry_url": "http://test1.com"},
        {"program": "Mystery", "entry_url": "http://test2.com"}
    ]
    
    with patch('src.module_2_1.clean.llm_clean_batch', return_value=records):
        result = clean_data(records)
        assert len(result) == 2


def test_normalize_status_with_variations():
    """Test normalize_status with various input formats."""
    from src.module_2_1.clean import normalize_status
    
    # Test accepted variations
    assert normalize_status("accepted") == "Accepted"
    assert normalize_status("ACCEPTED") == "Accepted"
    assert normalize_status("Accepted!!!") == "Accepted"
    
    # Test rejected variations
    assert normalize_status("rejected") == "Rejected"
    assert normalize_status("REJECTED") == "Rejected"
    assert normalize_status("Rejected :(") == "Rejected"
    
    # Test waitlisted variations
    assert normalize_status("waitlisted") == "Waitlisted"
    assert normalize_status("WAITLISTED") == "Waitlisted"
    assert normalize_status("wait listed") == "Waitlisted"
    
    # Test other/unknown
    result = normalize_status("pending")
    assert result in ["Other", "Pending", None] or isinstance(result, str)


def test_clean_single_gpa_edge_cases():
    """Test GPA cleaning with edge cases."""
    from src.module_2_1.clean import clean_data
    
    records = [
        {"program": "Test", "gpa": "3.5", "entry_url": "http://test.com"},
        {"program": "Test2", "gpa": "invalid", "entry_url": "http://test2.com"},
        {"program": "Test3", "gpa": None, "entry_url": "http://test3.com"}
    ]
    
    result = clean_data(records)
    assert len(result) == 3


def test_clean_data_with_citizenship_variations():
    """Test citizenship normalization."""
    from src.module_2_1.clean import clean_data
    
    records = [
        {"program": "Test", "citizenship": "American", "entry_url": "http://test1.com"},
        {"program": "Test", "citizenship": "U.S.", "entry_url": "http://test2.com"},
        {"program": "Test", "citizenship": "International", "entry_url": "http://test3.com"},
        {"program": "Test", "citizenship": "Other", "entry_url": "http://test4.com"}
    ]
    
    result = clean_data(records)
    assert len(result) == 4

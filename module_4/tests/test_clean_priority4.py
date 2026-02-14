# test_clean_priority4.py

from unittest.mock import patch, Mock, MagicMock, PropertyMock

def test_llm_clean_batch_content_extraction_error():
    """Test LLM when content extraction fails."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        
        # Content exists but accessing .text raises
        mock_content_item = Mock()
        mock_content_item.text = PropertyMock(side_effect=AttributeError("No text"))
        mock_message.content = [mock_content_item]
        
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)


def test_llm_clean_batch_json_extraction_from_markdown():
    """Test LLM when response has JSON in markdown code blocks."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        mock_text_block = Mock()
        
        # JSON wrapped in markdown
        mock_text_block.text = '''
Here is the cleaned data:

```json
{
  "records": [
    {"program": "Test University", "entry_url": "http://test.com"}
  ]
}
```

Hope this helps!
        '''
        
        mock_message.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        result = llm_clean_batch(records)
        assert isinstance(result, list)


def test_llm_clean_batch_with_partial_json():
    """Test LLM when JSON is truncated or incomplete."""
    from src.module_2_1.clean import llm_clean_batch
    
    records = [{"program": "Test", "entry_url": "http://test.com"}]
    
    with patch('src.module_2_1.clean.anthropic.Anthropic') as mock_anthropic:
        with patch('src.module_2_1.clean.json.loads') as mock_json_loads:
            mock_client = Mock()
            mock_message = Mock()
            mock_text_block = Mock()
            mock_text_block.text = '{"records": [{"program": "Test", "entry_url": '
            mock_message.content = [mock_text_block]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client
            
            # Make json.loads raise on incomplete JSON
            mock_json_loads.side_effect = ValueError("Incomplete JSON")
            
            result = llm_clean_batch(records)
            assert isinstance(result, list)
            assert len(result) == len(records)

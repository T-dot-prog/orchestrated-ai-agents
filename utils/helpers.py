"""
Helper utilities for the AI Agent Orchestration System.
"""
import json
import re
from typing import Any, Dict, List, Optional

def format_agent_response(
    success: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format agent response in a standardized way.
    
    Args:
        success (bool): Whether the agent operation was successful
        data (Optional[Dict[str, Any]]): Response data if successful
        error (Optional[str]): Error message if unsuccessful
    
    Returns:
        Dict[str, Any]: Formatted response
    """
    response = {
        "success": success,
        "data": data or {},
        "error": error
    }
    return response

def validate_json(data: str) -> Dict[str, Any]:
    """
    Validate and parse JSON string.
    
    Args:
        data (str): JSON string to validate
    
    Returns:
        Dict[str, Any]: Parsed JSON data
        
    Raises:
        ValueError: If JSON is invalid
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")

def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Split text into chunks of specified size.
    
    Args:
        text (str): Text to split
        chunk_size (int): Maximum size of each chunk
    
    Returns:
        List[str]: List of text chunks
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1 (Dict[str, Any]): First dictionary
        dict2 (Dict[str, Any]): Second dictionary
    
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    merged = dict1.copy()
    
    for key, value in dict2.items():
        if (
            key in merged and 
            isinstance(merged[key], dict) and 
            isinstance(value, dict)
        ):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    
    return merged

def convert_str_to_list(results: str) -> list[dict[str, Any]]:
    """
    Function for converting string text into listed dictionary
    Args:
        - results: str = The Text input
    Returns:
        - list[dict[str, Any]] = A listed dictionary
    """
    
    try:
        output = []

        entries = results.split("snippet:")[1:]

        for entry in entries:
            snippet_match = re.search(r'^(.*?)(?:,\s*title:)', entry, re.DOTALL)
            snippet = snippet_match.group(1).strip() if snippet_match else ""
            
            # Extract link (look for 'link:' followed by URL)
            link_match = re.search(r'link:\s*(https?://[^\s,]+)', entry)
            link = link_match.group(1).strip() if link_match else ""
            
            output.append({
                'snippet': snippet,
                'link': link
            })

        return output
    
    except Exception as e:
        print(f'Convertion failed: {e}')
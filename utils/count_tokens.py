#!/usr/bin/env python
# coding: utf-8

"""
Token counting utilities using tiktoken.

This module provides functions to count tokens for various OpenAI API inputs:
- Simple text strings
- Chat completion messages
- Function calls and tools
"""

import tiktoken
from typing import List, Dict, Any, Optional


def num_tokens_from_string(string: str, encoding_name: str = "o200k_base") -> int:
    """
    Returns the number of tokens in a text string.
    
    Args:
        string: The text string to count tokens for
        encoding_name: The encoding to use (default: "o200k_base" for gpt-4o models)
        
    Returns:
        Number of tokens in the string
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_string_by_model(string: str, model: str = "gpt-4o-mini") -> int:
    """
    Returns the number of tokens in a text string for a specific model.
    
    Args:
        string: The text string to count tokens for
        model: The model name to get the correct encoding for
        
    Returns:
        Number of tokens in the string
    """
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_messages(messages: List[Dict[str, Any]], model: str = "gpt-4o-mini") -> int:
    """
    Return the number of tokens used by a list of messages.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The model name to calculate tokens for
        
    Returns:
        Total number of tokens for the messages
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06"
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0125.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0125")
    elif "gpt-4o-mini" in model:
        print("Warning: gpt-4o-mini may update over time. Returning num tokens assuming gpt-4o-mini-2024-07-18.")
        return num_tokens_from_messages(messages, model="gpt-4o-mini-2024-07-18")
    elif "gpt-4o" in model:
        print("Warning: gpt-4o may update over time. Returning num tokens assuming gpt-4o-2024-08-06.")
        return num_tokens_from_messages(messages, model="gpt-4o-2024-08-06")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}."
        )
    
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def num_tokens_for_tools(functions: List[Dict[str, Any]], messages: List[Dict[str, Any]], model: str) -> int:
    """
    Calculate total tokens for messages that contain function/tool calls.
    
    Args:
        functions: List of function definitions
        messages: List of message dictionaries
        model: The model name to calculate tokens for
        
    Returns:
        Total number of tokens including function definitions and messages
    """
    # Initialize function settings to 0
    func_init = 0
    prop_init = 0
    prop_key = 0
    enum_init = 0
    enum_item = 0
    func_end = 0
    
    if model in ["gpt-4o", "gpt-4o-mini"]:
        # Set function settings for the above models
        func_init = 7
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    elif model in ["gpt-3.5-turbo", "gpt-4"]:
        # Set function settings for the above models
        func_init = 10
        prop_init = 3
        prop_key = 3
        enum_init = -3
        enum_item = 3
        func_end = 12
    else:
        raise NotImplementedError(
            f"num_tokens_for_tools() is not implemented for model {model}."
        )
    
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using o200k_base encoding.")
        encoding = tiktoken.get_encoding("o200k_base")
    
    func_token_count = 0
    if len(functions) > 0:
        for f in functions:
            func_token_count += func_init  # Add tokens for start of each function
            function = f["function"]
            f_name = function["name"]
            f_desc = function["description"]
            if f_desc.endswith("."):
                f_desc = f_desc[:-1]
            line = f_name + ":" + f_desc
            func_token_count += len(encoding.encode(line))  # Add tokens for set name and description
            if len(function["parameters"]["properties"]) > 0:
                func_token_count += prop_init  # Add tokens for start of each property
                for key in list(function["parameters"]["properties"].keys()):
                    func_token_count += prop_key  # Add tokens for each set property
                    p_name = key
                    p_type = function["parameters"]["properties"][key]["type"]
                    p_desc = function["parameters"]["properties"][key]["description"]
                    if "enum" in function["parameters"]["properties"][key].keys():
                        func_token_count += enum_init  # Add tokens if property has enum list
                        for item in function["parameters"]["properties"][key]["enum"]:
                            func_token_count += enum_item
                            func_token_count += len(encoding.encode(item))
                    if p_desc.endswith("."):
                        p_desc = p_desc[:-1]
                    line = f"{p_name}:{p_type}:{p_desc}"
                    func_token_count += len(encoding.encode(line))
        func_token_count += func_end
        
    messages_token_count = num_tokens_from_messages(messages, model)
    total_tokens = messages_token_count + func_token_count
    
    return total_tokens


def compare_encodings(example_string: str) -> None:
    """
    Prints a comparison of different string encodings.
    
    Args:
        example_string: The string to compare across different encodings
    """
    print(f'\nExample string: "{example_string}"')
    # for each encoding, print the # of tokens, the token integers, and the token bytes
    for encoding_name in ["r50k_base", "p50k_base", "cl100k_base", "o200k_base"]:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(example_string)
        num_tokens = len(token_integers)
        token_bytes = [encoding.decode_single_token_bytes(token) for token in token_integers]
        print()
        print(f"{encoding_name}: {num_tokens} tokens")
        print(f"token integers: {token_integers}")
        print(f"token bytes: {token_bytes}")


def estimate_cost(num_tokens: int, model: str = "gpt-4o-mini", request_type: str = "input") -> float:
    """
    Estimate the cost for a given number of tokens based on OpenAI pricing.
    
    Args:
        num_tokens: Number of tokens
        model: Model name
        request_type: "input" or "output" for different pricing tiers
        
    Returns:
        Estimated cost in USD
        
    Note: Pricing may change. This is for estimation purposes only.
    """
    # Pricing per 1M tokens (as of late 2024 - may need updates)
    pricing = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }
    
    if model not in pricing:
        print(f"Warning: Pricing not available for model {model}")
        return 0.0
    
    if request_type not in pricing[model]:
        print(f"Warning: Request type {request_type} not available for model {model}")
        return 0.0
    
    cost_per_million = pricing[model][request_type]
    estimated_cost = (num_tokens / 1_000_000) * cost_per_million
    
    return estimated_cost


# Example usage and testing functions
if __name__ == "__main__":
    # Test basic string counting
    test_string = "Hello, how are you doing today?"
    print(f"String: '{test_string}'")
    print(f"Tokens (o200k_base): {num_tokens_from_string(test_string)}")
    print(f"Tokens (gpt-4o-mini): {num_tokens_from_string_by_model(test_string, 'gpt-4o-mini')}")
    
    # Test message counting
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]
    print(f"\nMessage tokens: {num_tokens_from_messages(test_messages)}")
    
    # Test encoding comparison
    compare_encodings("Hello world!")
    
    # Test cost estimation
    tokens = 1000
    cost = estimate_cost(tokens, "gpt-4o-mini", "input")
    print(f"\nEstimated cost for {tokens} tokens: ${cost:.6f}")

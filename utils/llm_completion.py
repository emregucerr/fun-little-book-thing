import os
import time
from typing import Optional
from litellm import Router
from litellm.exceptions import RateLimitError, APIError, Timeout

model_list = [
    {
        "model_name": "claude-4-sonnet",
        "litellm_params": {
            "model": "bedrock/us.anthropic.claude-sonnet-4-20250514-v1:0",
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_KEY"),
            "model_id": "arn:aws:bedrock:us-west-2:533266980225:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0",
            "tpm":2000000
        }
    },
    {
        "model_name": "claude-3-5-sonnet",
        "litellm_params": {
            "model": "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_KEY"),
            "model_id": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
            "tpm":2000000
        },
    },
    {
        "model_name": "claude-3-5-haiku",
        "litellm_params": {
            "model": "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0",
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_KEY"),
            "model_id": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0",
            "tpm":2000000
        }
    },
    {
        "model_name": "gpt-4o",
        "litellm_params": {
            "model": "azure/gpt-4o",
        }
    },
    {
        "model_name": "gpt-4o-openai", 
        "litellm_params": {
            "model": "openai/gpt-4o", 
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_base": os.getenv("OPENAI_BASE_URL")
        }
    },
    {
        "model_name": "gpt-4o-mini", 
        "litellm_params": {
            "model": "openai/gpt-4o-mini", 
            "api_key": os.getenv("OPENAI_API_KEY"),
            "max_tokens": 16_384
        }
    }, {
        "model_name": "o1-mini",
        "litellm_params": {
            "model": "openai/o1-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    }, {
        "model_name": "o1",
        "litellm_params": {
            "model": "openai/o1",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    }, {
        "model_name": "gemini-1.5-pro",
        "litellm_params": {
            "model": "gemini/gemini-1.5-pro-002",
            "api_key": os.getenv("GEMINI_API_KEY"),
        }
    },
    {
        "model_name": "gemini-exp-1206",
        "litellm_params": {
            "model": "gemini/gemini-exp-1206",
            "api_key": os.getenv("GEMINI_API_KEY"),
        }
    },
    {
        "model_name": "gemini-2.0-flash-thinking-exp-01-21",
        "litellm_params": {
            "model": "gemini/gemini-2.0-flash-thinking-exp-01-21",
            "api_key": os.getenv("GEMINI_API_KEY"),
        }
    },
    {
        "model_name": "claude-3-5-sonnet-vertex",
        "litellm_params": {
            "model": "vertex_ai/claude-3-5-sonnet-v2@20241022",
            "vertex_credentials": os.getenv("GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON"),
            'vertex_location': "us-east5"
        }
    },
    {
        "model_name": "gemini-2.0-flash-exp-01-21",
        "litellm_params": {
            "model": "gemini/gemini-2.0-flash-exp-01-21",
            "api_key": os.getenv("GEMINI_API_KEY"),
        }
    },
    {
        "model_name": "gemini-2.5-flash-preview-05-20",
        "litellm_params": {
            "model": "gemini/gemini-2.5-flash-preview-05-20",
            "api_key": os.getenv("GEMINI_API_KEY"),
        }
    },
    {
        "model_name": "text-embedding-3-small",
        "litellm_params": {
            "model": "openai/text-embedding-3-small",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "text-embedding-3-large",
        "litellm_params": {
            "model": "openai/text-embedding-3-large",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "o3-mini",
        "litellm_params": {
            "model": "openai/o3-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "o3-mini-high",
        "litellm_params": {
            "model": "openai/o3-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "reasoning_effort": "high"
        }
    },
    {
        "model_name": "gemini-2.0-pro",
        "litellm_params": {
            "model": "vertex_ai/gemini-2.0-pro-exp-02-05",
            "vertex_credentials": os.getenv("GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON"),
            "vertex_project": os.getenv("GCP_PROJECT_ID"),
            "vertex_location": "us-east5"
        }
    },
    {
        "model_name": "deepseek-v3",
        "litellm_params": {
            "model": "deepseek/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        }
    },
    {
        "model_name": "deepseek-r1",
        "litellm_params": {
            "model": "deepseek/deepseek-reasoner",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
        }
    },
    {
        "model_name": "llama4-maverick",
        "litellm_params": {
            "model": "openrouter/meta-llama/llama-4-maverick",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
        }
    },
    {
        "model_name": "gpt-4.1",
        "litellm_params": {
            "model": "azure/gpt-4.1",
        }
    },
    {
        "model_name": "gpt-4.1-openai",
        "litellm_params": {
            "model": "openai/gpt-4.1",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "gpt-4.1-mini",
        "litellm_params": {
            "model": "azure/gpt-4.1-mini",
        }
    },
    {
        "model_name": "gpt-4.1-mini-openai",
        "litellm_params": {
            "model": "openai/gpt-4.1-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "o4-mini",
        "litellm_params": {
            "model": "azure/o4-mini"
        }
    },
    {
        "model_name": "o4-mini-openai",
        "litellm_params": {
            "model": "openai/o4-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "computer-use",
        "litellm_params": {
            "model": "openai/computer-use-preview",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    },
    {
        "model_name": "sonar-pro",
        "litellm_params": {
            "model": "perplexity/sonar-pro",
            "api_key": os.getenv("PERPLEXITY_API_KEY"),
        }
    },
    {
        "model_name": "gpt-5",
        "litellm_params": {
            "model": "azure/gpt-5",
            "api_key": os.getenv("AZURE_API_KEY"),
            "api_base": os.getenv("AZURE_API_BASE"),
            "api_version": os.getenv("AZURE_API_VERSION"),
        }
    }
]

model_capabilities = {
    "gpt-5": {
        "api_format": "openai",
        "context_window": 400000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": True,
    },
    "computer-use": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
    },
    "claude-4-sonnet": {
        "api_format": "anthropic",
        "context_window": 200000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": False
    },
    "claude-3-5-sonnet": {
        "api_format": "anthropic",
        "context_window": 200000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": False
    },
    "gpt-4o": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "gpt-4o-mini": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
    },
    "o1-mini": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": False,
        "vision": False,
        "reasoning": True
    },
    "o1": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": False,
        "vision": True,
        "reasoning": True
    },
    "gemini-1.5-pro": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "claude-3-5-haiku": {
        "api_format": "anthropic",
        "context_window": 200000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "gemini-exp-1206": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "gemini-2.0-flash-thinking-exp-01-21": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "gemini-2.0-flash-exp-01-21": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "gemini-2.5-flash-preview-05-20": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": False,
        "cache_control": True
    },
    "o3-mini": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": False,
        "reasoning": True
    },
    "o3-mini-high": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": False,
        "reasoning": True
    },
    "gemini-2.0-pro":{
        "api_format":"openai",
        "context_window":2000000,
        "support_streaming":False,
        "vision":True,
        "reasoning":False
    },
    "deepseek-v3": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": False,
        "reasoning": False
    },
    "deepseek-r1": {
        "api_format": "openai",
        "context_window": 128000,
        "supports_streaming": True,
        "vision": False,
        "reasoning": True
    },
    "llama4-maverick": {
        "api_format": "openai",
        "context_window": 1000000,
        "supports_streaming": False,
        "vision": True,
        "reasoning": False
    },
    "gpt-4.1": {
        "api_format": "openai",
        "context_window": 1000000,
        "supports_streaming": True,
        "vision": True,
    },
    "gpt-4.1-mini": {
        "api_format": "openai",
        "context_window": 1000000,
        "supports_streaming": True,
        "vision": True,
    },
    "o4-mini": {
        "api_format": "openai",
        "context_window": 200000,
        "supports_streaming": True,
        "vision": True,
        "reasoning": True
    }
}

fallbacks = [
    {"claude-4-sonnet": ["claude-3-5-sonnet"]},
    {"claude-3-5-sonnet": ["gpt-4.1"]},
    {"claude-3-5-haiku": ["gpt-4.1-mini"]},
    {"gpt-4o": ["claude-3-5-haiku"]},
    {"gpt-4o-mini": ["gemini-1.5-pro"]},
    {"o1-mini": ["deepseek-v3"]},
    {"o1": ["deepseek-v3"]},
    {"o3-mini": ["deepseek-v3"]},
    {"deepseek-v3": ["gpt-4o"]},
    {"deepseek-r1": ["deepseek-v3"]},
    {"llama4-maverick": ["claude-3-5-sonnet"]},
    {"gpt-4.1": ["gpt-4o"]},
    {"gpt-4.1-openai": ["gpt-4o"]},
    {"gpt-4.1-mini": ["gpt-4o-mini"]},
    {"o4-mini": ["o4-mini-openai"]},
    {"gemini-2.5-flash-preview-05-20": ["gemini-2.0-flash-exp-01-21"]},
    {"gemini-2.0-flash-exp-01-21": ["gpt-4.1"]},
    {"sonar-pro": ["gpt-4o"]},
    {"gpt-5": ["claude-4-sonnet"]},
]

context_window_fallbacks = [
    {"claude-4-sonnet": ["gemini-1.5-pro"]},
    {"claude-3-5-sonnet": ["gemini-1.5-pro"]},
    {"gpt-4o": ["gemini-1.5-pro"]},
    {"gpt-4o-mini": ["gemini-1.5-pro"]},
    {"o1-mini": ["gemini-1.5-pro"]},
    {"o1": ["gemini-1.5-pro"]},
    {"o3-mini": ["gemini-1.5-pro"]},
    {"deepseek-v3": ["gpt-4o"]},
    {"deepseek-r1": ["gpt-4o"]},
    {"sonar-pro": ["gpt-4o"]},
    {"gpt-5": ["claude-4-sonnet"]},
]

router = Router(
    model_list=model_list,
    allowed_fails=1,
    cooldown_time=60,
    fallbacks=fallbacks,
    context_window_fallbacks=context_window_fallbacks
)

def llm_completion(
    model_name: str, 
    messages: list[dict], 
    timeout: int = 60,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> str:
    """
    Complete a chat completion with timeout and retry mechanism.
    
    Args:
        model_name: Name of the model to use
        messages: List of message dictionaries
        timeout: Timeout in seconds for the API call
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        
    Returns:
        The completion content as a string
        
    Raises:
        Exception: If all retries are exhausted or an unrecoverable error occurs
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            response = router.completion(
                model=model_name,
                messages=messages,
                stream=False,
                timeout=timeout
            )
            
            # Handle different response types
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content
                    if content is not None:
                        return content
                    else:
                        raise ValueError("Response content is None")
                else:
                    raise ValueError("Invalid response structure: no message or content")
            else:
                raise ValueError("Invalid response structure: no choices")
                
        except (RateLimitError, APIError, Timeout, Exception) as e:
            last_exception = e
            
            if attempt == max_retries:
                break
                
            # Calculate delay with exponential backoff
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
    
    # If we get here, all retries failed
    raise Exception(f"All {max_retries + 1} attempts failed. Last error: {str(last_exception)}")

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Which model are you?"}
    ]
    print(llm_completion("sonar-pro", messages))
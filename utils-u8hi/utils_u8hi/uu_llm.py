"""
create LLM chat client from model_name
"""
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient

CHAT_CLIENT_MAPPINGS = {
    # Agno framework
    "agno": {
        "openai": {
            "class": OpenAIChat, 
            "model_id": "id",
        },
        "ollama": {
            "class": Ollama, 
            "model_id": "id",
        },
    },
    # autogen/Magnetic-one framework
    "magnetic-one": {
        "openai": {
            "class": OpenAIChatCompletionClient, 
            "model_id": "model",
        },
        "ollama": {
            "class": OllamaChatCompletionClient, 
            "model_id": "model",
        },
    },
}

LLM_PROVIDER_MAP = {
    "qwen": "ollama",
    "gpt": "openai",
}

def resolve_llm_provider(model_name: str):
    """
    Lookup provider name based on model prefix with help of LLM_PROVIDER_MAP
    """
    for prefix, provider in LLM_PROVIDER_MAP.items():
        if model_name.startswith(prefix):
            return provider
    # Default case or raise exception
    raise ValueError(f"Unknown model provider for model: {model_name}")

def create_chat_client(model_name: str, agent_framework: str = "agno", **kwargs):
    """
    Instantiate LLM chat client based on agent framework and model
    
    Args:
        model_name: Name/ID of the model
        agent_framework: Framework to use (agno, magnetic-one)
        **kwargs: Additional parameters to pass to the client constructor
        
    Returns:
        Instantiated chat client
    """
    # Resolve the provider from the model name
    llm_provider = resolve_llm_provider(model_name)
    
    # Get the appropriate client configuration
    if agent_framework not in CHAT_CLIENT_MAPPINGS:
        raise ValueError(f"Unknown agent framework: {agent_framework}")
    
    provider_map = CHAT_CLIENT_MAPPINGS[agent_framework]
    if llm_provider not in provider_map:
        raise ValueError(f"Provider {llm_provider} not supported for agent framework {agent_framework}")
    
    client_config = provider_map[llm_provider]
    client_class = client_config["class"]
    
    # Map the parameters according to our mappings
    mapped_kwargs = kwargs.copy()
    
    # Add model_id to the parameters with the appropriate key
    model_param_name = client_config.get("model_id", "id")  
    mapped_kwargs[model_param_name] = model_name
    
    # Map any other parameters as specified in the config
    for param_name, kwargs_name in client_config.items():
        if param_name != "class" and param_name != "model_id" and param_name in kwargs:
            mapped_kwargs[kwargs_name] = kwargs[param_name]
            # Remove the original parameter to avoid duplicates
            if param_name != kwargs_name:
                mapped_kwargs.pop(param_name, None)
    
    # Create and return the client instance
    return client_class(**mapped_kwargs)
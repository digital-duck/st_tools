from api_key_store import ApiKeyStore
import os

def get_api_key(key_name="OPENAI/Yiwen"):
    return ApiKeyStore().get_api_key(key_name)

os.environ["OPENAI_API_KEY"] = get_api_key()

# use this less costly model
model_id = "gpt-4o-mini"
# Note: The openai-python library support for Azure OpenAI is in preview.
import logging
import os
from openai import AzureOpenAI
from util.app_config import app_config
from util.logger import gpt_logger, app_logger
if app_config.IS_AZURE:
    client = AzureOpenAI(azure_endpoint=app_config.AZURE_API_HOST,
        api_version="2023-12-01-preview",
        api_key=app_config.AZURE_API_KEY,
        api_key=app_config.OPENAI_KEY)

def get_single_response(message, prompt=app_config.DEFAULT_PROMPT):
    return get_chat_response([{"role": "user", "content": message}])


def get_chat_response(chat_history, prompt=app_config.DEFAULT_PROMPT):
    messages = [{"role": "system", "content": prompt}, *chat_history]
    gpt_logger.info("GPT request: %s", messages)
    response = get_gpt_response(messages)
    if "choices" not in response:
        gpt_logger.info("GPT raw response: %s", response)
        return ""
    choice = response.choices[0]  # type: ignore
    if "message" not in choice:
        gpt_logger.info("GPT raw response: %s", response)
        return ""
    message = choice["message"]
    if "content" in message and "role" in message and message["role"] == "assistant":
        gpt_logger.info("GPT response: %s", message["content"])
        return message["content"]
    gpt_logger.info("GPT raw response: %s", response)
    return ""


def get_gpt_response(messages):
    response = client.chat.completions.create(model=app_config.GPT_MODEL,
        messages=messages,
        stop=None)
    return response


if __name__ == "__main__":
    app_logger.info(get_chat_response([{"role": "assistant", "content": "Hello, how can I help you?"}, {
                    "role": "user", "content": "Tell me a joke."}]))
    app_logger.info(get_single_response("什么是战争国债"))

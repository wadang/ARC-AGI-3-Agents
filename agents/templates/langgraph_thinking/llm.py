from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from ...openai_utils import get_openai_base_url
from .schema import LLM


def get_llm(llm: LLM) -> BaseChatModel:
    """
    Get an LLM instance based on the LLM enum.
    """

    match llm:
        case LLM.OPENAI_GPT_41:
            kwargs = {"model": "gpt-4.1"}
            base_url = get_openai_base_url()
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
        case _:
            raise ValueError(f"Unknown LLM: {llm}")

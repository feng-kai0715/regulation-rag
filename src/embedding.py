import os

from langchain_huggingface import HuggingFaceEmbeddings
from functools import lru_cache

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    if token:
        return HuggingFaceEmbeddings(model_name=_MODEL_NAME, model_kwargs={"token": token})

    try:
        return HuggingFaceEmbeddings(model_name=_MODEL_NAME, model_kwargs={"local_files_only": True})
    except Exception:
        return HuggingFaceEmbeddings(model_name=_MODEL_NAME)


def preload_embedding():
    get_embedding_model()
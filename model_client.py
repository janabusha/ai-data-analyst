from ollama import Client
import streamlit as st


LOCAL_MODEL = "qwen3.5:4b"
CLOUD_MODEL = "gpt-oss:120b"

LOCAL_HOST = "http://localhost:11434"
CLOUD_HOST = "https://ollama.com"


def get_setting(
    name: str,
    default: str | None = None,
) -> str | None:
    """Read a setting from Streamlit secrets or return its default."""
    try:
        return st.secrets[name]
    except (KeyError, FileNotFoundError):
        return default


def create_model_client() -> tuple[Client, str]:
    """Create either a local Ollama client or an Ollama Cloud client."""
    provider = get_setting("MODEL_PROVIDER", "local")

    if provider == "local":
        client = Client(host=LOCAL_HOST)

        model_name = (
            get_setting("MODEL_NAME")
            or LOCAL_MODEL
        )

        return client, model_name

    if provider == "cloud":
        api_key = get_setting("OLLAMA_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OLLAMA_API_KEY is required when "
                "MODEL_PROVIDER is set to 'cloud'."
            )

        client = Client(
            host=CLOUD_HOST,
            headers={
                "Authorization": f"Bearer {api_key}",
            },
        )

        model_name = (
            get_setting("MODEL_NAME")
            or CLOUD_MODEL
        )

        return client, model_name

    raise ValueError(
        f"Unknown MODEL_PROVIDER: {provider}. "
        "Use 'local' or 'cloud'."
    )
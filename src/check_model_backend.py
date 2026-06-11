from src.model_client import OpenAICompatibleModelClient


def main() -> None:
    print("Model backend check")
    print("-------------------")

    try:
        client = OpenAICompatibleModelClient()
    except Exception as exc:
        print("Model mode is not ready.")
        print(f"Reason: {exc}")
        return

    print(f"MODEL_NAME: {client.model}")
    print(f"MODEL_BASE_URL: {client.base_url or 'not set'}")
    print(f"MODEL_BACKEND: {client.backend_type}")
    print("MODEL_API_KEY: set")

    print("")
    print("Checking /v1/models...")
    try:
        models = client.list_models()
        print(f"Server returned {len(models)} model(s).")
        if models:
            print(f"First model: {models[0]}")
    except Exception as exc:
        print("Could not list models.")
        print(f"Reason: {exc}")

    print("")
    print("Sending a tiny chat request...")
    try:
        result = client.chat(
            prompt="Return exactly this text: backend-ok",
            temperature=0,
        )
        print("Chat request succeeded.")
        print(f"Latency seconds: {result.latency_seconds}")
        print(f"Output: {result.text.strip()}")
    except Exception as exc:
        print("Chat request failed.")
        print(f"Reason: {exc}")


if __name__ == "__main__":
    main()

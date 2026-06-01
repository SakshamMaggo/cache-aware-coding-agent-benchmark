import os

from src.env_loader import load_env


def main() -> None:
    load_env()

    model_name = os.getenv("MODEL_NAME")
    api_key = os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL")

    print("Model backend check")
    print("-------------------")

    if model_name:
        print(f"MODEL_NAME: {model_name}")
    else:
        print("MODEL_NAME: not set")

    if base_url:
        print(f"MODEL_BASE_URL: {base_url}")
    else:
        print("MODEL_BASE_URL: not set")

    if api_key:
        print("MODEL_API_KEY: set")
    else:
        print("MODEL_API_KEY: not set")

    if not api_key:
        print("")
        print("Model mode is not ready yet.")
        print("Add MODEL_API_KEY to your local .env file before running --fixer model.")
        return

    if api_key == "your_api_key_here":
        print("")
        print("Model mode is not ready yet.")
        print("MODEL_API_KEY is still the placeholder value.")
        return

    print("")
    print("Model mode has the basic config needed to start.")
    print("This script does not call the model server.")


if __name__ == "__main__":
    main()
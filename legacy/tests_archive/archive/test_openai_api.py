import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import openai
from record_catalog.config_manager import ConfigManager

def test_openai_api():
    config = ConfigManager()
    api_key = config.get("OPENAI_API_KEY")

    if not api_key:
        print("OpenAI API key not set in environment or config. Test aborted.")
        return

    openai.api_key = api_key

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=5,
            temperature=0.0
        )
        if response.choices:
            print("OpenAI API Test Passed: Response received.")
        else:
            print("OpenAI API Test Failed: No response choices.")
    except Exception as e:
        print("OpenAI API Test Exception:", e)

if __name__ == "__main__":
    test_openai_api()

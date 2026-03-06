from typing import List
from dotenv import load_dotenv
import os
from utils import load_system_prompt, set_env_vars
from entities.logs_analysis import BatchSummary
from litellm import completion_with_retries
from logger import logger
from pathlib import Path
load_dotenv()
env_dict = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", None),
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY", None)
}
set_env_vars(env_dict)


def send_log_batch(logs: List[dict]) -> BatchSummary:
    system_prompt = load_system_prompt(
        Path(__file__).parent.parent / "prompts" / "summarize_batch.txt")
    messages = [{"role": "system", "content": system_prompt}, {
        "role": "user", "content": f"Logs batch: {logs}"
    }]
    response = completion_with_retries(model="groq/llama-3.3-70b-versatile",
                                       messages=messages, temperature=0, response_format=BatchSummary, num_retries=3)
    logger.debug(f"Received response: {response}")
    batch_summary = BatchSummary.model_validate_json(
        response.choices[0].message.content)
    return batch_summary


if __name__ == "__main__":
    test_batch = [
        {
            "endpoint": "/api/v1/users",
            "status_code": 500,
            "response_time_ms": 1200,
            "traceback": "sqlalchemy.exc.OperationalError: connection refused"
        }
    ]

    result = send_log_batch(test_batch)
    print(result)

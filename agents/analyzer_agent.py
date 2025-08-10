# --- agents/analyzer_agent.py ---
import json
from utils.local_llm import call_llm
from utils.logger import logger


class AnalyzerAgent:
    def __init__(self, model: str = "mistralai/devstral-small-2507"):
        self.model = model

    def analyze(self, task_prompt: str, generated_code: str, execution_output: str) -> dict:
        full_prompt = (
            f"### Task Prompt:\n{task_prompt.strip()}\n\n"
            f"### Generated Code:\n{generated_code.strip()}\n\n"
            f"### Execution Output:\n{execution_output.strip()}\n\n"
            f"Now analyze and return JSON as instructed."
        )

        logger.debug("AnalyzerAgent prompt constructed")

        try:
            result = call_llm(
                prompt=full_prompt,
                model=self.model,
                temperature=0.0,
                max_tokens=256
            )
            logger.debug("Raw Analyzer LLM response:\n{}", result)

            parsed = json.loads(result)
            if "status" in parsed and "explanation" in parsed:
                return parsed
            else:
                raise ValueError("Missing 'status' or 'explanation' keys in response JSON")
        except Exception as e:
            logger.error("AnalyzerAgent failed: {}", e)
            return {
                "status": "incomplete",
                "explanation": f"Analyzer failed to evaluate properly: {e}"
            }


# --- agents/builder_agent.py ---
from utils.local_llm import call_llm
from utils.logger import logger


class BuilderAgent:
    def __init__(self, model: str = "qwen/qwen3-coder-30b"):
        self.model = model

    def build_test(self, task_prompt: str, analysis_result: dict) -> str:
        full_prompt = (
            f"### Task Prompt:\n{task_prompt.strip()}\n\n"
            f"### Analyzer Feedback:\n{json.dumps(analysis_result, indent=2)}\n\n"
            f"Now generate the improved test code based on the above."
        )

        logger.debug("BuilderAgent prompt constructed")

        try:
            result = call_llm(
                prompt=full_prompt,
                model=self.model,
                temperature=0.2,
                max_tokens=1024
            )
            logger.debug("Builder LLM response received")
            return result.strip()
        except Exception as e:
            logger.error("BuilderAgent failed: {}", e)
            return "# Builder failed to generate test"


# --- agents/runner_agent.py ---
import subprocess
from utils.logger import logger


class RunnerAgent:
    def __init__(self):
        pass

    def run_code(self, code: str) -> str:
        try:
            with open("temp_test.py", "w") as f:
                f.write(code)

            result = subprocess.run(
                ["python", "temp_test.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + "\n" + result.stderr
            logger.debug("RunnerAgent output:\n{}", output)
            return output
        except Exception as e:
            logger.error("RunnerAgent execution failed: {}", e)
            return str(e)

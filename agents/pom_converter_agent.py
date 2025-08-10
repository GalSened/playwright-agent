# --- sandbox/pom_converter_agent.py ---
import json
from utils.local_llm import call_llm
from utils.logger import logger
from utils.validators import validate_python_code


class POMConverterAgent:
    def __init__(self, analyzer_model="the-analyzer", builder_model="builder"):
        self.analyzer_model = analyzer_model
        self.builder_model = builder_model

    def convert(self, selenium_test_code: str) -> dict:
        logger.debug("POMConverterAgent: Starting conversion process...")

        if not selenium_test_code.strip():
            return {"status": "failure", "error": "No input test code provided"}

        try:
            # Step 1: Analyze original test structure
            analyze_response = call_llm(
                model=self.analyzer_model,
                prompt=selenium_test_code,
                temperature=0.0,
                max_tokens=2048
            )
            logger.debug("Analyzer response:\n{}", analyze_response)

            try:
                extracted = json.loads(analyze_response)
            except Exception as e:
                raise ValueError(f"Failed to parse analyzer output: {e}")

            if not extracted or "steps" not in extracted:
                raise ValueError("Analyzer output missing 'steps' field")

            # Step 2: Generate POM-style Playwright test
            builder_prompt = self._build_generation_prompt(extracted)
            build_response = call_llm(
                model=self.builder_model,
                prompt=builder_prompt,
                temperature=0.0,
                max_tokens=4096
            )
            logger.debug("Builder response:\n{}", build_response)

            # Step 3: Validate + retry (self-healing logic)
            if not validate_python_code(build_response):
                logger.warning("Generated code failed validation. Retrying with refined prompt...")

                retry_prompt = self._build_generation_prompt(extracted, retry=True)
                build_response = call_llm(
                    model=self.builder_model,
                    prompt=retry_prompt,
                    temperature=0.0,
                    max_tokens=4096
                )
                if not validate_python_code(build_response):
                    raise ValueError("Generated code is invalid after retry")

            return {
                "status": "success",
                "generated_test": build_response.strip()
            }

        except Exception as e:
            logger.error("POMConverterAgent failed: {}", e)
            return {"status": "failure", "error": str(e)}

    def _build_generation_prompt(self, extracted: dict, retry: bool = False) -> str:
        base_instruction = (
            "Generate Playwright + Pytest code using Page Object Model based on these extracted steps. "
            "Ensure the code is clean, structured, and avoids anti-patterns like `sleep()` or `assert True`. "
            "Follow best practices and include all logic.\n\n"
        )
        if retry:
            base_instruction = (
                "The previous output was invalid. Please regenerate valid Python Playwright code using POM. "
                "Fix all issues and validate output integrity. Do not return partial or broken code.\n\n"
            )
        return base_instruction + json.dumps(extracted, indent=2)

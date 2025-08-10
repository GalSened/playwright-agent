# --- agents/dom_analyzer_agent.py ---
import json
from utils.local_llm import call_llm
from utils.logger import logger


class DOMAnalyzerAgent:
    def __init__(self, model: str = "dom_analyzer"):
        self.model = model

    def analyze(self, html_content: str) -> dict:
        logger.debug("DOMAnalyzerAgent: analyzing HTML content...")

        prompt = html_content.strip()
        if not prompt:
            return {
                "status": "failure",
                "error": "No HTML content provided"
            }

        try:
            result = call_llm(
                prompt=prompt,
                model=self.model,
                temperature=0.2,
                max_tokens=2048
            )

            logger.debug("Raw DOMAnalyzerAgent LLM response:\n{}", result)
            parsed = json.loads(result)

            if parsed.get("status") == "success" and "elements" in parsed:
                return parsed
            else:
                raise ValueError("Missing expected fields in response")

        except Exception as e:
            logger.error("DOMAnalyzerAgent failed: {}", e)
            return {
                "status": "failure",
                "error": f"Exception during analysis: {e}"
            }

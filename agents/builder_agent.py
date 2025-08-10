import logging
from utils.local_llm import call_llm

logger = logging.getLogger(__name__)

class BuilderAgent:
    """
    BuilderAgent is responsible for generating Playwright Python test code 
    following the Page Object Model structure, based on task instructions.
    
    It assumes the system prompt (role definition and behavior rules) is preconfigured 
    inside LM Studio or the LLM backend.
    """

    def __init__(self, model: str = "qwen/qwen3-coder-30b", temperature: float = 0.3):
        self.model = model
        self.temperature = temperature

    def build(self, instructions: str) -> dict:
        """
        Generates Page Object and Pytest-based test file based on the instructions.
        
        Args:
            instructions (str): A task description or analyzed spec from AnalyzerAgent.
        
        Returns:
            dict: {
                "status": "success" | "error",
                "page": "<Python code for Page Object>",
                "test": "<Python code for test file>",
                "error": "<optional error message>"
            }
        """
        logger.debug("BuilderAgent received instructions:\n%s", instructions)

        try:
            response = call_llm(
                model=self.model,
                system_prompt=None,  # Preset is configured in LM Studio
                user_prompt=instructions,
                temperature=self.temperature,
                max_tokens=4096
            )

            logger.debug("BuilderAgent raw response:\n%s", response)

            # Expecting structured JSON response from model
            parsed = response if isinstance(response, dict) else {}

            if "page" in parsed and "test" in parsed:
                return {
                    "status": "success",
                    "page": parsed["page"],
                    "test": parsed["test"]
                }
            else:
                return {
                    "status": "error",
                    "error": "Incomplete response from LLM",
                    "raw": parsed
                }

        except Exception as e:
            logger.exception("BuilderAgent failed during code generation")
            return {
                "status": "error",
                "error": str(e)
            }

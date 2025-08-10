from utils.local_llm import call_llm
from utils.logger import logger

class BuilderAgent:
    """
    BuilderAgent is responsible for generating Playwright test code based on tasks.
    The system prompt is expected to be defined in LM Studio (preset).
    """

    def __init__(self, model="Qwen/Qwen1.5-32B-Chat", temperature=0.3, max_tokens=4096):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_test(self, task_description: str, additional_context: str = "") -> dict:
        """
        Generates production-grade test code from a task description.
        
        Args:
            task_description: A plain English description of the test goal.
            additional_context: (Optional) Any structured analysis or context (e.g., output from Analyzer).
        
        Returns:
            A dictionary with 'page' and 'test' keys containing the generated code.
        """
        logger.debug("BuilderAgent: Constructing task for LLM")

        task = f"""\
You are assigned a test generation task.
Task Description:
{task_description.strip()}

{f"Additional Context:\n{additional_context.strip()}" if additional_context else ""}
"""

        logger.debug(f"BuilderAgent Task:\n{task}")

        response = call_llm(
            prompt=task,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            system_prompt=None  # Prompt lives in LM Studio preset
        )

        logger.debug(f"BuilderAgent LLM Response:\n{response}")
        return response

import logging
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

class RunnerAgent:
    """
    RunnerAgent executes generated test code in a temporary environment,
    validates that the code runs correctly, and returns execution results.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless

    def run_tests(self, page_code: str, test_code: str) -> dict:
        """
        Executes provided Page Object and test code using Pytest + Playwright.

        Args:
            page_code (str): Python code for the Page Object class.
            test_code (str): Python code for the corresponding test file.

        Returns:
            dict: {
                "status": "success" | "error",
                "output": "<stdout + stderr of test execution>",
                "exit_code": <int>
            }
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug("Created temporary directory: %s", temp_dir)

            page_file = os.path.join(temp_dir, "page.py")
            test_file = os.path.join(temp_dir, "test_generated.py")

            with open(page_file, "w") as pf:
                pf.write(page_code)
            with open(test_file, "w") as tf:
                tf.write(test_code)

            logger.info("Running tests in isolated temp environment...")

            cmd = [
                "pytest",
                "--tb=short",
                "-q",
                test_file
            ]
            env = os.environ.copy()
            if self.headless:
                env["HEADLESS"] = "1"

            try:
                result = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=60
                )

                logger.info("Test execution completed with exit code %d", result.returncode)

                return {
                    "status": "success" if result.returncode == 0 else "error",
                    "output": result.stdout + "\n" + result.stderr,
                    "exit_code": result.returncode
                }

            except subprocess.TimeoutExpired:
                logger.error("Test execution timed out.")
                return {
                    "status": "error",
                    "output": "Test execution timed out.",
                    "exit_code": -1
                }

            except Exception as e:
                logger.exception("Unexpected error during test execution")
                return {
                    "status": "error",
                    "output": str(e),
                    "exit_code": -1
                }

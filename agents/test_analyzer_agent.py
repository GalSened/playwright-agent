# --- sandbox/test_analyzer_agent.py ---
from agents.analyzer_agent import AnalyzerAgent

if __name__ == "__main__":
    analyzer = AnalyzerAgent()

    task = "Write a function that returns the sum of two integers."
    generated_code = """
def sum_numbers(a, b):
    return a + b
"""
    execution_output = "✅ All tests passed. Output: 7"

    result = analyzer.analyze(task, generated_code, execution_output)
    print("\n--- Analyzer Result ---")
    print(result)

# --- agents/selenium_parser_agent.py ---
"""
Pilot-only parser: סורק קובץ Page-Object וקובץ טסט של Selenium-Python
ומוציא JSON עם:
  • locators  (משייכת שמות משתנים לסלקטורים)
  • assertions (ביטויי assert מהטסט)
"""

import ast, pathlib, json

class SeleniumParserAgent:
    def __init__(self, page_path: pathlib.Path, test_path: pathlib.Path):
        self.page_path = page_path
        self.test_path = test_path

    # public ---------------------------------------------------------------
    def parse(self) -> dict:
        return {
            "page":  self._parse_page(self.page_path.read_text()),
            "tests": self._parse_test(self.test_path.read_text()),
        }

    # private --------------------------------------------------------------
    def _parse_page(self, src: str) -> dict:
        tree = ast.parse(src)
        locators = {}
        for node in ast.walk(tree):
            # match: self.foo = driver.find_element(..., "selector")
            if isinstance(node, ast.Call) and hasattr(node.func, "attr"):
                if node.func.attr.startswith("find_element"):
                    try:
                        target = node.parent.targets[0]        # left-hand variable
                        if isinstance(target, ast.Attribute):
                            name = target.attr
                            selector = ast.literal_eval(node.args[-1])
                            locators[name] = selector
                    except Exception:
                        continue
        return {"locators": locators}

    def _parse_test(self, src: str) -> dict:
        tree = ast.parse(src)
        assertions = [
            ast.get_source_segment(src, n)
            for n in ast.walk(tree)
            if isinstance(n, ast.Assert)
        ]
        return {"assertions": assertions}

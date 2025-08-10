# --- main.py (timestamped runs, Asia/Jerusalem) ---
from agents.browser_agent        import BrowserAgent
from agents.dom_analyzer_agent   import DOMAnalyzerAgent
from agents.test_generator_agent import TestGeneratorAgent
from utils.logger                import logger
import json, pathlib, datetime as dt
from zoneinfo import ZoneInfo     # ⇦ timezone support

def main() -> None:
    logger.info("==== Playwright-Agent run started ====")

    url  = "https://www.w3schools.com/html/tryit.asp?filename=tryhtml_form_submit"
    goal = "Fill first & last name and assert submission success"

    # ── 1. create per-run directory in Asia/Jerusalem time ──────────────────
    tz  = ZoneInfo("Asia/Jerusalem")
    ts  = dt.datetime.now(tz=tz).strftime("%Y%m%d_%H%M%S")
    run = pathlib.Path(f"runs/{ts}")
    run.mkdir(parents=True, exist_ok=True)
    logger.info("Run folder: {}", run)

    # ── 2. Browser → DOM ────────────────────────────────────────────────────
    dom = BrowserAgent().visit_url_and_get_dom(url)
    (run / "dom.html").write_text(dom, encoding="utf-8")

    # ── 3. DOM analysis ─────────────────────────────────────────────────────
    analysis = DOMAnalyzerAgent(dom).analyze()
    (run / "dom_analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ── 4. Generate Page Object + pytest spec via LLM ───────────────────────
    generated = TestGeneratorAgent().generate(
        analysis_json=analysis,
        url=url,
        goal=goal,
        lang="python",
    )

    # Save Page Object
    page_path = run / "form_page.py"
    page_path.write_text(generated["page"], encoding="utf-8")

    # Save Test Spec
    test_path = run / "test_form_page.py"
    test_path.write_text(generated["test"], encoding="utf-8")

    logger.success("✅ Artifacts saved in {}", run)
    logger.info("==== run finished ====")

if __name__ == "__main__":
    main()

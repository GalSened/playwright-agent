import argparse
import os
from pathlib import Path
from agents.pom_converter_agent import POMConverterAgent

def main():
    parser = argparse.ArgumentParser(description="Convert Selenium tests to Playwright tests.")
    parser.add_argument("--in", dest="input_dir", required=True, help="Input directory with Selenium tests")
    parser.add_argument("--out", dest="output_dir", required=True, help="Output directory for Playwright tests")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    converter = POMConverterAgent()

    for file_path in input_path.glob("*.py"):
        print(f"Converting {file_path.name}...")
        selenium_code = file_path.read_text(encoding="utf-8")
        result_dict = converter.convert(selenium_code)

        for filename, playwright_code in result_dict.items():
            output_file = output_path / f"{filename}.py"
            output_file.write_text(playwright_code, encoding="utf-8")
            print(f"✅ Saved: {output_file}")

if __name__ == "__main__":
    main()

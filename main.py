from agents.browser_agent import BrowserAgent

def main():
    agent = BrowserAgent(headless=False)
    url = "https://example.com"
    dom = agent.visit_url_and_get_dom(url)
    print(dom[:1000])  # הדפסה חלקית לבדיקה

if __name__ == "__main__":
    main()

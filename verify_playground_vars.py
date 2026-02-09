from playwright.sync_api import sync_playwright, expect
import os

def verify_playground_variables():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        path = os.path.abspath("docs/playground/index.html")
        page.goto(f"file://{path}")

        # Load Fibonacci example
        page.select_option("#examples", "fibonacci")

        # Click Debug
        page.click("#btnDebug")

        # Step through until we see some variables
        for _ in range(15):
            page.click("text=Step")

        # Switch to Variables tab
        page.click("text=Variables")

        # Take a screenshot
        page.screenshot(path="playground_variables.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    verify_playground_variables()

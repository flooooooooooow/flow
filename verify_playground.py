from playwright.sync_api import sync_playwright, expect
import os

def verify_playground():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the playground
        path = os.path.abspath("docs/playground/index.html")
        page.goto(f"file://{path}")

        # Check if Debug button is present
        debug_btn = page.locator("#btnDebug")
        expect(debug_btn).to_be_visible()
        expect(debug_btn).to_contain_text("Debug")

        # Click Debug button
        debug_btn.click()

        # Check if Step and Continue buttons appear
        expect(page.locator("text=Step")).to_be_visible()
        expect(page.locator("text=Continue")).to_be_visible()
        expect(page.locator("text=Stop")).to_be_visible()

        # Click Step a few times
        page.click("text=Step")
        page.click("text=Step")

        # Check Variables tab
        page.click("text=Variables")
        expect(page.locator("#variables")).to_be_visible()

        # Take a screenshot
        page.screenshot(path="playground_debug.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    verify_playground()

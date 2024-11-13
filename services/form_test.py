import asyncio
from playwright.async_api import async_playwright

async def test_forms(domain):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Log navigation status
        response = await page.goto(domain)
        print(f"Navigated to {domain} with status code {response.status}")

        # Intercept form submission request
        async def intercept_route(route):
            if route.request.method == "POST" and "contact" in route.request.url:
                print(f"Intercepted form submission to {route.request.url}")
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", intercept_route)

        # Find and fill out forms
        forms = await page.query_selector_all("form")
        for form in forms:
            inputs = await form.query_selector_all("input, textarea, select")
            for input in inputs:
                input_name = await input.get_attribute("name")
                if input_name == "input_1.3":
                    await input.fill("John")
                    print("Filled First Name with 'John'")
                elif input_name == "input_1.6":
                    await input.fill("Doe")
                    print("Filled Last Name with 'Doe'")
                elif input_name == "input_2":
                    await input.fill("john.doe@example.com")
                    print("Filled Email with 'john.doe@example.com'")
                elif input_name == "input_3":
                    await input.fill("1234567890")
                    print("Filled Phone Number with '1234567890'")
                elif input_name == "input_7":
                    await input.fill("This is a test message.")
                    print("Filled Message with 'This is a test message.'")
                elif await input.get_attribute("type") == "checkbox":
                    await input.check()
                    print(f"Checked checkbox with name {input_name}")
                elif await input.get_attribute("type") == "radio":
                    await input.check()
                    print(f"Checked radio button with name {input_name}")
                elif await input.evaluate("(element) => element.tagName.toLowerCase()") == "select":
                    options = await input.query_selector_all("option")
                    if options:
                        await options[0].click()
                        print(f"Selected first option in select with name {input_name}")

            # Click the submit button
            submit_button = await form.query_selector("#gform_submit_button_4")
            await submit_button.click()
            print("Clicked the submit button")

            # Wait for the network to be idle
            await page.wait_for_load_state("networkidle")
            print("Network is idle")

            # Check for confirmation message
            confirmation_message = await page.query_selector("div.confirmation_message")
            if confirmation_message:
                print("Form submission confirmed on the page")
            else:
                print("No confirmation message found on the page")

        await browser.close()
        print(f"Closed browser for domain {domain}")

async def main():
    domains = ["https://www.andrewsama.com/contact/"]  # Replace with your list of domains
    for domain in domains:
        print(f"Testing forms on {domain}")
        await test_forms(domain)
        print(f"Completed testing forms on {domain}")

asyncio.run(main())
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebTablePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

        # Modal Locators
        self.modal_content = (By.CLASS_NAME, "modal-content")
        self.add_button = (By.ID, "addNewRecordButton")
        self.first_name = (By.ID, "firstName")
        self.last_name = (By.ID, "lastName")
        self.email = (By.ID, "userEmail")
        self.age = (By.ID, "age")
        self.salary = (By.ID, "salary")
        self.department = (By.ID, "department")
        self.submit_btn = (By.ID, "submit")

    def hide_ads_and_footers(self):
        """Removes intrusive elements that intercept clicks."""
        self.driver.execute_script("""
            let fixedBan = document.getElementById('fixedban');
            if (fixedBan) fixedBan.remove();
            let footer = document.querySelector('footer');
            if (footer) footer.remove();
        """)

    def click_edit_by_index(self, index: int):
        """Clicks the edit icon for a specific row index."""
        self.hide_ads_and_footers()
        edit_locator = (By.CSS_SELECTOR, f"#edit-record-{index}, span[id='edit-record-{index}']")
        edit_icon = self.wait.until(EC.presence_of_element_located(edit_locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_icon)
        self.driver.execute_script("arguments[0].click();", edit_icon)

        # Wait for modal dialog to appear
        self.wait.until(EC.visibility_of_element_located(self.modal_content))

    def close_modal(self):
        """Closes the open modal cleanly using the ESC key or the close button."""
        try:
            # First attempt: Try closing via Escape key (native modal dismissal)
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
        except Exception:
            pass

        # If modal is still open, click the close button via JavaScript
        if len(self.driver.find_elements(*self.modal_content)) > 0:
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".close, button[aria-label='Close']")
            if close_buttons and close_buttons[0].is_displayed():
                self.driver.execute_script("arguments[0].click();", close_buttons[0])
            else:
                # Fallback: Submit existing data to close the modal
                submit = self.driver.find_element(*self.submit_btn)
                self.driver.execute_script("arguments[0].click();", submit)

        # Wait until modal completely disappears
        self.wait.until(EC.invisibility_of_element_located(self.modal_content))
        time.sleep(0.5)

    def add_new_record(self, data: dict):
        """Fills out the registration form, clicks submit, and confirms modal exit."""
        self.hide_ads_and_footers()

        # Click the Add button
        add_btn = self.wait.until(EC.element_to_be_clickable(self.add_button))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
        self.driver.execute_script("arguments[0].click();", add_btn)

        # Wait for modal visibility
        self.wait.until(EC.visibility_of_element_located(self.modal_content))

        # Fill inputs
        self.wait.until(EC.visibility_of_element_located(self.first_name)).send_keys(data["firstName"])
        self.driver.find_element(*self.last_name).send_keys(data["lastName"])
        self.driver.find_element(*self.email).send_keys(data["email"])
        self.driver.find_element(*self.age).send_keys(str(data["age"]))
        self.driver.find_element(*self.salary).send_keys(str(data["salary"]))
        self.driver.find_element(*self.department).send_keys(data["department"])

        # Click submit via JavaScript
        submit = self.wait.until(EC.presence_of_element_located(self.submit_btn))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit)
        self.driver.execute_script("arguments[0].click();", submit)

        # Wait until modal closes completely so table DOM renders the new row
        self.wait.until(EC.invisibility_of_element_located(self.modal_content))
        time.sleep(0.5)

    def get_row_data_by_email(self, email: str) -> list[str]:
        """
        Generic dynamic locator:
        Finds the exact row containing the unique email without relying on hardcoded row indexes.
        """
        row_xpath = f"//div[@class='rt-tr-group'][.//div[normalize-space()='{email}']]//div[@role='gridcell']"
        cells = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, row_xpath)))
        return [cell.text.strip() for cell in cells if cell.text.strip()]


def test_webtables_workflow():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get("https://demoqa.com/webtables")
        table_page = WebTablePage(driver)

        # 1. Click on the 3rd edit button
        table_page.click_edit_by_index(3)

        # 2. Close edit modal cleanly
        table_page.close_modal()

        # 3. Add a new row
        new_user = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "johndoe.qa@test.com",
            "age": 29,
            "salary": 65000,
            "department": "Engineering"
        }
        table_page.add_new_record(new_user)

        # 4. Verify details in table using generic locator
        actual_row = table_page.get_row_data_by_email(new_user["email"])
        print(f"Captured Row Data: {actual_row}")

        assert actual_row[0] == new_user["firstName"]
        assert actual_row[1] == new_user["lastName"]
        assert actual_row[2] == str(new_user["age"])
        assert actual_row[3] == new_user["email"]
        assert actual_row[4] == str(new_user["salary"])
        assert actual_row[5] == new_user["department"]

        print("Verification Successful!")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_webtables_workflow()
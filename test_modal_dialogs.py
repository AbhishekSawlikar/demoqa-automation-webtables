from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ModalDialogsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # Trigger Buttons
        self.small_modal_btn = (By.ID, "showSmallModal")
        self.large_modal_btn = (By.ID, "showLargeModal")

        # Modal Elements
        self.modal_content = (By.CLASS_NAME, "modal-content")
        self.small_modal_title = (By.ID, "example-modal-sizes-title-sm")
        self.large_modal_title = (By.ID, "example-modal-sizes-title-lg")
        self.modal_body = (By.CLASS_NAME, "modal-body")
        self.close_small_btn = (By.ID, "closeSmallModal")
        self.close_large_btn = (By.ID, "closeLargeModal")

    def hide_ads_and_footers(self):
        """Removes intrusive DemoQA ad banners and footers."""
        self.driver.execute_script("""
            let fixedBan = document.getElementById('fixedban');
            if (fixedBan) fixedBan.remove();
            let footer = document.querySelector('footer');
            if (footer) footer.remove();
        """)

    def open_small_modal(self):
        self.hide_ads_and_footers()
        btn = self.wait.until(EC.element_to_be_clickable(self.small_modal_btn))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.visibility_of_element_located(self.modal_content))

    def get_small_modal_details(self) -> dict:
        title = self.wait.until(EC.visibility_of_element_located(self.small_modal_title)).text.strip()
        body = self.driver.find_element(*self.modal_body).text.strip()
        return {"title": title, "body": body}

    def close_small_modal(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.close_small_btn))
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.invisibility_of_element_located(self.modal_content))

    def open_large_modal(self):
        self.hide_ads_and_footers()
        btn = self.wait.until(EC.element_to_be_clickable(self.large_modal_btn))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.visibility_of_element_located(self.modal_content))

    def get_large_modal_details(self) -> dict:
        title = self.wait.until(EC.visibility_of_element_located(self.large_modal_title)).text.strip()
        body = self.driver.find_element(*self.modal_body).text.strip()
        return {"title": title, "body": body}

    def close_large_modal(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.close_large_btn))
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.invisibility_of_element_located(self.modal_content))


def test_modal_content():
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get("https://demoqa.com/modal-dialogs")
        modal_page = ModalDialogsPage(driver)

        # ---------------- Small Modal Verification ----------------
        modal_page.open_small_modal()
        small_details = modal_page.get_small_modal_details()

        print(f"Small Modal Title: {small_details['title']}")
        print(f"Small Modal Body: {small_details['body']}")

        assert small_details["title"] == "Small Modal"
        assert "This is a small modal. It has very less content" in small_details["body"]

        modal_page.close_small_modal()

        # ---------------- Large Modal Verification ----------------
        modal_page.open_large_modal()
        large_details = modal_page.get_large_modal_details()

        print(f"Large Modal Title: {large_details['title']}")

        assert large_details["title"] == "Large Modal"
        assert "Lorem Ipsum is simply dummy text" in large_details["body"]

        modal_page.close_large_modal()

        print("Both modal content verifications passed successfully!")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_modal_content()
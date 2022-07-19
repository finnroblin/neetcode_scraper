from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import pandas as pd

option = Options()
option.binary_location = '/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta'

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager(version='104.0.5112.20').install()),
                          options=option)
driver.get("https://neetcode.io")
driver.implicitly_wait(2)


class Scraper:
    def __init__(self):
        self.df = pd.DataFrame(columns=[
            "Category", "is_completed", "problem_name", "problem_url",
            "difficulty_level", "youtube_url"
        ])

    def export_to_csv(self):
        self.df.to_csv("out.csv")

    def scrape(self):
        n_th_child_counter = 4  # used for selecting the close button for each category app-modal
        overarching_categories = driver.find_elements(By.CLASS_NAME,
                                                      "accordion-container")
        for category in overarching_categories[
                1:]:  # the first one doesn't count
            unparsed_category_name = category.text
            category_name = unparsed_category_name.split("\n")[0]
            print("cat name: ", category_name)
            category.click()  # open the category accordian
            problems = category.find_elements(By.TAG_NAME, "tr")

            for problem in problems[1:]:
                problem_is_completed = problem.get_attribute(
                    "class") == "ng-star-inserted completed"
                print("iscompleted", problem_is_completed)
                problem_attributes = problem.find_elements(By.TAG_NAME, "td")

                # Get the link and problem name
                problem_link_element = problem_attributes[1].find_element(
                    By.TAG_NAME, "a")
                problem_href = problem_link_element.get_attribute("href")
                problem_name_element = problem_link_element.find_element(
                    By.TAG_NAME, "b")
                problem_name = problem_name_element.text
                print(problem_href, problem_name)

                # Get the difficulty
                button_text_element = problem_attributes[2].find_element(
                    By.TAG_NAME, "div").find_element(By.TAG_NAME,
                                                     "button").find_element(
                                                         By.TAG_NAME, "b")
                difficulty_text = button_text_element.text
                print(difficulty_text)

                # get the youtube url
                youtube_button_element = problem_attributes[3].find_element(
                    By.TAG_NAME, "div").find_element(By.TAG_NAME, "a")
                WebDriverWait(driver, 50).until(
                    EC.element_to_be_clickable(
                        (youtube_button_element))).click()

                actual_button_link = driver.find_element(
                    By.CSS_SELECTOR,
                    "body > app-root > app-pattern-table-list > app-pattern-table:nth-child(4) > app-accordion > div > div > app-table > app-modal:nth-child(3) > div > div.modal-card > header > h1 > a"
                )
                youtube_href = actual_button_link.get_attribute("href")
                print("youtube href: ", youtube_href)
                close_button_element_path = f"body > app-root > app-pattern-table-list > app-pattern-table:nth-child({n_th_child_counter}) > app-accordion > div > div > app-table > app-modal:nth-child(3) > div > div.modal-card > footer > button > b"
                close_button_element = WebDriverWait(driver, 50).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, close_button_element_path)))
                driver.execute_script(
                    "arguments[0].click();", close_button_element
                )  # magic selenium shit from https://stackoverflow.com/questions/57741875/selenium-common-exceptions-elementclickinterceptedexception-message-element-cl that made it work

                # .click()

                # driver.find_element(By.CSS_SELECTOR, "body > app-root > app-pattern-table-list > app-pattern-table:nth-child(4) > app-accordion > div > div > app-table > app-modal:nth-child(3) > div > div.modal-card > footer > button > b")
                # close_button_element.click()

                data = [
                    category_name, problem_is_completed, problem_name,
                    problem_href, difficulty_text, youtube_href
                ]
                self.df.loc[len(self.df.index)] = data
                print("data: ", data)
            # end problems loop
            n_th_child_counter += 1  # to make the CSS path of the YouTube elements work
            print("finished category: ", category_name)


s = Scraper()
s.scrape()
s.export_to_csv()

driver.close()
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
import requests
import concurrent.futures
from ratelimit import limits, sleep_and_retry
import re

blog_url = "https://taracod.wixsite.com/biotope/kemono"
imgs = []
folder = "wixsite-illustrations"


@sleep_and_retry
@limits(200, 60)
def save_img(url):
    path = f"{folder}/{url.split('/')[-1]}"
    with open(path, 'wb+') as img:
        img.write(requests.get(url).content)


if __name__ == "__main__":
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(blog_url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == "complete")
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    if not os.path.isdir(folder):
        os.mkdir(folder)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for iframe in driver.find_elements(By.XPATH, "//iframe[@class='_3yxZn']"):
            driver.switch_to.frame(iframe)
            for element in driver.find_elements(By.XPATH, "//img[@src]"):
                executor.submit(save_img, re.findall(f'(?:https://static.wixstatic.com/media/[^/]+)', element.get_attribute('src'))[0])
            driver.switch_to.default_content()
        executor.shutdown(wait=True)

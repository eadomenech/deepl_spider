import time

import requests
import undetected_chromedriver as uc
from decouple import config
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Spider:

    def __init__(self):
        self.client_user = config('CLIENT_USER')
        self.password = config('PASSWORD')
        self.url = 'https://www.deepl.com/es/login/'

    def run(self):
        raise NotImplementedError

    def download_invoices(self, links, download_path='', **kwargs):

        if 'cookies' in kwargs:
            cookies = kwargs['cookies']

        paths = list()

        for index, link in enumerate(links):
            invoice_url = link.get_attribute("href")
            invoice_name = link.text

            invoice_path = f"{download_path}{invoice_name}.pdf"
            with open(invoice_path, 'wb') as f:
                r = requests.get(invoice_url, cookies=cookies)
                f.write(r.content)

            paths.append(invoice_path)

        return paths


class SeleniumSpider(Spider):

    def __init__(self):
        self.delay = 60
        super().__init__()

    def run(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        self.driver = uc.Chrome(options=options)

        cookies = self.do_login()
        links = self.get_invoice_links()
        paths = self.download_invoices(links, cookies=cookies)

        self.driver.close()

        return paths

    def do_login(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, self.delay).until(
            EC.presence_of_element_located((By.NAME, 'email')))
        username_element = self.driver.find_element(By.NAME, "email")
        username_element.send_keys(self.client_user)

        username_element = self.driver.find_element(By.NAME, "password")
        username_element.send_keys(self.password)

        self.driver.find_element(By.XPATH, ".//button[@type='submit']").click()

        time.sleep(45)

        return self.get_cookies(self.driver)

    def get_invoice_links(self):
        self.driver.get("https://www.deepl.com/es/account/invoices")
        time.sleep(20)

        links = self.driver.find_elements(
            By.XPATH, "//div[@class='invoices-module--invoice--Mo1P6']//a")

        return links

    def get_cookies(self, driver):
        cookies_out = driver.get_cookies()
        cookies = {}

        for c in cookies_out:
            cookies[c['name']] = c['value']

        return cookies

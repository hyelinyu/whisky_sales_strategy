from selenium import webdriver
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
driver.get("https://www.thewhiskyexchange.com/p/3512/macallan-12-year-old-sherry-oak")

# challenge 기다림 (Cloudflare 로딩)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")

# 예시 추출
name = soup.select_one("h1.product-main__name").text.strip()
price = soup.select_one("p.product-action__price").text.strip()

print(name, price)
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

with open('links_data/single_malt_scotch_links.json', 'r') as f:
    data = json.load(f)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach',True)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")

whisky_info =
for whisky in data:

    driver = webdriver.Chrome(chrome_options)
    url_whisky_info = whisky['url']
    driver.get(url_whisky_info)
    time.sleep(3)

    try:
        # 최대 5초까지 대기 후 'Accept' 버튼 클릭
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
        ).click()
        print("쿠키 동의 처리 완료")
    except:
        print("쿠키 동의창 없음 또는 이미 처리됨")

    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:



#product main name
#product main info
#price
#vol/alcohol%
#style (style_body, style_richness, style_smoke, style_sweetness
#character [,]
#food paring dishes [,]
#region
#country
#tasting note (note_nose,note_palate,note_finish)
#review 덩어리만 texts


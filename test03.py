import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach',True)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")


driver = webdriver.Chrome(chrome_options)
url_whisky_info ='https://www.thewhiskyexchange.com/p/72478/grand-old-parr-12-year-old-litre'
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
# product_name = soup.select_one('h1.product-main__name').text
# # product_main_info = soup.select('ul.product-main__meta')
# print(product_name)
# print(product_main_info[0].text)

# characters = soup.find_all(name='li',class_='flavour-profile__item flavour-profile__item--character')
# list = []
# for n in characters:
#     text = n.getText()
#     list.append(text)
# print(list)
import numpy as np
# style_dict = {'style_body': np.nan,
#              'style_richness':np.nan,
#              'style_smoke':np.nan,
#              'style_sweetness':np.nan}
#
# try:
#     style_tags = soup.find_all(name='div', class_='flavour-profile__gauge js-flavour-profile__gauge gauge-container')
#     if style_tags :
#         values = []
#         for n in style_tags:
#             number = n.getText()
#             values.append(number)
#
#         for key, val in zip(style_dict.keys(),values):
#             style_dict[key] = val
# except Exception as e:
#     print('style parsing error:',e)
# print(style_dict)


# product_facts_dict = {'bottler':np.nan,
#                           'age':np.nan,
#                           'country':np.nan,
#                           'region':np.nan,
#                           'casktype':np.nan,
#                           'colouring':np.nan}
# try:
#     product_facts_type_tags = soup.find_all(name='h3', class_='product-facts__type')
#     product_facts_data_tags = soup.find_all(name='p', class_='product-facts__data')
#
#     for type_tag, data_tag in zip(product_facts_type_tags, product_facts_data_tags):
#         key = type_tag.getText().strip().lower()
#         value = data_tag.getText().strip().lower()
#
#         if key in product_facts_dict:
#             product_facts_dict[key] = value
#
# except Exception as e:
#     print('product facts parsing error:', e)
#
# print(product_facts_dict)

# tasting_notes_dict = {'nose':np.nan,
#                           'palate':np.nan,
#                           'finish':np.nan}
#
# try:
#     tasting_note_title_tags = soup.find_all(name='h4', class_='product-notes__title')
#     tasting_note_content_tags = soup.find_all(name='p', class_='product-notes__copy')
#
#     if tasting_note_title_tags :
#
#         for title_tag, content_tag in zip(tasting_note_title_tags,tasting_note_content_tags):
#             key = title_tag.getText().strip().lower()
#             value = content_tag.getText()
#
#             if key in tasting_notes_dict:
#                 tasting_notes_dict[key] = value
#
# except Exception as e:
#     print('tasting notes parsing error:', e)
#
# print(tasting_notes_dict)

# reviews = []
#
# try:
#     show_more = WebDriverWait(driver, 5).until(
#         EC.element_to_be_clickable(
#             (By.CSS_SELECTOR, 'button.cta-button.cta-button--delta.js-review-list__more.review-list__more')
#         )
#     )
#     driver.execute_script("arguments[0].scrollIntoView();", show_more)
#     time.sleep(0.5)
#     show_more.click()
#     time.sleep(1)  # 클릭 후 리뷰가 로딩될 시간 주기
# except:
#     pass
#
# time.sleep(7)
# html = driver.page_source
# soup = BeautifulSoup(html, 'html.parser')
# reviews_tags = soup.find_all(name='p', class_='review-list__copy')
#
# if reviews_tags:
#     for tag in reviews_tags:
#         review = tag.getText(strip=True)
#         if 'service' not in review.lower() and 'deliver' not in review.lower():
#             reviews.append(review)
# else:
#     reviews = [np.nan]
# print(reviews)

product_name = soup.find(name='h1',class_='product-main__name').getText()
product_main_info = soup.find(name='ul',class_='product-main__meta').getText()
vol_alcohol = soup.find(name='p', class_='product-main__data').getText()
product_price = soup.find(name='p', class_='product-action__price').getText()
vat_price = soup.find(name='p', class_='product-action__vat-price').getText()


print(product_name)
print(product_main_info)
print(vol_alcohol)
print(product_price)
print(vat_price)

driver.quit()
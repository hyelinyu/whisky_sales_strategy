import json
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os

scrapped_data = []
json_name = os.listdir('./links_data')
for file in json_name:
    with open(f'links_data/{file}', 'r') as f:
        data = json.load(f)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('detach',True)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")



    # scrap from each page
    for whisky in data:

        driver = webdriver.Chrome(chrome_options)
        url_whisky_info = whisky['url']
        driver.get(url_whisky_info)
        time.sleep(5)

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
        #columns
        #--main info

        product_name = soup.select('h1.product-main__name')[0].text
        product_name = soup.find(name='h1',class_='product-main__name').getText()
        product_main_info = soup.find(name='ul',class_='product-main__meta').getText()
        vol_alcohol = soup.find(name='p', class_='product-main__data').getText()
        product_price = soup.find(name='p', class_='product-action__price').getText()
        vat_price = soup.find(name='p', class_='product-action__vat-price').getText()


        time.sleep(3)

        #--style
        style_dict = {'style_body': np.nan,
                 'style_richness':np.nan,
                 'style_smoke':np.nan,
                 'style_sweetness':np.nan}

        try:
            style_tags = soup.find_all(name='div', class_='flavour-profile__gauge js-flavour-profile__gauge gauge-container')
            if style_tags :
                values = []
                for n in style_tags:
                    number = n.getText()
                    values.append(number)

                for key, val in zip(style_dict.keys(),values):
                    style_dict[key] = val
        except Exception as e:
            print('style parsing error:',e)

        time.sleep(3)

        #--character
        characters = []
        try:
            characters_tag = soup.find_all(name='li', class_='flavour-profile__item flavour-profile__item--character')
            if characters_tag:
                for tag in characters_tag:
                    character = tag.getText()
                    characters.append(character)
            else:
                characters = [np.nan]
        except Exception as e:
            print('character parsing error:', e)
        time.sleep(2)
        #--food paring dishes
        paring_dishes = []
        try :
            food_paring_tags = soup.find_all(name='li',class_='food-pairing__item')
            if food_paring_tags:
                for tag in food_paring_tags:
                    food = tag.getText()
                    paring_dishes.append(food)
            else:
                paring_dishes = [np.nan]
        except Exception as e:
            print('Food paring parsing error:', e)

        time.sleep(3)
        #--product facts
        product_facts_dict = {'bottler':np.nan,
                              'age':np.nan,
                              'country':np.nan,
                              'region':np.nan,
                              'casktype':np.nan,
                              'colouring':np.nan}
        try:
            product_facts_type_tags = soup.find_all(name='h3', class_='product-facts__type')
            product_facts_data_tags = soup.find_all(name='p', class_='product-facts__data')

            if product_facts_type_tags:

                for type_tag, data_tag in zip(product_facts_type_tags, product_facts_data_tags):
                    key = type_tag.getText().strip().lower()
                    value = data_tag.getText().strip().lower()

                    if key in product_facts_dict:
                        product_facts_dict[key] = value

        except Exception as e:
            print('product facts parsing error:', e)

        time.sleep(3)


        #--tasting notes
        tasting_notes_dict = {'nose':np.nan,
                              'palate':np.nan,
                              'finish':np.nan}

        try:
            tasting_note_title_tags = soup.find_all(name='h4', class_='product-notes__title')
            tasting_note_content_tags = soup.find_all(name='p', class_='product-notes__copy')

            if tasting_note_title_tags :

                for title_tag, content_tag in zip(tasting_note_title_tags,tasting_note_content_tags):
                    key = title_tag.getText().strip().lower()
                    value = content_tag.getText()

                    if key in tasting_notes_dict:
                        tasting_notes_dict[key] = value

        except Exception as e:
            print('tasting notes parsing error:', e)

        time.sleep(3)


        #--reviews : 'service','deliver' 포함 시 pass
        #한페이지당 5개
        reviews = []

        try:
            show_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button.cta-button.cta-button--delta.js-review-list__more.review-list__more')
                )
            )
            driver.execute_script("arguments[0].scrollIntoView();", show_more)
            time.sleep(0.5)
            show_more.click()
            time.sleep(1)  # 클릭 후 리뷰가 로딩될 시간 주기
        except:
            pass

        time.sleep(7)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        reviews_tags = soup.find_all(name='p', class_='review-list__copy')

        if reviews_tags:
            for tag in reviews_tags:
                review = tag.getText(strip=True)
                if 'service' not in review.lower() and 'deliver' not in review.lower():
                    reviews.append(review)
        else:
            reviews = [np.nan]



        #row
        row = {
            'name': product_name,
            'main_info': product_main_info,
            'volume_alcohol': vol_alcohol,
            'price': product_price,
            'vat_price': vat_price,
            'style_body': style_dict['style_body'],
            'style_richness': style_dict['style_richness'],
            'style_smoke': style_dict['style_smoke'],
            'style_sweetness': style_dict['style_sweetness'],
            'characters': ', '.join([str(c) for c in characters]),
            'food_paring': ', '.join([str(d) for d in paring_dishes]),
            'bottler': product_facts_dict['bottler'],
            'age': product_facts_dict['age'],
            'country': product_facts_dict['country'],
            'region': product_facts_dict['region'],
            'casktype': product_facts_dict['casktype'],
            'colouring': product_facts_dict['colouring'],
            'nose': tasting_notes_dict['nose'],
            'palate': tasting_notes_dict['palate'],
            'finish': tasting_notes_dict['finish'],
            'reviews': ' || '.join([str(r) for r in reviews])
        }

        scrapped_data.append(row)

        #CHECK if it is completed
        print(f'completed : scrapping for {whisky}')
        driver.quit()
        time.sleep(3)

df = pd.DataFrame(scrapped_data)
df.to_csv('whisky_data.csv',index=False)




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


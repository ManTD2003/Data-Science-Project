from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException, NoSuchWindowException
import time
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
from concurrent.futures import ProcessPoolExecutor

def crawl_data(driver):
    def extract_reviews(driver):
        """
        take reviews from customers
        """
        reviews_data = []
        page_number = 1

        while True:
            # print(f"Extracting reviews from page {page_number}")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.comment-list"))
                )
            except TimeoutException:
                # print("No reviews found on this page. Exiting pagination.")
                break

            reviews = driver.find_elements(By.CSS_SELECTOR, "ul.comment-list > li.par")
            for review in reviews:
                review_data = {}
                try:
                    reviewer_name = review.find_element(By.CSS_SELECTOR, "p.cmt-top-name").text
                    review_data['reviewer_name'] = reviewer_name
                except:
                    review_data['reviewer_name'] = None
                try:
                    review_content = review.find_element(By.CSS_SELECTOR, "p.cmt-txt").text
                    review_data['review_content'] = review_content
                except:
                    review_data['review_content'] = None

                try:
                    stars = review.find_elements(By.CSS_SELECTOR, "div.cmt-top-star i")
                    rating = len([star for star in stars if 'iconcmt-starbuy' in star.get_attribute('class')])
                    review_data['review_rating'] = rating
                except:
                    review_data['review_rating'] = None

                reviews_data.append(review_data)

            try:
                next_page_number = page_number + 1
                next_button = driver.find_element(By.XPATH, f"//div[@class='pagcomment']/a[@title='trang {next_page_number}'][text()='›']")
                
                if next_button:
                    # print(f"chuyen toi page {next_page_number}")
                    driver.execute_script(f"ratingCmtList({next_page_number});")
                    page_number += 1
                    time.sleep(2)
                else:
                    # print("het page, dung extracting reviews.")
                    break
            except NoSuchElementException:
                # print("khong co nut next. Finished extracting reviews.")
                break
            except Exception as e:
                # print(f"loi dme nooo: {e}")
                break

        return reviews_data


    product_links = []
    products_data = []

    products = driver.find_elements(By.CSS_SELECTOR, "ul.listproduct > li.item")
    for product in products:
        link_element = product.find_element(By.TAG_NAME, "a")
        href = link_element.get_attribute('href')
        product_links.append(href)

    for index, product_link in enumerate(product_links):
        data = {}
        try:
            # print(f"\nProcessing product {index}")

            driver.get(product_link)

            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # get product name
            try:
                product_name_element = driver.find_element(By.CSS_SELECTOR, "div.product-name > h1")
                product_name = product_name_element.text
                data['name'] = product_name
            except:
                data['name'] = None

            # get product price
            try:
                product_price_element = driver.find_element(By.CSS_SELECTOR, "div.bs_price > strong")
                product_price = product_price_element.text
                data['price'] = product_price
            except:
                data['price'] = None

            # get product rating
            try:
                product_point_element = driver.find_element(By.CSS_SELECTOR, "div.boxrate__top div.point > p")
                product_point = product_point_element.text
                data['point'] = product_point
            except:
                data['point'] = None

            # get reviews
            try:
                view_all_reviews_link = driver.find_element(By.CSS_SELECTOR, "a.btn-view-all")
                reviews_page_url = view_all_reviews_link.get_attribute('href')

                driver.get(reviews_page_url)
                
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                reviews_data = extract_reviews(driver)
                data['reviews'] = reviews_data
                driver.back()
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except NoSuchElementException:
                reviews_data = extract_reviews(driver)
                data['reviews'] = reviews_data

            products_data.append(data)

        except Exception as e:
            print("Exception occurred:", e)
            continue
    return products_data


def save_data(products_data, category):
    for idx, product in enumerate(products_data):
        product['id'] = idx + 1  # Start IDs from 1
    products_df = pd.DataFrame(products_data, columns=['id', 'name', 'price', 'point'])
    reviews_list = []

    for product in products_data:
        product_id = product['id']
        reviews = product.get('reviews', [])
        for review in reviews:
            review_data = {
                'reviewer_name': review.get('reviewer_name'),
                'review_content': review.get('review_content'),
                'review_point': review.get('review_rating'),
                'product_id': product_id
            }
            reviews_list.append(review_data)

    reviews_df = pd.DataFrame(reviews_list, columns=['reviewer_name', 'review_content', 'review_point', 'product_id'])
    if not os.path.exists(category):
        os.makedirs(category)
    products_df.to_csv(os.path.join(category, "products.csv"), index=False, encoding="utf-8")
    reviews_df.to_csv(os.path.join(category, "reviews.csv"), index=False, encoding="utf-8")
    print(f"done with {category} category")
    
def crawl_data_single_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    
    while True:
        try:
            see_more_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//strong[@class='see-more-btn' and contains(text(), 'Xem thêm')]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView();", see_more_button)
            see_more_button.click()
            time.sleep(2)
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
            break
        except NoSuchWindowException:
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    cate = url.strip().split('/')[-1]
    data = crawl_data(driver)
    save_data(products_data=data, category=cate)
    driver.quit()

def crawl_data_from_urls(urls: list[str]):
    for url in urls:
        driver = webdriver.Chrome()
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)

        wait = WebDriverWait(driver, 10)

        while True:
            try:
                see_more_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//strong[@class='see-more-btn' and contains(text(), 'Xem thêm')]")
                    )
                )
                
                driver.execute_script("arguments[0].scrollIntoView();", see_more_button)
                see_more_button.click()
                # print("Clicked 'See More' button")
                time.sleep(2) 
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):
                # print("No more 'See More' button to click or button not clickable.")
                break
            except NoSuchWindowException:
                # print("Browser window was closed unexpectedly.")
                break
            except Exception as e:
                # print(f"An unexpected exception occurred: {e}")
                break
        cate = url.strip().split('/')[-1]
        data = crawl_data(driver)
        save_data(products_data=data, category=cate)

def crawl_data_multi_threads(urls):
    max_workers = os.cpu_count()  # Use as many processes as the system allows
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(crawl_data_single_url, urls)


import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/?start={}"


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def scrape_catalog(driver):

    all_products = []

    for start in range(0, 500, 12):
        url = CATALOG_URL.format(start)
        print(f"Opening {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td.custom__table-heading__title"))
            )
        except:
            print("No table found, stopping.")
            break

        rows = driver.find_elements(By.CSS_SELECTOR, "td.custom__table-heading__title")

        for cell in rows:
            link = cell.find_element(By.TAG_NAME, "a")
            name = link.text.strip()
            product_url = link.get_attribute("href")

            if "solution" in name.lower():
                continue

            all_products.append({
                "name": name,
                "url": product_url,
            })

    return all_products


def scrape_product_details(driver, product):
    from selenium.webdriver.common.by import By

    driver.get(product["url"])
    time.sleep(2)

    # -------- DESCRIPTION --------
    description = ""
    try:
        sections = driver.find_elements(By.CSS_SELECTOR, "div.product-catalogue-training-calendar__row.typ")
        for section in sections:
            try:
                heading = section.find_element(By.TAG_NAME, "h4").text.strip()
                if heading == "Description":
                    description = section.find_element(By.TAG_NAME, "p").text.strip()
                    break
            except:
                continue
    except:
        pass

    # -------- TEST TYPE --------
    test_types = []
    try:
        type_elements = driver.find_elements(By.CLASS_NAME, "product-catalogue__key")
        for el in type_elements:
            text = el.text.strip()
            if text:
                test_types.append(text)
    except:
        pass

    # -------- DURATION --------
    duration = "Unknown"
    try:
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for p in paragraphs:
            if "Completion Time" in p.text:
                duration = p.text.strip()
                break
    except:
        pass

    # -------- REMOTE SUPPORT --------
    remote_support = "No"
    try:
        remote_icons = driver.find_elements(By.CSS_SELECTOR, "span.catalogue__circle")
        for icon in remote_icons:
            classes = icon.get_attribute("class")
            if "-yes" in classes:
                remote_support = "Yes"
                break
    except:
        pass

    product["description"] = description
    product["test_type"] = test_types
    product["duration"] = duration
    product["remote_support"] = remote_support
    product["adaptive_support"] = "Unknown"

    return product


if __name__ == "__main__":
    driver = get_driver()

    basic_catalog = scrape_catalog(driver)

    print("Basic count:", len(basic_catalog))

    detailed_catalog = []

    for idx, product in enumerate(basic_catalog):
        print(f"Scraping detail {idx + 1}/{len(basic_catalog)}")
        enriched = scrape_product_details(driver, product)
        detailed_catalog.append(enriched)

    driver.quit()

    print("Final enriched count:", len(detailed_catalog))

    with open("data/processed_catalog.json", "w") as f:
        json.dump(detailed_catalog, f, indent=2)
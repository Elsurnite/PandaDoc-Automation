import requests
import random
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

# Airtable API bilgileri
base_id = ''
table_id = ''
view_name = ''
personal_access_token = ''
base_table_api_url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
headers = {
    'Authorization': f'Bearer {personal_access_token}',
}

def tik(record_id, text):
    update_url = f'{base_table_api_url}/{record_id}'
    data = {
        'fields': {
            'SozlesmeDurumu': f'{text}' 
        }
    }
    try:
        response = requests.patch(update_url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Kayıt başarıyla güncellendi. Record ID: {record_id}")
        else:
            print(f"Hata: Güncelleme yapılamadı. Status kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Bir hata oluştu: {e}")

def url(record_id):
    update_url = f'{base_table_api_url}/{record_id}'
    data = {
        'fields': {
            'SozlesmeLink': f'{driver.current_url}'
        }
    }
    try:
        response = requests.patch(update_url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Kayıt başarıyla güncellendi. Record ID: {record_id}")
        else:
            print(f"Hata: Güncelleme yapılamadı. Status kodu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Bir hata oluştu: {e}")
                

def split_full_name(full_name):
    # Trim leading and trailing spaces
    full_name = full_name.strip()
    
    # Split the full name into parts
    name_parts = full_name.split()
    
    # Determine the first name, middle names, and last name
    if len(name_parts) == 1:
        first_name = name_parts[0]
        middle_names = ""
        last_name = ""
    elif len(name_parts) == 2:
        first_name = name_parts[0]
        middle_names = ""
        last_name = name_parts[1]
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1]
        middle_names = " ".join(name_parts[1:-1])
    
    return first_name, middle_names, last_name

mode = input("Please select mode: 1 for 'Status Check' or 2 for 'Status Check and Link Update': ")

if mode not in ['1', '2']:
    print("Invalid selection. Please choose '1' or '2'.")
    exit()

# WebDriver'ı başlat
options = webdriver.ChromeOptions() # Eğer Edge kullanıyorsanız EdgeOptions kullanın
options.add_argument("--incognito")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Giriş işlemlerini gerçekleştir
driver.get("https://app.pandadoc.com/a/#/dashboard")
driver.implicitly_wait(20)
time.sleep(4)
try:
    driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    driver.find_element(By.ID, 'email').send_keys("")
    time.sleep(1)
    driver.find_element(By.ID, 'password').send_keys("")
    time.sleep(1)
    driver.find_element(By.ID, 'submit_button').click()
    driver.implicitly_wait(10)
    print("Giriş Başarılı")
    time.sleep(2)
except NoSuchElementException:
    print("Giriş elementleri bulunamadı.")

while True:
    driver.get("https://app.pandadoc.com/a/#/")
    driver.implicitly_wait(20)
    time.sleep(3) 
    
    # Airtable'dan verileri al
    params = {'view': view_name}
    response = requests.get(base_table_api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        records = [
            {
                'OgernciEmail': record['fields'].get('OgernciEmail', 'Bilinmiyor'),
                'Sözleşme Tipi': record['fields'].get('Sözleşme Tipi', 'Bilinmiyor'),
                'record_id': record['id']
            }
            for record in data.get('records', [])
        ]
        
        if records:
            for record in records:
                öemail = record['OgernciEmail']
                sozlesme_tipi = record['Sözleşme Tipi']
                record_id = record['record_id']
                
                print(f"Öğrenci mail={öemail}, Sözleşme Tipi={sozlesme_tipi}, Rec ID={record_id}")
        else:
            print("Kayıt bulunamadı. Yeniden denemek için bekleniyor...")
            continue  
    else:
        print(f"API isteği başarısız oldu. Durum kodu: {response.status_code}. Yeniden denemek için bekleniyor...")
        
    try:
        time.sleep(3) 
        input_element = driver.find_element(By.XPATH, "//button[contains(@class, 'Button-cgzqex-0 bcGtQn')]")
        driver.execute_script("arguments[0].click();", input_element)
        time.sleep(2)
        search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
        )

        # Search input alanına tıklama
        search_input.click()

        # Metni gönder
        baslik_deger = f"{öemail}"
        search_input.send_keys(baslik_deger)
        time.sleep(3)

        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{sozlesme_tipi}')]"))
        )
        ActionChains(driver).move_to_element(element).click().perform()

        # WebDriverWait kullanarak iframe'in yüklenmesini bekleyin
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "kolas-editor-iframe")))

        # iFrame'e geçiş yapın
        driver.switch_to.frame(iframe)

        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Text-sc-158xh7x-0"))
        )

        # İçindeki metni al
        text = element.find_element(By.CLASS_NAME, "ColoredText-bglvd-0").text
        print(text)
        time.sleep(1)
        tik(record_id, text)
        time.sleep(1)

        if mode == '2':  # If user selected to update link as well
            current_url = driver.current_url
            time.sleep(1)
            url(record_id)
            time.sleep(1)

        # Ana sayfaya geri dönün
        driver.switch_to.default_content()

    except TimeoutException:
        print(f"Hata: {sozlesme_tipi} öğesi bulunamadı veya tıklanamadı.")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

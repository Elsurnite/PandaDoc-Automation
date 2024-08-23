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
view_name = ''  # Buraya istediğiniz görünümün adını yazın
personal_access_token = ''
base_table_api_url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
headers = {
    'Authorization': f'Bearer {personal_access_token}',
}

def tik(record_id):
    update_url = f'{base_table_api_url}/{record_id}'
    data = {
        'fields': {
            'SozlesmeStatu': 'Done' 
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
                'AdSoyad': record['fields'].get('AdSoyad', 'Bilinmiyor'),
                'OgernciEmail': record['fields'].get('OgernciEmail', 'Bilinmiyor'),
                'DanısmanEmail': record['fields'].get('DanısmanEmail', 'Bilinmiyor'),
                'SozlesmeTipi': record['fields'].get('Sözleşme Tipi', 'Bilinmiyor'),
                'record_id': record['id']
            }
            for record in data.get('records', [])
        ]
        
        if records:
            for record in records:
                ad_soyad = record['AdSoyad']
                öemail = record['OgernciEmail']
                demail = record['DanısmanEmail']
                sozlesme_tipi = record['SozlesmeTipi']
                record_id = record['record_id']
                
                print(f"İşleniyor: AdSoyad={ad_soyad}, Öğrenci mail={öemail}, Danışman mail={demail}, Sözleşme Tipi={sozlesme_tipi}, Rec ID={record_id}")
        else:
            print("Kayıt bulunamadı. Yeniden denemek için bekleniyor...")
            continue  
    else:
        print(f"API isteği başarısız oldu. Durum kodu: {response.status_code}. Yeniden denemek için bekleniyor...")
        
    try:
        driver.get("https://app.pandadoc.com/a/#/")
        driver.implicitly_wait(20)
        time.sleep(3) 
        driver.get("https://app.pandadoc.com/a/#/dashboard?wizard-tab=quick_access&invocation-source=default")
        driver.implicitly_wait(20)
        time.sleep(3)   

        img_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f'//img[@alt="{sozlesme_tipi}"]'))
        )
        # Öğeye tıkla
        img_element.click()

        print(f"{sozlesme_tipi} metnini içeren öğeye tıklandı.")

        try:
            add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "Button-cgzqex-0") and contains(text(), "Add 1 item")]'))
            )
            add_button.click()
            try:
                input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'Input-sc-1kxjdmn-0.eemSBi.Input-sc-1qolfy6-0.rDetw'))
                )
                input_element.click()  # Input alanına tıklanıyor

                # Mevcut metni temizle
                input_element.clear()

                # Yeni metni gir
                baslik_deger = f"{ad_soyad} {sozlesme_tipi}"
                input_element.send_keys(baslik_deger)
                try:
                    Add_recipient = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'Input-sc-1kxjdmn-0.eAtPjM.Input-sc-1qolfy6-0.rDetw'))
                    )
                    Add_recipient.click()  # Input alanına tıklanıyor

                    # Mevcut metni temizle
                    Add_recipient.clear()

                    # Yeni metni gir
                    Add_recipient_deger = f"{öemail}"
                    Add_recipient.send_keys(Add_recipient_deger)
                    time.sleep(5)
                    Add_recipient.send_keys(Keys.RETURN)
                    time.sleep(1)
                    try:
                        FirstName = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@class="Item-sc-1rnphil-0 bTyiGW Line-sc-1sftx0m-0 fZCkwn"]//input[@name="firstName"]'))
                        ) 

                        full_name = f"{ad_soyad}"
                        first_name, middle_names, last_name = split_full_name(full_name)
                        FirstName.click()
                        print(f"First Name: {first_name}")
                        print(f"Middle Names: {middle_names}")
                        print(f"Last Name: {last_name}")

                        FirstName_deger = f"{first_name} {middle_names}"
                        FirstName.send_keys(FirstName_deger)

                        print("İsim girildi")
                        time.sleep(1)

                        LastName = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@class="Item-sc-1rnphil-0 bTyiGW Line-sc-1sftx0m-0 fZCkwn"]//input[@name="lastName"]'))
                        )

                        LastName_deger = f"{last_name}"
                        LastName.send_keys(LastName_deger)
                        print("Soyad girildi")
                        time.sleep(1)

                        add_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'styled__ActionsWrapper-sc-13e1ijg-4')]//button[contains(@class, 'Button-cgzqex-0') and contains(@class, 'PrimaryButton-sc-52bl8x-0')]"))
                        )
                        # Butona tıklama
                        add_button.click()
                        print(f"kişi oluşturuldu:{ad_soyad}")
                        time.sleep(5)

                        add_recipient_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '.styled__StyledAddRecipientButton-jKtSpI'))
                        )
                        # Butona tıklama
                        add_recipient_button.click()
                        time.sleep(2)
                        input_element_cc = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Start typing name, email or group"]'))
                        )
                        # Butona tıklayın
                        input_element_cc.click()
                        input_element_cc_deger = f"{demail}"
                        time.sleep(1)
                        input_element_cc.send_keys(input_element_cc_deger)
                        time.sleep(2)
                        input_element_cc.click()
                        time.sleep(1)
                        input_element_cc.send_keys(Keys.RETURN)
                        time.sleep(2)

                        continue_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="add_recipients_step__continue_button"]'))
                        )
                        # Butona tıklayın
                        continue_button.click()
                        driver.implicitly_wait(100)
                        print("bekleniyor")
                        time.sleep(10)
                        print("BEKLEME SÜRESİ BİTT")

                        # WebDriverWait kullanarak iframe'in yüklenmesini bekleyin
                        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "kolas-editor-iframe")))

                        # iFrame'e geçiş yapın
                        driver.switch_to.frame(iframe)

                        print("iframe'e girildi")
                        time.sleep(2)
                        
                        try: 
                            try:
                                # Butonu bekleyin ve tıklayın
                                close_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="close-dialog"]'))
                                )
                                close_button.click()
                                print("Butona tıklandı")
                                time.sleep(8)
                            except Exception:
                                print("Buton bulunamadı veya tıklanamadı:")

                            # Butonu bulup tıklayın
                            send_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.Button-cgzqex-0.iWkrqu.BaseButton-sc-7rutg1-0.PrimaryButton-sc-52bl8x-0.gNgDLB.cStaUW')))
                            driver.execute_script("arguments[0].click();", send_button)

                            email_sms_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='MenuItem__Content-xcdxyv-3 ticGK' and text()='Email / Text (SMS)']")))
                            email_sms_button.click()
                            time.sleep(10)
                        except Exception:
                            print("send_button bulunamadı veya tıklanamadı:")

                        continue_button2 = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="continue-button"]'))
                        )

                        # Butona tıklayın
                        continue_button2.click()

                        time.sleep(5)

                        saved_messages_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[text()="Saved messages"]'))
                        )

                        # Butona tıklayın
                        saved_messages_button.click()

                        time.sleep(10)

                        element = driver.find_element(By.XPATH, f"//span[text()='{sozlesme_tipi}']")
                        element.click()
                        print(f"{sozlesme_tipi}")

                        button = driver.find_element(By.XPATH, "//button[text()='Send document']")
                        button.click()
                        print("Sözleşme Gönderildi.")


                        # Ana sayfaya geri dönün
                        driver.switch_to.default_content()
                        tik(record_id)




                    except:
                        print("Kişi Sistemde Kayıtlı")
                        add_recipient_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '.styled__StyledAddRecipientButton-jKtSpI'))
                        )
                        # Butona tıklama
                        add_recipient_button.click()
                        time.sleep(2)
                        input_element_cc = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Start typing name, email or group"]'))
                        )
                        # Butona tıklayın
                        input_element_cc.click()
                        input_element_cc_deger = f"{demail}"
                        time.sleep(1)
                        input_element_cc.send_keys(input_element_cc_deger)
                        time.sleep(2)
                        input_element_cc.click()
                        time.sleep(1)
                        input_element_cc.send_keys(Keys.RETURN)
                        time.sleep(2)



                        continue_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="add_recipients_step__continue_button"]'))
                        )
                        # Butona tıklayın
                        continue_button.click()
                        driver.implicitly_wait(100)
                        print("bekleniyor")
                        time.sleep(10)
                        print("BEKLEME SÜRESİ BİTT")

                        # WebDriverWait kullanarak iframe'in yüklenmesini bekleyin
                        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "kolas-editor-iframe")))

                        # iFrame'e geçiş yapın
                        driver.switch_to.frame(iframe)

                        print("iframe'e girildi")

                        time.sleep(2)
                        try: 
                            try:
                                # Butonu bekleyin ve tıklayın
                                close_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="close-dialog"]'))
                                )
                                close_button.click()
                                print("Butona tıklandı")
                                time.sleep(8)
                            except Exception:
                                print("Buton bulunamadı veya tıklanamadı:")

                            # Butonu bulup tıklayın
                            send_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.Button-cgzqex-0.iWkrqu.BaseButton-sc-7rutg1-0.PrimaryButton-sc-52bl8x-0.gNgDLB.cStaUW')))
                            driver.execute_script("arguments[0].click();", send_button)

                            email_sms_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='MenuItem__Content-xcdxyv-3 ticGK' and text()='Email / Text (SMS)']")))
                            email_sms_button.click()
                            time.sleep(10)
                        except Exception:
                            print("send_button bulunamadı veya tıklanamadı:")

                        continue_button2 = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="continue-button"]'))
                        )

                        # Butona tıklayın
                        continue_button2.click()

                        time.sleep(5)

                        saved_messages_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[text()="Saved messages"]'))
                        )

                        # Butona tıklayın
                        saved_messages_button.click()

                        time.sleep(10)

                        element = driver.find_element(By.XPATH, f"//span[text()='{sozlesme_tipi}']")
                        element.click()
                        print(f"{sozlesme_tipi}")

                        button = driver.find_element(By.XPATH, "//button[text()='Send document']")
                        button.click()
                        print("Sözleşme Gönderildi.")


                        # Ana sayfaya geri dönün
                        driver.switch_to.default_content()
                        tik(record_id)

                except:
                    print("1. Kişi Seçilemedi")
            except:
                print("Dosya Adı Değiştirilemedi")

        except:
            print("Butona Tıklamak Başarılı Olmadı")

    except TimeoutException:
        print(f"Hata: {sozlesme_tipi} öğesi bulunamadı veya tıklanamadı.")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")
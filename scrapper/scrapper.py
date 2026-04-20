from selenium import webdriver
from selenium.webdriver.chrome import webdriver as w_chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import chromedriver_autoinstaller
from dotenv import load_dotenv
import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import re
from connect2 import connectDB 
import mariadb

load_dotenv()
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
url = os.getenv('PLATFORM')

broker_url = 'https://www.idx.co.id/id/anggota-bursa-dan-partisipan/profil-anggota-bursa'
stock_url = 'https://www.idx.co.id/id/perusahaan-tercatat/profil-perusahaan-tercatat/'
_get_master = False


class CheckChangesOnHTML():
    def __init__(self, locator, old_html):
        self.locator = locator
        self.old_html = old_html 

    def __call__(self, driver):
        called_html = driver.find_element(*self.locator).get_attribute('innerHTML')
        return called_html != self.old_html

def _build_driver()-> webdriver.Chrome :
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome()
    return driver 

def _login(driver: webdriver.Chrome)-> webdriver.Chrome:
    wait = WebDriverWait(driver, 15)
    driver.get(url)

    email_field = wait.until(
        EC.presence_of_element_located((By.ID, 'username'))
    )
    email_field.clear()
    email_field.send_keys(email)

    password_field = driver.find_element(By.ID, 'password')
    password_field.clear()
    password_field.send_keys(password)

    login_button = driver.find_element(By.ID, 'email-login-button')
    login_button.click()

    return driver  


# data saham atau broker bisa diambil lewat sini
def get_data_from_idx(driver: webdriver.Chrome, url: str, filename: str):
    driver.get(url)

    wait = WebDriverWait(driver, 15)
    btn_selectall = wait.until(
        EC.presence_of_element_located((By.NAME, 'perPageSelect'))
    )
    select = Select(btn_selectall)
    select.select_by_value("-1")

    table = driver.find_element(By.TAG_NAME, 'tbody')
    html = table.get_attribute('outerHTML')
    soup = BeautifulSoup(html, 'html.parser')
    datas = [[cell.text.strip() for cell in row.find_all('td')] for row in soup.find_all("tr")]

    df = pd.DataFrame(datas)
    df.to_csv(filename)       

def turn_float(s: str):
    multiplier = 1
    if 'B' in s:
        multiplier = 1_000_000_000
    elif 'M' in s:
        multiplier = 1_000_000    
    elif 'K' in s:
        multiplier = 1_000
    else:
        multiplier = 1        

    numeric = re.sub(r'[^0-9.]', '', s)
    return float(numeric) * multiplier           


def get_broker_summary(driver: webdriver.Chrome):
    driver.get(url)
    wait = WebDriverWait(driver, 60)

    btn_skip_avatar = wait.until(
        EC.presence_of_element_located((By.ID, 'modalnewavatar-button-skip'))
    )
    btn_skip_avatar.click()

    # masuk ke menu bandar detector
    driver.find_element(By.CSS_SELECTOR, "*[data-cy='right-menu-bandar_detector']").click()
    
    # tunggu hingga input untuk kode emiten muncul
    input_code = wait.until(
        EC.presence_of_element_located((By.ID, 'rc_select_2'))
    )    

    conn, cur = connectDB()    
    cur.execute('SELECT stock_symbol from stock_symbols')
    stocks = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
 
    first_date = date(2026, 4, 15)
    end_date = date.today()
    tbody = (By.XPATH, '//*[@id="rc-tabs-0-panel-BROKER_SUMMARY"]/div[2]/div/div/div/div/div/div/div[2]/table/tbody')

    dates = [first_date + timedelta(days=x) for x in range((end_date - first_date).days + 1)]    
    format = '%b %d, %Y'
      
    for x, dt in enumerate(dates):
        if dt.weekday() in (5,6):
            continue
        if x==0:
            input_stock = driver.find_element(By.XPATH, '//*[@id="rc_select_2"]')
            input_stock.send_keys('PTRO', Keys.ENTER) # -----> random pilih emiten agar formnya muncul
            driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-BROKER_SUMMARY"]/div[2]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[1]/td[1]/p').click() # --> random click agar dropodown hilang                                 
            driver.find_element(By.XPATH, '//*[@id="bandar-settings-default"]/div/div/div/div/div[2]').click() # ---> idk wtf is this
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="rc-tabs-0-panel-BROKER_SUMMARY"]/div[1]/div[2]/div[2]/div[3]/div[1]/span[2]'))).click() # ---> dropdown gross
            time.sleep(0.5)         
            driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-BROKER_SUMMARY"]/div[1]/div[2]/div[2]/div[3]/div[2]/div/div/div/div[2]/div/div/div/div[2]/div').click() # ---> tekan gross    
        

        pick_date = dt.strftime(format)      
        date_input1 = driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-BROKER_SUMMARY"]/div[1]/div[2]/div[1]/div[1]/div[1]/input')
        date_input1.click()
        date_input1.send_keys(Keys.CONTROL + "a")
        date_input1.send_keys(Keys.DELETE)
        time.sleep(0.25)
        date_input1.send_keys(pick_date, Keys.ENTER) # ---> Tanggal awal
        time.sleep(0.25)

        date_input2 = driver.find_element(By.XPATH, '//*[@id="rc-tabs-0-panel-BROKER_SUMMARY"]/div[1]/div[2]/div[1]/div[2]/div/input')
        date_input2.click()
        date_input2.send_keys(Keys.CONTROL + "a")
        date_input2.send_keys(Keys.DELETE)
        time.sleep(0.25)
        date_input2.send_keys(pick_date, Keys.ENTER) # ---> Tanggal akhir 
        time.sleep(0.25)

        temp = driver.find_element(*tbody).find_elements(By.TAG_NAME, 'tr')      
        if len(temp) <= 2: # -------> libur bursa
            continue      

        for stock in stocks:              
            try :
                input_stock = driver.find_element(By.XPATH, '//*[@id="rc_select_2"]')
                input_stock.send_keys(Keys.CONTROL + "a")
                input_stock.send_keys(Keys.DELETE) 
                time.sleep(0.25)                
                prev_html = driver.find_element(*tbody).get_attribute('innerHTML')             
                input_stock.send_keys(stock, Keys.ENTER)                        
                driver.find_element(By.XPATH, '//*[@id="widget-container"]/div[1]/div/div/div[2]/div[1]/div[1]/div/div[1]').click()  # ---> random click
                                                            
                # wait.until(CheckChangesOnHTML(tbody, prev_html))
                time.sleep(0.5)
                trows = driver.find_element(*tbody).find_elements(By.TAG_NAME, 'tr')
                if len(trows) <= 2: # ---> berati kosong dan kemungkinan libur bursa. tetap ada kemungkinan betul2 kosong. tapi sangat unlikely
                    continue

                all_texts = []        
                for row in trows[1:]:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    all_texts.append([c.get_attribute("textContent") for c in cells])                        
                    # dapetin per kolomnya
                    # 8 kolom, 4 kiri beli, 4 kanan jual            
                    # cells = row.find_elements(By.TAG_NAME, 'td')
                    # texts = [c.get_attribute("textContent") for c in cells]

                for texts in all_texts:
                    data_buy = []
                    data_sell = []

                    data_buy = texts[:4]
                    data_sell = texts[4:]

                    # untuk menangani data yang - di sebelah buy atau sell
                    if data_buy[0] is not None and data_buy[0] != '' and data_buy[0] != '-':
                        data_buy[1] = turn_float(str(data_buy[1]))
                        data_buy[2] = turn_float(str(data_buy[2]))
                        data_buy[3] = float(data_buy[3].replace(',', ''))

                    if data_sell[0] is not None and data_sell[0] != '' and data_sell[0] != '-':
                        data_sell[1] = turn_float(str(data_sell[1]))
                        data_sell[2] = turn_float(str(data_sell[2]))
                        data_sell[3] = float(data_sell[3].replace(',', ''))
                    
                    conn, cur = connectDB()
                    try:
                        if data_buy[0] is not None and data_buy[0] != '' and data_buy[0] != '-':
                            cur.execute(
                                """
                                INSERT INTO BROKER_SUMMARY(broker_code, value, total_lot, price_average, stock_symbol ,date_start, date_end, time_range, ACTION)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """
                                ,[*data_buy, stock, dt, dt, 'D', 'B']
                            )

                        if data_sell[0] is not None and data_sell[0] != '' and data_sell[0] != '-':
                            cur.execute(
                                """
                                INSERT INTO BROKER_SUMMARY(broker_code, value, total_lot, price_average, stock_symbol ,date_start, date_end, time_range, ACTION)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """
                                ,[*data_sell, stock, dt, dt, 'D', 'S']
                            )                            
                    except mariadb.Error as e:
                        print(f"ada error : {e}")
                        with open("error_log.txt", "a") as file:
                            file.write(f"[{datetime.now()}] ada error saat mengeksekusi saham {stock}. pada tanggal [{pick_date}]")                    
                    finally:
                        conn.commit()
                        cur.close()
                        conn.close()       
                        
                    

            except NoSuchElementException as e:
                print('ada error : ', e)
                input('ketik enter untuk lanjut . . . ')            

            except Exception as e:
                print('ada error : ', e)
                input('ketik enter untuk lanjut . . . ')
             

    input('ketik enter sudah berakhir')    


if __name__ == '__main__':
    driver = _build_driver()

    if _get_master :
        get_data_from_idx(driver, stock_url, 'daftar_saham_bei_' + str(date.strftime(date.today(),'%d_%m_%Y')) + '.csv')
        get_data_from_idx(driver, broker_url, 'daftar_broker_terdaftar_' + str(date.strftime(date.today(),'%d_%m_%Y')) + '.csv')
    #driver = _login(driver)
    get_broker_summary(driver)
    #_login(driver)
    
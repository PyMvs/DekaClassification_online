# LIBRARIES
from bs4 import BeautifulSoup
import os
import requests

# SELENIUM LIBRARIES
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions


# TELEGRAM INFORMATION
TOKEN_KEY = os.getenv("token_key") #SECRETS GITHUB
CHAT_ID = os.getenv("chat_id") #SECRETS GITHUB

# CHROME INFORMATION
web = "https://es.deka.fit/race-results/?eventid=266769"

# PERSONAL INFORMATION
MY_NAME = os.getenv("my_name") #SECRETS GITHUB
MY_GENDER = " " # M / F

############################
####    WEB SCRAPING    ####
############################

#service = Service(executable_path=path)

# Opciones de navegación
options = ChromeOptions()
options.add_argument("--headless")  # BACKGROUND

driver = webdriver.Chrome(options=options) # NO PATH, IT'S INNECESSARY IN MY COMPUTER

driver.get(web)

#DAMOS TIEMPO A CARGAR
time.sleep(10)

# PATHS
COMPETITIONS = {

    "DEKA STRONG": "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[2]/div[1]/div[2]/select/option[2]",
    "DEKA MILE": "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[2]/div[1]/div[2]/select/option[3]",
    "DEKA FIT": "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[2]/div[1]/div[2]/select/option[4]",
}

for comp, path in COMPETITIONS.items():

    select_competition = driver.find_element(By.XPATH, path)
    select_competition.click()
    
    time.sleep(2)
    
    if comp == "DEKA FIT":
        
        Select_Overall = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[2]/div[1]/div[3]/select/option[1]")
        Select_Overall.click()
    
        time.sleep(3)
    
        # Showing all participants
        Show_all_participants = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[4]/table/tbody[3]/tr/td/a[2]")
        Show_all_participants.click()   
    
        time.sleep(3)
    
        # Extrat element HTML to analyse
        html_data = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[4]/table/tbody[2]")
        html_data = html_data.get_attribute('outerHTML')
        
    else:

        # Showing all participants
        Show_all_participants = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[4]/table/tbody[5]/tr/td/a[2]")
        Show_all_participants.click()
    
        time.sleep(3)
    
        # ExtraCt element HTML to analyse
        html_data = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/main/div/article/section/div/div[4]/table/tbody[4]")
        html_data = html_data.get_attribute('outerHTML')

    soup = BeautifulSoup(html_data, 'html.parser')

    rows = soup.find_all('tr', class_ ='Hover LastRecordLine')

    count = 1

    print("\n  =======================")
    print("|| CLASIFICACIÓN - DEKA ||")
    print("  ======================\n")

    # PROCESS FOR EACH ROW & OBTAING REQUIRED DATA
    for row in rows:
        img_tag = row.find('img')
        if img_tag:
            pais = img_tag['src'].split('/')[-1].split('.')[0].upper()
        else:
            pais = "N/A"  # Or any other default value you want to assign when there is no 'img' tag

        nombre = row.find('td', style ='text-align: left;').find_next('td').find_next('td').text.strip()
        categoria = row.find('td', style ='text-align: left;').find_next('td').find_next('td').find_next('td').find_next('td').text.strip()
        tiempo = row.find_all('td', style ='text-align: left;')[-1].text.strip()

        # CREATE THE OUT CHAIN FOR EACH FILE AND SHOW IT
        output = f"{pais} - {nombre} - {categoria}. Tiempo: {tiempo}"

        if pais == "ES":
            if MY_GENDER in categoria:

                if nombre == MY_NAME: # SEARCH MY NAME AND SAVE IT TO SHOW IT LATER
                    my_position = count
                    my_time = tiempo

                count += 1

    try:
        if my_position == 0:
            raise ValueError("Position is 0, skipping requests.")
        
        percent_position = (1 - (my_position / count)) * 100

        requests.post("https://api.telegram.org/bot" + TOKEN_KEY + "/sendMessage", data={"chat_id": CHAT_ID, "text": "\n" + comp})
        requests.post("https://api.telegram.org/bot" + TOKEN_KEY + "/sendMessage", data={"chat_id": CHAT_ID, "text": f"\n\nPosición {my_position}/{count - 1} | Tiempo: {my_time}"})
        requests.post("https://api.telegram.org/bot" + TOKEN_KEY + "/sendMessage", data={"chat_id": CHAT_ID, "text": f"\nPor delante del {percent_position:.2f}% de todos los participantes"})
        requests.post("https://api.telegram.org/bot" + TOKEN_KEY + "/sendMessage", data={"chat_id": CHAT_ID, "text": f"\n---------------------------------------"})

    except:
        requests.post("https://api.telegram.org/bot" + TOKEN_KEY +"/sendMessage", data={"chat_id": CHAT_ID, "text": f"\nNo se encontró tu nombre en la clasificación de " + comp + ".  Vuelve a revisar tu nombre e inténtalo de nuevo"})

    # INITIALIZING NAME
    my_position = 0 

driver.close()

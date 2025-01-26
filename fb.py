import traceback
import json
import time
import os
from typing import List, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from difflib import SequenceMatcher

CATEGORIES = {
    2: "Veicoli", # Auto
    5: "Veicoli", # Accessori Auto
    3: "Veicoli", # Moto e Scooter",
    36: "Veicoli", # Accessori Moto",
    22: "Veicoli", # Nautica",
    34: "Veicoli", # Caravan e Camper",
    4: "Veicoli", # Veicoli commerciali",
    1: "Veicoli", # Tutto motori",
    9: "Elettronica e computer", # Elettronica",
    10: "Elettronica e computer", # Informatica",
    44: "Videogiochi", #"Console e Videogiochi",
    11: "Audio/Video",
    40: "Fotografia",
    12: "Telefonia",
    13: "Per la casa e la persona",
    14: "Arredamento e Casalinghi",
    37: "Elettrodomestici",
    15: "Giardino e Fai da te",
    16: "Abbigliamento e Accessori",
    17: "Neonati e bambini", # Tutto per i bambini",
    18: "Sports e hobby",
    23: "Animali",
    100: "Accessori per animali",
    19: "Musica e Film",
    38: "Libri e Riviste",
    39: "Strumenti Musicali",
    20: "Sports",
    41: "Biciclette",
    21: "Collezionismo",
    28: "Altri",
    7: "Appartamenti",
    43: "Camere/Posti letto",
    29: "Ville singole e a schiera",
    30: "Terreni e rustici",
    31: "Garage e box",
    32: "Loft, mansarde e altro",
    33: "Case vacanza",
    8: "Uffici e Locali commerciali",
    6: "Tutto immobili",
    26: "Offerte di lavoro",
    50: "Servizi",
    42: "Candidati in cerca di lavoro",
    25: "Attrezzature di lavoro",
    24: "Tutto lavoro"
}

GUI = {
    # LOGIN
    'non_accettare':          lambda d: d.find_element(By.XPATH, "//span[text()='Decline optional cookies']"),
    'email':                  lambda d: d.find_element(By.XPATH, "//input[@id=':r11:']"),
    'password':               lambda d: d.find_element(By.XPATH, "//input[@id=':r14:']"),
    'accedi':                 lambda d: d.find_element(By.XPATH, "//div[@aria-label='Accessible login button']"),
    'marketplace':            lambda d: d.find_element(By.XPATH, "//h1[normalize-space()='Marketplace']"), 

    # PAGE1
    'immagini':                 lambda d: d.find_element_by_css_selector('input[type="file"]'),
    'titolo':                   lambda d: d.find_element(By.XPATH, "//label[@aria-label='Titolo']/div/input"),
    'prezzo':                   lambda d: d.find_element(By.XPATH, "//label[@aria-label='Prezzo']/div/input"),
    'categoria':                lambda d: d.find_element(By.XPATH, "//label[contains(@aria-label,'Categoria')]"),
    'categorie':                lambda d: d.find_elements(By.XPATH, "//div[contains(@role,'button')]"),
    'descrizione':              lambda d: d.find_element(By.XPATH, "//label[@aria-label='Descrizione']/div/div/textarea"),
    'comune':                   lambda d: d.find_element(By.XPATH, "//label[@aria-label='Luogo']/div/input"),
    'condizione':               lambda d: d.find_element(By.XPATH, "//label[@aria-label='Condizione']"),
    'condizione_Nuovo':         lambda d: d.find_element(By.XPATH, "//span[text()='Nuovo']"),
    'condizione_ComeNuovo':     lambda d: d.find_element(By.XPATH, "//span[text()='Usato - Come nuovo']"),
    'condizione_Ottimo':        lambda d: d.find_element(By.XPATH, "//span[text()='Usato - Come nuovo']"),
    'condizione_Buono':         lambda d: d.find_element(By.XPATH, "//span[text()='Usato - Buono']"),
    'condizione_Danneggiato':   lambda d: d.find_element(By.XPATH, "//span[text()='Usato - Accettabile']"),
    'nascondi_numero':          lambda d: d.find_element(By.XPATH, "//span[text()='Nascondi agli amici']/ancestor::div[@role='button']"),
    'avanti':                   lambda d: d.find_element(By.XPATH, "//div[@aria-label='Avanti' and @role='button']"),

    # PAGE2
    'pubblica':                 lambda d: d.find_element(By.XPATH, "//div[@aria-label='Pubblica' and @role='button']"),
}

def get_gui(driver, name, retry=10) -> WebElement:
    count = 0
    while count < retry:
        time.sleep(0.5)
        count += 1
        try:
            return GUI[name](driver)
        except:
            pass
    raise Exception(f"Element {name} not found")

def get_guis(driver, name, retry=10) -> List[WebElement]:
    count = 0
    while count < retry:
        time.sleep(0.5)
        count += 1
        try:
            return GUI[name](driver)
        except:
            pass
    raise Exception(f"Elements {name} not found")
    
def type_text(driver, name, text):
    ui = get_gui(driver, name)
    # check string similarity
    while SequenceMatcher(None, ui.get_attribute("value").strip().lower(), text.strip().lower()).ratio() < 0.7:
        ui.click()
        ui.clear()
        ui.send_keys(text)
        time.sleep(1)

def login(driver):
    # Load session cookie if it exists
    cookie_file = r'resources/cookie_fb.json'
    credentials_file = r'resources/credentials_fb.json'
    url = 'https://www.facebook.com/marketplace/'
    
    first_access = True
    try:
      with open(cookie_file, 'r') as f:
        cookies = json.load(f)
        driver.get(url)
        for cookie in cookies:
          driver.add_cookie(cookie)
        driver.refresh()

      # Check if login was successful by looking for a specific element
      if get_gui(driver, 'marketplace'):
        print(f"Login successful with cookies")
        return
      else:
        first_access = False
    except Exception as e:
      print(f"Failed to load cookies: {e}")

    # If cookies are not present or login failed, proceed with normal login
    with open(credentials_file, 'r') as f:
      credentials = json.load(f)

    driver.get(url)
    
    # Answer to cookies policy
    if first_access:
      get_gui(driver, 'non_accettare').click()

    type_text(driver, 'email', credentials['EMAIL'])
    type_text(driver, 'password', credentials['PASSWORD'])
    get_gui(driver, 'accedi').click()
    time.sleep(0.5)
    print(f"Login successful with credentials")
    
    # Save session cookies
    print(f"Saving cookies to {cookie_file}")
    cookies = driver.get_cookies()
    with open(cookie_file, 'w') as f:
      json.dump(cookies, f)

def page1(driver, data):
    get_gui(driver, 'marketplace')
    driver.get(f'https://www.facebook.com/marketplace/create/item')

    type_text(driver, 'titolo', data['titolo'])

    if data['prezzo'] is None:
        get_gui(driver, 'prezzo').clear()
    else:
        type_text(driver, 'prezzo', data['prezzo'])

    get_gui(driver, 'immagini').send_keys('\n'.join(data['immagini']))


    # category
    get_gui(driver, 'categoria').click()
    category_selected = False
    for elem in get_guis(driver, 'categorie'):
        try:
            if str(elem.text.strip()).lower() == CATEGORIES[data['categoria']].strip().lower():
                elem.click()
                category_selected = True
                break
        except:
            pass
    if not category_selected:
        raise Exception(f"Category {data['categoria']} not found")

    get_gui(driver, 'condizione').click()
    get_gui(driver, f'condizione_{data["condizione"]}').click()
    
    type_text(driver, 'descrizione', data['descrizione'])

    type_text(driver, 'comune', data['comune'])
    time.sleep(0.3)
    get_gui(driver, 'comune').send_keys(Keys.DOWN)
    time.sleep(0.3)
    get_gui(driver, 'comune').send_keys(Keys.RETURN)
    time.sleep(0.3)
        
    nascondi_amici_checked = get_gui(driver, 'nascondi_numero').get_attribute('data-state') == 'checked'
    if nascondi_amici_checked and not data['nascondi_numero'] or not nascondi_amici_checked and data['nascondi_numero']:
        get_gui(driver, 'nascondi_numero').click()
    
    get_gui(driver, 'avanti').click()

def page2(driver):
    get_gui(driver, 'pubblica').click()

def setup()  -> WebDriver:
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--no-sandbox")
    user_data_dir = f"/tmp/firefox_user_data_{int(time.time())}"
    firefox_options.set_preference("profile", user_data_dir)
    firefox_options.set_preference("browser.in-content.dark-mode", True) 
    driver = webdriver.Firefox(firefox_options=firefox_options)
    driver.maximize_window()
    driver.delete_all_cookies()
    return driver

def publish(filepath_items) -> None:
    with open(filepath_items) as f:
        items = json.load(f)
    
    driver = setup()
    cwd = os.getcwd()

    login(driver)
    input('press ENTER to continue')

    for data in items:
      if data['pubblica_annuncio'] == False:
          print(f'[{data["id"]}] Skipping item')
          continue
      
      try:
          print(f'[{data["id"]}] Publishing item')
          data['immagini'] = [os.path.join(cwd, p) for p in data['immagini']]
          page1(driver, data)
          page2(driver)
      except Exception as e:
          traceback.print_exc()
          input('ERROR: press ENTER to continue with the next item')

    time.sleep(5)
    driver.quit()
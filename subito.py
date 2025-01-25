import traceback
import json
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from difflib import SequenceMatcher

CATEGORIES = {
    2: "Auto",
    5: "Accessori Auto",
    3: "Moto e Scooter",
    36: "Accessori Moto",
    22: "Nautica",
    34: "Caravan e Camper",
    4: "Veicoli commerciali",
    1: "Tutto motori",
    9: "Elettronica",
    10: "Informatica",
    44: "Console e Videogiochi",
    11: "Audio/Video",
    40: "Fotografia",
    12: "Telefonia",
    13: "Per la casa e la persona",
    14: "Arredamento e Casalinghi",
    37: "Elettrodomestici",
    15: "Giardino e Fai da te",
    16: "Abbigliamento e Accessori",
    17: "Tutto per i bambini",
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

TYPES = {
    'Auto': [], 
    'Accessori Auto': [], 
    'Moto e Scooter': [], 
    'Accessori Moto': [], 
    'Nautica': [], 
    'Caravan e Camper': [], 
    'Veicoli commerciali': [], 
    'Tutto motori': [], 
    'Elettronica': [], 
    'Informatica': ['NoteBook & Tablet', 'Computer Fissi', 'Accessori'], 
    'Console e Videogiochi': [], 
    'Audio/Video': ['TV', 'Lettori DVD', 'Radio/Stereo', 'Lettori MP3', 'Altro'], 
    'Fotografia': [], 
    'Telefonia': ['Cellulari e Smartphone', 'Accessori Telefonia', 'Fissi, Cordless e Altro'], 
    'Per la casa e la persona': [], 
    'Arredamento e Casalinghi': [], 
    'Elettrodomestici': [], 
    'Giardino e Fai da te': [], 
    'Abbigliamento e Accessori': ['Scarpe', 'Borse', 'Orologi e Gioielli', 'Polo e t-shirt', 'Pantaloni', 'Gonne', 'Felpe e maglioni', 'Giacche e giubbotti', 'Vestiti completi', 'Intimo', 'Accessori', 'Altro'], 
    'Tutto per i bambini': ['Abbigliamento Bimbi', "Prodotti per l'infanzia", 'Giochi'], 
    'Sports e hobby': [], 
    'Animali': [], 
    'Accessori per animali': [], 
    'Musica e Film': [], 
    'Libri e Riviste': ['Letteratura e Narrativa', 'Gialli e Thriller', 'Biografie', 'Storia', 'Cucina', 'Fumetti', 'Libri per bambini', 'Libri scolastici e universitari', 'Altro'], 
    'Strumenti Musicali': [], 
    'Sports': ['Calcio', 'Palestra', 'Basket', 'Volley', 'Sci e Snowboard', 'Ciclismo', 'Acquatici', 'Golf', 'Motori', 'Outdoor', 'Altro'], 
    'Biciclette': ['Uomo', 'Donna', 'Bimbo', 'MTB e Touring', 'Corsa', 'Pieghevoli', 'BMX', 'Scatto fisso e single speed', 'Componenti e abbigliamento', 'Altre tipologie'], 
    'Collezionismo': ['Francobolli', 'Monete', 'Editoria', 'Carte e Schede', 'Modellismo', 'Cartoline', 'Militaria', 'Modernariato', 'Bambole', 'Altro'], 
    'Altri': [], 
    'Appartamenti': [], 
    'Camere/Posti letto': [], 
    'Ville singole e a schiera': [], 
    'Terreni e rustici': [], 
    'Garage e box': [], 
    'Loft, mansarde e altro': [], 
    'Case vacanza': [], 
    'Uffici e Locali commerciali': [], 
    'Tutto immobili': [], 
    'Offerte di lavoro': [], 
    'Servizi': [], 
    'Candidati in cerca di lavoro': [], 
    'Attrezzature di lavoro': [], 
    'Tutto lavoro': []
}

GUI = {
    # LOGIN
    'accetta':                lambda d: d.find_element(By.ID, 'didomi-notice-agree-button'),
    'non_accettare':          lambda d: d.find_element(By.CLASS_NAME, 'didomi-continue-without-agreeing'),
    'email':                  lambda d: d.find_element(By.ID, 'username'),
    'password':               lambda d: d.find_element(By.ID, 'password'),
    'accedi':                 lambda d: d.find_elements(By.XPATH, '//button[@type="submit"]')[0],
    'i_tuoi_annunci':         lambda d: d.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[2]/ul/li[1]/a/span')[0], 

    # PAGE1
    'immagini':                 lambda d: d.find_element(By.ID, 'file-input'),
    'tipo_di_annuncio_Vendita': lambda d: d.find_elements_by_xpath('//label[text()="In vendita"]')[0],
    'tipo_di_annuncio_Regalo':  lambda d: d.find_elements_by_xpath('//label[text()="In regalo"]')[0],
    'titolo':                   lambda d: d.find_element(By.ID, 'title'),
    'descrizione':              lambda d: d.find_element(By.ID, 'description'),
    'comune':                   lambda d: d.find_element(By.ID, 'location'),
    'condizione':               lambda d: d.find_elements_by_xpath('//*[@id="__next"]/div/main/div[2]/form/div/section[5]/div[2]/div/div/div/div')[0],
    'condizione_Nuovo':         lambda d: d.find_elements_by_xpath('//*[@id="itemCondition__option--0"]')[0],
    'condizione_ComeNuovo':     lambda d: d.find_elements_by_xpath('//*[@id="itemCondition__option--1"]')[0],
    'condizione_Ottimo':        lambda d: d.find_elements_by_xpath('//*[@id="itemCondition__option--2"]')[0],
    'condizione_Buono':         lambda d: d.find_elements_by_xpath('//*[@id="itemCondition__option--3"]')[0],
    'condizione_Danneggiato':   lambda d: d.find_elements_by_xpath('//*[@id="itemCondition__option--4"]')[0],
    'prezzo':                   lambda d: d.find_element(By.ID, 'price'),
    'spedizione':               lambda d: d.find_element(By.ID, 'itemShippable'),
    'spedizione_TuttoSubito':   lambda d: d.find_elements_by_xpath('//label[@aria-label="Spedizione con TuttoSubito"]/div[@class="ListItemRadio_radio__eriFK"]')[0],
    'spedizione_Piccolo':       lambda d: d.find_elements_by_xpath('//label[@aria-label="Piccolo (Massimo 2kg)"]')[0],
    'spedizione_Medio':         lambda d: d.find_elements_by_xpath('//label[@aria-label="Medio (Massimo 5kg)"]')[0],
    'spedizione_Grande':        lambda d: d.find_elements_by_xpath('//label[@aria-label="Grande (Massimo 15kg)"]')[0],
    'spedizione_Maxi':          lambda d: d.find_elements_by_xpath('//label[@aria-label="Maxi (Massimo 20kg)"]')[0],
    'spedizione_GestitaDaTe':   lambda d: d.find_elements_by_xpath('//label[@aria-label="Spedizione gestita da te (pacchi ingombranti)"]/div[@class="ListItemRadio_radio__eriFK"]')[0],
    'costi_di_spedizione':      lambda d: d.find_element(By.ID, 'itemShippingCost'),
    'telefono':                 lambda d: d.find_element(By.ID, 'phone'),
    'nascondi_numero':          lambda d: d.find_element(By.ID, 'phoneHidden'),
    'inserzionista_Privato':    lambda d: d.find_elements_by_xpath('//label[text()="Privato"]')[0],
    'inserzionista_Azienda':    lambda d: d.find_elements_by_xpath('//label[text()="Azienda"]')[0],
    'continua':                 lambda d: d.find_elements_by_xpath('//*[@id="__next"]/div/main/div[2]/form/section/button')[0],
    'fascia_di_eta':            lambda d: d.find_elements_by_xpath('//body/div[@id="__next"]/div[@class="Layout_layout__fOhwR"]/main[@class="Layout_main__Ybyix"]/div[@class="Form_form-wrapper__Ue0H5"]/form[@aria-label="form"]/div[@class="Form_inputs-wrapper__1fBgX"]/section[7]/div[2]/div[1]/div[1]/div[1]/div[1]')[0],
    'fascia_di_eta_0_12_mesi':  lambda d: d.find_elements_by_xpath('//*[@id="childrenAge__option--0"]')[0],
    'fascia_di_eta_1_3_anni':   lambda d: d.find_elements_by_xpath('//*[@id="childrenAge__option--1"]')[0],
    'fascia_di_eta_3_6_anni':   lambda d: d.find_elements_by_xpath('//*[@id="childrenAge__option--2"]')[0],
    'fascia_di_eta_6_12_anni':  lambda d: d.find_elements_by_xpath('//*[@id="childrenAge__option--3"]')[0],
    'fascia_di_eta_altro':      lambda d: d.find_elements_by_xpath('//*[@id="childrenAge__option--4"]')[0],

    # PAGE2
    'pubblica_annuncio':        lambda d: d.find_elements_by_xpath('//button[normalize-space()="Pubblica annuncio"]')[0],

    # PAGE3
    'page3_continua':           lambda d: d.find_elements_by_xpath('//button[normalize-space()="Continua"]')[0],

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
    
def type_text(driver, name, text):
    ui = get_gui(driver, name)
    # check string similarity
    while SequenceMatcher(None, ui.get_attribute("value").strip().lower(), text.strip().lower()).ratio() < 0.8:
        ui.click()
        ui.clear()
        ui.send_keys(text)
        time.sleep(1)

def login(driver):
    # Load session cookie if it exists
    cookie_file = r'resources/cookie.json'
    credentials_file = r'resources/credentials.json'
    url = 'https://areariservata.subito.it/login_form'

    first_access = True
    try:
      with open(cookie_file, 'r') as f:
        cookies = json.load(f)
        driver.get(url)
        for cookie in cookies:
          driver.add_cookie(cookie)
        driver.refresh()

      # Check if login was successful by looking for a specific element
      if get_gui(driver, 'i_tuoi_annunci'):
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
    time.sleep(1)
    print(f"Login successful with credentials")
    
    # Save session cookies
    print(f"Saving cookies to {cookie_file}")
    cookies = driver.get_cookies()
    with open(cookie_file, 'w') as f:
      json.dump(cookies, f)

def page1(driver, data):
    get_gui(driver, 'i_tuoi_annunci')
    driver.get(f'https://inserimento.subito.it/?category={str(data["categoria"])}&type={str(data["tipologia"])}&from=vendere#insert')

    get_gui(driver, 'immagini').send_keys('\n'.join(data['immagini']))
    get_gui(driver, f'tipo_di_annuncio_{data["tipo_di_annuncio"]}').click()
    
    type_text(driver, 'titolo', data['titolo'])
    type_text(driver, 'descrizione', data['descrizione'])
    get_gui(driver, 'condizione').click()
    get_gui(driver, f'condizione_{data["condizione"]}').click()

    if 'fascia_di_eta' in data:
        get_gui(driver, 'fascia_di_eta').click()
        get_gui(driver, f'fascia_di_eta_{data["fascia_di_eta"]}').click()

    type_text(driver, 'comune', data['comune'])
    get_gui(driver, 'comune').send_keys(Keys.RETURN)

    if data['prezzo'] is None:
        get_gui(driver, 'prezzo').clear()
    else:
        type_text(driver, 'prezzo', data['prezzo'])
    
    if data['spedizione'] == 'TuttoSubito':
        get_gui(driver, 'spedizione_TuttoSubito').click()
        get_gui(driver, f'spedizione_{data["dimensioni"]}').click()
    elif data['spedizione'] == 'GestitaDaTe':
        get_gui(driver, 'spedizione_GestitaDaTe').click()
        type_text(driver, 'costi_di_spedizione', data['costi_di_spedizione'])
    else:
        get_gui(driver, 'spedizione').click()
        
    type_text(driver, 'telefono', data['telefono'])
    nascondi_numero_checked = get_gui(driver, 'nascondi_numero').get_attribute('data-state') == 'checked'
    if nascondi_numero_checked and not data['nascondi_numero'] or not nascondi_numero_checked and data['nascondi_numero']:
        get_gui(driver, 'nascondi_numero').click()

    # get_gui(driver, f'inserzionista_{data['inserzionista']}').click()
    
    get_gui(driver, 'continua').click()

def page2(driver):
    get_gui(driver, 'pubblica_annuncio').click()

def page3(driver):
    get_gui(driver, 'page3_continua').click()

def publish(filepath_items) -> None:
    with open(filepath_items) as f:
        items = json.load(f)
    
    # Configure Firefox options
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--no-sandbox")
    user_data_dir = f"/tmp/firefox_user_data_{int(time.time())}"
    firefox_options.set_preference("profile", user_data_dir)
    firefox_options.set_preference("browser.in-content.dark-mode", True) 
    driver = webdriver.Firefox(firefox_options=firefox_options)
    driver.maximize_window()
    driver.delete_all_cookies()

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
          page3(driver)
      except Exception as e:
          traceback.print_exc()
          input('ERROR: press ENTER to continue with the next item')

    time.sleep(5)
    driver.quit()
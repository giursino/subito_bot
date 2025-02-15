import json
import os
import sys
import shutil
import time
import random
import string
import traceback
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from tkinter.filedialog import askopenfilenames
from PIL import Image, ImageDraw, ImageFont

from utils import *

filepath_items = r'resources/items.json'
filepath_template = r'resources/template.json'

def publish() -> None:
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
    input('continue?')

    for data in items:
      try:
          data['immagini'] = [os.path.join(cwd, p) for p in data['immagini']]
          page1(driver, data)
          page2(driver)
          page3(driver)
      except Exception as e:
          traceback.print_exc()
          input('continue with next item?')

    time.sleep(5)
    input('exit?')
    driver.quit()

def create_new_adv():
    with open(filepath_items) as f:
        items = json.load(f)

    with open(filepath_template) as f:
        template = json.load(f)

    for key in template.keys():
        OK  = False
        while not OK:
            try:
                value = ''
                if key == 'id':
                    value = input(key + ' (unique)?: ').lower()
                elif key == 'categoria':
                    print('OPTIONS:', '\n'.join([f'{k:<5}: {v}' for k, v in CATEGORIES.items()]), sep='\n')
                    value = int(input(f'{key}? '))
                    assert value in CATEGORIES
                elif key == 'tipologia':
                    options = TYPES[CATEGORIES[template['categoria']]]
                    if len(options) > 0:
                        print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                        value = int(input(f'{key}? '))
                        value = value + 1
                    else:
                        value = 1
                elif key == 'immagini':
                    paths = askopenfilenames()
                    relpath = os.path.join('resources', template['id'])
                    os.makedirs(relpath)
                    paths_new = [os.path.join(relpath, f'{id}{os.path.splitext(p)[1]}') for id, p in enumerate(paths)]
                    for src, dst in zip(paths, paths_new):
                        shutil.copyfile(src, dst)
                    value = paths_new
                elif key == 'tipo_di_annuncio':
                    options = ['Regalo', 'Vendita']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = int(input(f'{key}? '))
                    value = options[value]
                elif key == 'condizione':
                    options = ['Nuovo', 'ComeNuovo', 'Ottimo', 'Buono', 'Danneggiato']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = int(input(f'{key}? '))
                    value = options[value]
                elif key == 'fascia_di_eta':
                    options = ['0_12_mesi', '1_3_anni', '3_6_anni', '6_12_anni', 'altro']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = int(input(f'{key}? '))
                    value = options[value]
                elif key == 'spedizione':
                    options = ['Nessuna', 'TuttoSubito', 'GestitaDaTe']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = input(f'{key}? ')
                    if value == '':
                        value = options[0]
                    else:
                        value = options[int(value)]
                elif key == 'dimensioni':
                    if template['spedizione'] == 'TuttoSubito':
                        options = ['Piccolo', 'Medio', 'Grande', 'Maxi']
                        print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                        value = int(input(f'{key}? '))
                        value = options[value]
                elif key == 'costi_di_spedizione':
                    if template['spedizione'] == 'GestitaDaTe':
                        value = input(f'{key}? ')
                elif key == 'nascondi_numero':
                    value = True
                elif key == 'inserzionista':
                    value = 'Privato'
                else:
                    value = input(f'{key} (default: {template[key]})? ')
                    if value == '':
                        value =  template[key]

                template[key] = value
                OK  = True
            except Exception as e:
                print(e)

    # remove duplicated ids
    items = [x for x in items if x['id'] != template['id']]
    items.append(template)

    # backup old items file
    timestr = time.strftime("%Y%m%d%H%M%S")
    backup_items_file = os.path.join(os.path.dirname(filepath_items), f"{timestr}_{os.path.basename(filepath_items)}")
    shutil.copyfile(filepath_items, backup_items_file)

    # overwrite items file
    with open(filepath_items, 'w') as f:
        json.dump(items, f, indent=2)

def list_advs():
    with open(filepath_items) as f:
        items = json.load(f)

    for idx, item in enumerate(items):
        print(f'{idx :<3}: {item["id"]}')

def update_advs():
    with open(filepath_items) as f:
        items = json.load(f)

    def generate_random_string(length=6):
        letters_and_digits = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    timestr = time.strftime("%Y%m%d%H%M%S")

    for item in items:
        # Trova il suffisso esistente nel titolo e nella descrizione
        existing_suffix = None
        if ' - ' in item['titolo']:
            existing_suffix = item['titolo'].split(' - ')[-1]

        # Genera un nuovo suffisso
        suffix = generate_random_string()

        # Aggiorna il titolo e la descrizione con il suffisso
        item['titolo'] = f"{item['titolo'].split(' - ')[0]} - {suffix}"
        item['descrizione'] = f"{item['descrizione'].split(' - ')[0]} - {suffix}"


        # Aggiorna le immagini con il suffisso esistente o nuovo
        for img_path in item['immagini']:
            
            original_img_file = os.path.join(os.path.dirname(img_path), f"original_{os.path.basename(img_path)}")
            
            if not existing_suffix: shutil.copyfile(img_path, original_img_file)

            # Aggiungi il suffisso all'immagine e salvala
            add_text_to_image(original_img_file, img_path, suffix)

    # Backup del vecchio file items
    backup_items_file = os.path.join(os.path.dirname(filepath_items), f"{timestr}_{os.path.basename(filepath_items)}")
    shutil.copyfile(filepath_items, backup_items_file)

    # Sovrascrivi il file items
    with open(filepath_items, 'w') as f:
        json.dump(items, f, indent=2)


def add_text_to_image(input_image_path, output_image_path, text):
    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    textbbox = draw.textbbox((0, 0), text, font=font)
    textwidth = textbbox[2] - textbbox[0]
    textheight = textbbox[3] - textbbox[1]
    width, height = image.size
    x = width - textwidth - 10
    y = height - textheight - 10
    draw.text((x, y), text, font=font, fill=(0, 0, 0))
    image.save(output_image_path)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'add':
        create_new_adv()
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'list':
        list_advs()
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'update':
        update_advs()
    else:
        publish()

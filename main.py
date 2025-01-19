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
          input('ERROR: continue with the next item?')

    time.sleep(5)
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
                    paths = askopenfilenames(title="Select images", multiple=True)
                    relpath = os.path.join('resources', template['id'])
                    os.makedirs(relpath, exist_ok=True)
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
        print(f'{idx :<3}: [{item["id"]}] {item["titolo"]}')

def update_advs():
    with open(filepath_items) as f:
        items = json.load(f)

    def generate_random_string(length=6):
        letters_and_digits = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    timestr = time.strftime("%Y%m%d%H%M%S")

    for item in items:
        # Find the existing suffix in the title and description
        existing_suffix = None
        if 'SKU:' in item['titolo']:
            existing_suffix = item['titolo'].split('SKU:')[-1].strip()

        # Generate a new suffix
        suffix = generate_random_string()

        # Update the title and description with the suffix
        item['titolo'] = f"{item['titolo'].split('SKU:')[0].strip()} SKU:{suffix}"
        item['descrizione'] = f"{item['descrizione'].split('SKU:')[0].strip()} SKU:{suffix}"

        # Update the images with the existing or new suffix
        for img_path in item['immagini']:
            original_img_file = os.path.join(os.path.dirname(img_path), f"original_{os.path.basename(img_path)}")
            if not existing_suffix:
                shutil.copyfile(img_path, original_img_file)

            # Add the suffix to the image and save it
            add_text_to_image(original_img_file, img_path, suffix)

    # Backup the old items file
    backup_items_file = os.path.join(os.path.dirname(filepath_items), f"{timestr}_{os.path.basename(filepath_items)}")
    shutil.copyfile(filepath_items, backup_items_file)

    # Overwrite the items file
    with open(filepath_items, 'w') as f:
        json.dump(items, f, indent=2)


def add_text_to_image(input_image_path, output_image_path, text):
  image = Image.open(input_image_path).convert("RGBA")
  txt = Image.new("RGBA", image.size, (255, 255, 255, 0))

  draw = ImageDraw.Draw(txt)
  font = ImageFont.truetype("DejaVuSans-Bold", 32)
  textbbox = draw.textbbox((0, 0), text, font=font)
  textwidth = textbbox[2] - textbbox[0]
  textheight = textbbox[3] - textbbox[1]
  width, height = image.size
  # Ensure the textbox is 80% of the image size
  max_textwidth = width * 0.8
  max_textheight = height * 0.8

  while (textwidth > max_textwidth or textheight > max_textheight) and font.size > 12:
    font = ImageFont.truetype("DejaVuSans-Bold", font.size - 1)
    textbbox = draw.textbbox((0, 0), text, font=font)
    textwidth = textbbox[2] - textbbox[0]
    textheight = textbbox[3] - textbbox[1]

  # Randomize the position ensuring the text does not go out of the image
  # and is either at the top or bottom of the image, not in the center 80%
  y_positions = list(range(0, int(height * 0.20))) + list(range(int(height * 0.80), height - textheight))
  x = random.randint(0, width - textwidth)
  y = random.choice(y_positions)

  # Draw the text with a shadow (emboss effect)
  shadow_color = (0, 0, 0, 128)
  draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)

  # Draw the text with semi-transparent fill
  text_color = (255, 255, 255, 128)
  draw.text((x, y), text, font=font, fill=text_color)

  watermarked = Image.alpha_composite(image, txt)
  watermarked = watermarked.convert("RGB")

  # Save the image in JPEG format
  watermarked.save(output_image_path, format='JPEG')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'add':
        create_new_adv()
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'list':
        list_advs()
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'update':
        update_advs()
    else:
        publish()

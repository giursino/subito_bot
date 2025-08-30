import json
import os
import sys
import shutil
import time
import random
import string
from tkinter.filedialog import askopenfilenames
from PIL import Image, ImageDraw, ImageFont

import subito
import fb

filepath_items = r'resources/items.json'
filepath_template = r'resources/template.json'

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
                    print('OPTIONS:', '\n'.join([f'{k:<5}: {v}' for k, v in subito.CATEGORIES.items()]), sep='\n')
                    value = int(input(f'{key}? '))
                    assert value in subito.CATEGORIES
                elif key == 'tipologia':
                    options = subito.TYPES[subito.CATEGORIES[template['categoria']]]
                    if len(options) > 0:
                        print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                        value = int(input(f'{key}? '))
                        value = value + 1
                    else:
                        value = 1
                elif key == 'immagini':
                    paths = askopenfilenames(title="Select images")
                    relpath = os.path.join('resources', template['id'])
                    os.makedirs(relpath, exist_ok=True)
                    paths_new = [os.path.join(relpath, f'{id}{os.path.splitext(p)[1]}') for id, p in enumerate(paths)]
                    for src, dst in zip(paths, paths_new):
                        shutil.copyfile(src, dst)
                    value = paths_new
                elif key == 'tipo_di_annuncio':
                    options = ['Regalo', 'Vendita']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = input(f'{key} (default: {options.index(template[key])})? ')
                    if value == '': value = options.index(template[key])
                    value = options[int(value)]
                elif key == 'condizione':
                    options = ['Nuovo', 'ComeNuovo', 'Ottimo', 'Buono', 'Danneggiato']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = input(f'{key} (default: {options.index(template[key])})? ')
                    if value == '': value = options.index(template[key])
                    value = options[int(value)]
                elif key == 'fascia_di_eta':
                    if subito.CATEGORIES[template['categoria']] == "Tutto per i bambini":
                      options = ['0_12_mesi', '1_3_anni', '3_6_anni', '6_12_anni', 'altro']
                      print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                      value = input(f'{key} (default: {options.index(template[key])})? ')
                      if value == '': value = options.index(template[key])
                      value = options[int(value)]
                elif key == 'spedizione':
                    options = ['Nessuna', 'TuttoSubito', 'GestitaDaTe']
                    print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                    value = input(f'{key} (default: {options.index(template[key])})? ')
                    if value == '': value = options.index(template[key])
                    value = options[int(value)]
                elif key == 'dimensioni':
                    if template['spedizione'] == 'TuttoSubito':
                        options = ['Piccolo', 'Medio', 'Grande', 'Maxi']
                        print('OPTIONS:', '\n'.join([f'{id:<5}: {t}' for id, t in enumerate(options)]), sep='\n')
                        value = input(f'{key} (default: {options.index(template[key])})? ')
                        if value == '': value = options.index(template[key])
                        value = options[int(value)]
                elif key == 'costi_di_spedizione':
                    if template['spedizione'] == 'GestitaDaTe':
                        value = input(f'{key} (default: {template[key]})? ')
                        if value == '': value = template[key]
                elif key == 'nascondi_numero':
                    value = True
                elif key == 'inserzionista':
                    value = 'Privato'
                elif key == 'pubblica_annuncio':
                    value = True
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

  active_items = [item for item in items if item.get("pubblica_annuncio") is True]
  inactive_items = [item for item in items if item.get("pubblica_annuncio") is False]

  print("Publishable Advertisements:")
  for idx, item in enumerate(active_items):
    print(f'- {item["id"] :<15}: {item["titolo"]}')

  print("\nUnpublishable Advertisements:")
  for idx, item in enumerate(inactive_items):
    print(f'- {item["id"] :<15}: {item["titolo"]}')

def update_advs():
    with open(filepath_items) as f:
        items = json.load(f)

    def generate_random_string(length=6):
        letters_and_digits = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    timestr = time.strftime("%Y%m%d%H%M%S")

    for item in items:
        # Check if the SKU key exists in the item and is not an empty string
        existing_sku = 'sku' in item and item['sku'] != ''

        # Generate a new sku
        sku = generate_random_string()

        # Backup the original title and description
        if not existing_sku:
            item['titolo_originale'] = item['titolo']
            item['descrizione_originale'] = item['descrizione']

        # Update the title and description with the original price and sku
        original_price = f"\nPrezzo nuovo: {item['prezzo_listino']} €" if 'prezzo_listino' in item else ""
        item['titolo'] = f"{item['titolo_originale']} SKU:{sku}"
        item['descrizione'] = f"{item['descrizione_originale']}{original_price}\nSKU:{sku}"
        item['sku'] = sku

        # Update the images with the existing or new sku
        for img_path in item['immagini']:
            original_img_file = os.path.join(os.path.dirname(img_path), f"original_{os.path.basename(img_path)}")
            if not existing_sku:
                shutil.copyfile(img_path, original_img_file)

            # Add the suffix to the image and save it
            add_text_to_image(original_img_file, img_path, sku)

    # Backup the old items file
    backup_items_file = os.path.join(os.path.dirname(filepath_items), f"{timestr}_{os.path.basename(filepath_items)}")
    shutil.copyfile(filepath_items, backup_items_file)

    # Overwrite the items file
    with open(filepath_items, 'w') as f:
        json.dump(items, f, indent=2)

def restore_advs():
  with open(filepath_items) as f:
    items = json.load(f)

  for item in items:
    if 'titolo_originale' in item and 'descrizione_originale' in item:
      item['titolo'] = item['titolo_originale']
      item['descrizione'] = item['descrizione_originale']
      del item['titolo_originale']
      del item['descrizione_originale']
    if 'sku' in item:
      del item['sku']

    # Restore original images
    for img_path in item['immagini']:
      original_img_file = os.path.join(os.path.dirname(img_path), f"original_{os.path.basename(img_path)}")
      if os.path.exists(original_img_file):
        shutil.copyfile(original_img_file, img_path)
        os.remove(original_img_file)

  # Backup the old items file
  timestr = time.strftime("%Y%m%d%H%M%S")
  backup_items_file = os.path.join(os.path.dirname(filepath_items), f"{timestr}_{os.path.basename(filepath_items)}")
  shutil.copyfile(filepath_items, backup_items_file)

  # Overwrite the items file
  with open(filepath_items, 'w') as f:
    json.dump(items, f, indent=2)

def remove_unpublishable_advs():
    with open(filepath_items) as f:
        items = json.load(f)

    # Mostra gli item attuali
    list_advs()

    # Trova gli item non pubblicabili
    to_remove = [item for item in items if item.get("pubblica_annuncio") is False]
    
    if not to_remove:
        print("No items to remove.")
        return

    print("The unpublished items will be removed.")

    confirm = input("Are you sure you want to remove these items? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    # Backup del file originale
    timestr = time.strftime("%Y%m%d%H%M%S")
    backup_items_file = os.path.join(os.path.dirname(filepath_items), f"{timestr}_{os.path.basename(filepath_items)}")
    shutil.copyfile(filepath_items, backup_items_file)

    # Crea una nuova lista senza gli item non pubblicabili
    items = [item for item in items if item.get("pubblica_annuncio") is True]

    # Sovrascrivi il file
    with open(filepath_items, 'w') as f:
        json.dump(items, f, indent=2)

    print(f"Removed {len(to_remove)} items. Backup created at {backup_items_file}")

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
  y_positions = list(range(0, int(height * 0.20))) + list(range(int(height * 0.80), int(height - textheight)))
  x = random.randint(0, int(width - textwidth))
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

  def print_help():
    print("Usage: python main.py [options] [command]")
    print("Options:")
    print("  --help, -h    Show this help message")
    print("Commands:")
    print("  add                Create a new advertisement")
    print("  list               List all advertisements")
    print("  update             Update advertisements with a new SKU")
    print("  restore            Restore advertisements to original state")
    print("  remove_unpub       Remove all unpublishable advertisements from the list")
    print("  publish PLATFORM   Publish advertisements to a platform")
    print("Platforms:")
    print("  subito             Publish to Subito")
    print("  fb                 Publish to Facebook")

  if len(sys.argv) > 1:
    command = sys.argv[1].lower()
    if command in ['--help', '-h']: print_help()
    elif command == 'add': create_new_adv()
    elif command == 'list': list_advs()
    elif command == 'update': update_advs()
    elif command == 'restore': restore_advs()
    elif command == 'remove_unpub': remove_unpublishable_advs()
    elif command == 'publish' and len(sys.argv) > 2:
      platform = sys.argv[2].lower()
      if platform == 'subito':
        subito.publish(filepath_items)
      elif platform == 'fb':
        fb.publish(filepath_items)
      else:
        print("ERROR: Unknown platform.")
        print_help()
    else:
      print("ERROR: Unknown command.")
      print_help()
  else:
    print("ERROR: No command provided.")
    print_help()
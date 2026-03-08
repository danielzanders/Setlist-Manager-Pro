import configparser
import os

CONFIG_FILE = 'config.ini'

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
        return dict(config['SETTINGS'])
    return {}

def save_config(key, folder, excel_path, complete, last_count=0):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {
        'key': key,
        'folder': folder,
        'excel_path': excel_path,
        'complete': str(complete),
        'last_line_count': str(last_count)
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

def is_config_complete():
    c = load_config()
    return c.get('complete') == 'True' and os.path.exists(c.get('excel_path', ''))

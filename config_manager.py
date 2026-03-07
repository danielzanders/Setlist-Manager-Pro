import configparser
import os

CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
        if 'SETTINGS' in config:
            return dict(config['SETTINGS'])
    return {}

def save_config(api_key, folder, excel_path, auto_check, last_count=0):
    config = configparser.ConfigParser()
    config['SETTINGS'] = {
        'key': api_key,
        'folder': folder,
        'excel_path': excel_path,
        'auto_check': str(auto_check),
        'last_line_count': str(last_count)
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)

def is_config_complete():
    cfg = load_config()
    required = ['key', 'folder', 'excel_path']
    return all(k in cfg and cfg[k] and "Nicht gewählt" not in cfg[k] for k in required)
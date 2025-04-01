import os
from dotenv import load_dotenv
from pathlib import Path


def _create_default_settings_file():    
    default_settings_lines = [
        'TG_TOKEN=put_your_telegram_token_here',
        'GEMINI_TOKEN=put_your_google_gemini_token_here',
        'AI_MODEL=gemini-2.0-flash',
        '#You need to put the name of your telegram bot for reasons with leading @',
        'BOT_USERNAME=@yourtelegrambotname',
        'DB_PATH=chatbot.db'
    ]
    
    # Add new line for every line and encode to utf-8    
    default_settings_lines = [(x+'\n').encode('utf-8') for x in default_settings_lines]

    # Create the file and write default values
    with open("settings.env", "wb") as file:
        file.writelines(default_settings_lines)        


# If there is no 'settings.env' file then create one with default values
if not Path('settings.env').is_file():
    _create_default_settings_file()
    input('''The settings file was missing. Default values loaded. 
You may need to turn off the program and change "settings.env" according to your needs.
Or press "Enter" to continue.''')


dotenv_path = Path('settings.env')
load_dotenv(dotenv_path=dotenv_path)


GEMINI_TOKEN: str = os.getenv('GEMINI_TOKEN')
TG_KEY: str = os.getenv('TG_TOKEN')
BOT_USERNAME: str = os.getenv('BOT_USERNAME')
DB_PATH: str = os.getenv('DB_PATH')
AI_MODEL: str = os.getenv('AI_MODEL')
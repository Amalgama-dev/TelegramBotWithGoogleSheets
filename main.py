from __future__ import print_function

import os.path
import pickle
import telebot
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SAMPLE_RANGE_NAME = 'Messages!A2:E250'

class GoogleSheet:
    SPREADSHEET_ID = 'Your Spreadsheet id'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def updateRangeValues(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))
    

def update_cells(username, text):
    gs = GoogleSheet()
    a_cell = None
    b_cell = None

    with open('cells.json', 'r') as f:
        d = f.read()
        d = json.loads(d)
        a_cell = d['A']
        b_cell = d['B']
    
    test_range = f'Messages!A{a_cell}:B{b_cell}'
    test_values = [
        [username, text],
    ]

    with open('cells.json', 'w') as f:
        new_d = {'A': a_cell + 1, 'B': b_cell + 1}
        f.write(json.dumps(new_d))
        
    gs.updateRangeValues(test_range, test_values)


#code for bot
bot = telebot.TeleBot('Your Telegram bot api')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '<b>Hello!</b>', parse_mode='html')

@bot.message_handler()
def get_user_text(message):
    username = message.from_user.username
    text = message.text
    update_cells(username, text)
    

bot.polling(none_stop=True)
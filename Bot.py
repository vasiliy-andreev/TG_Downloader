import telebot
import json
import requests
import torrent_parser
from telebot import types
import os
import time

token = ""
proxies=dict(http='socks5://', https='')
Database = 'DownloadsDB'
path = ''
torrents = ''
FileMessage = None
FileName = None
Users=['firstname surname',]

bot = telebot.TeleBot(token, threaded=False)
telebot.apihelper.proxy = proxies

print('Starting')
def GetDatabase(Database=Database):
    DictDB = dict()
    with open(Database,'r') as f:
        FileList = f.read()
        FileList = FileList.split(',')
        for file in FileList[0:-1]:
            DictDB[file.split(':')[0]] = int(file.split(':')[1])
        return DictDB

def WriteDatabase(FileName,chat_id,Database=Database):
    with open(Database,'a') as f:
        f.write(FileName+':'+str(chat_id)+',')
        print('{0} is added to Database'.format(FileName))

def DownloadFile(message, path=path, torrents=torrents, Database=Database,bot=bot):
    FileName = message.document.file_name
    if 'torrent' in FileName:
        path = torrents
    FullFileName = path+FileName
    FileID = message.document.file_id
    FileInfo = bot.get_file(FileID)
    FileContent = bot.download_file(FileInfo.file_path)
    with open(FullFileName,'wb') as f:
        f.write(FileContent)
        bot.send_message(message.chat.id, 'File {0} is downloaded'.format(FileName))
        print('File is downloaded')

def Choice(chat_id,FileName):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_yes = types.InlineKeyboardButton('Да',callback_data='yes')
    button_no = types.InlineKeyboardButton('Нет',callback_data='no')
    keyboard.add(button_yes,button_no)
    text = 'Файл {0} уже был загружен, всё равно сохранить?'.format(FileName)
    bot.send_message(chat_id,text=text,reply_markup=keyboard)

def CheckUser(message, Users=Users):
    UserName = message.from_user.first_name + ' ' + message.from_user.last_name
    if UserName in Users:
        print('User {0} in list'.format(UserName))
        return True
    else:
        print ('User {0} is new here'.format(UserName))
        return False

def DLNAUpdate(chat_id):
    os.system('minidlnad -R')
    time.sleep(1)
    os.system('service minidlna restart')
    time.sleep(1)
    bot.send_message(chat_id,text='DLNA has been restarted')

def getTorrents():
    host = 'http://127.0.0.1:8112/json'
    headers = {'Content-Type':'application/json'}
    dataLogin = {"method":"auth.login","params":["deluge"],"id":133}
    dataTorrents = {"method":"web.update_ui","params":[
        ["queue","name","total_wanted","state","progress","num_seeds","total_seeds","num_peers",
        "total_peers","download_payload_rate","upload_payload_rate","eta","ratio","distributed_copies",
        "is_auto_managed","time_added","tracker_host","save_path","total_done","total_uploaded",
        "max_download_speed","max_upload_speed","seeds_peers_ratio"],{}],"id":133}
    login = requests.request('POST',host,headers=headers,data=json.dumps(dataLogin))
    cookies = login.cookies
    torrents = requests.request('POST',host, headers=headers, cookies=cookies, data=json.dumps(dataTorrents))
    #a = a['result']['torrents']
    #for i in list(a.keys()): db[a[i]['name']]=a[i]['progress']
    return torrents.json()['result']['torrents']

def notLoaded(delugeInfo,chat_id):
    data = dict()
    for entry in list(delugeInfo.keys()):
        if delugeInfo[entry]['progress'] != 100:
            data[delugeInfo[entry]['name']] = round(delugeInfo[entry]['progress'],2)
    bot.send_message(chat_id,text=str(data))

print('Functions are loaded')


@bot.message_handler(content_types=['text'])
def Message(message):
    if CheckUser(message) is False:
        bot.send_message(message.chat.id, 'You are is not allowd to write me')
        return
    if message.text == 'DLNA':
        DLNAUpdate(message.chat.id)
        return
    if message.text == 'Get':
        notLoaded(getTorrents(), message.chat.id)
        return
    bot.send_message(message.chat.id, 'You said '+message.text)


@bot.message_handler(content_types=['document'])
def ReceiveFile(message,proxies=proxies):
    if CheckUser(message) is False:
        bot.send_message(message.chat.id, 'You are is not allowd to write me')
        return
    print('Document part is called')
    global FileName
    global FileMessage
    FileMessage = message
    FileName = message.document.file_name
    FileName = FileName.replace(',','_')
    print ('Filename is {0}'.format(FileName))
    if FileName not in list(GetDatabase().keys()):
        print('File is not in Database')
        DownloadFile(message)
        WriteDatabase(FileName,message.chat.id)
    else:
        print('File is already in Database')
        Choice(message.chat.id, FileName)
        @bot.callback_query_handler(func=lambda call: True)
        def getAnswer(call):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Файл {0} уже был загружен, всё равно сохранить?'.format(FileName),
                                    reply_markup=None)
            print(call.data)
            if call.data == 'yes':
                DownloadFile(message)
            if call.data == 'no':
                bot.send_message(message.chat.id, 'File {0} is not downloaded'.format(FileName))



while True:
    time.sleep(2)
    try:
        print('polling...')
        bot.infinity_polling(True)
    except:
        print('it was except')
        time.sleep(3)
        os.system('nohup python3 myBot-inf.py &')
        time.sleep(1)
        exit()

import telebot
from telebot import types
import requests
import os

token = ''
proxies=dict(http='socks5://username:password@ip:port', https='socks5://username:password@ip:port')
Database = ''
path = ''
FileMessage = None
FileName = None
Users=['Firstname Lastname',]

bot = telebot.TeleBot(token)
telebot.apihelper.proxy = proxies

print('Starting')
def GetDatabase(Database=Database):
    with open(Database,'r') as f:
        FileList = f.read()
        FileList = FileList.split(',')
        return FileList

def WriteDatabase(FileName,Database=Database):
    with open(Database,'r+') as f:
        f.write(FileName+',')
        print('{0} is added to Database'.format(FileName))

def DownloadFile(message, path=path, Database=Database,bot=bot):
    FileName = message.document.file_name
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
    button_yes = types.InlineKeyboardButton('Yes',callback_data='yes')
    button_no = types.InlineKeyboardButton('No',callback_data='no')
    keyboard.add(button_yes,button_no)
    text = 'File {0} has already been downloaded, save it anyway?'.format(FileName)
    bot.send_message(chat_id,text=text,reply_markup=keyboard)

def CheckUser(message, Users=Users):
    UserName = message.from_user.first_name + ' ' + message.from_user.last_name
    if UserName in Users:
        print('User {0} in list'.format(UserName))
        return True
    else:
        print ('User {0} is new here'.format(UserName))
        return False

print('Functions are loaded')


@bot.message_handler(content_types=['text'])
def Message(message):
    if CheckUser(message) is False:
        bot.send_message(message.chat.id, 'You are is not allowd to write me')
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
    if FileName not in GetDatabase():
        print('File is not in Database')
        DownloadFile(message)
        WriteDatabase(FileName)
    else:
        print('File is already in Database')
        Choice(message.chat.id, FileName)
        @bot.callback_query_handler(func=lambda call: True)
        def getAnswer(call):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='File {0} has already been downloaded, save it anyway?'.format(FileName),
                                    reply_markup=None)
            print(call.data)
            if call.data == 'yes':
                DownloadFile(message)
            if call.data == 'no':
                bot.send_message(message.chat.id, 'File {0} is not downloaded'.format(FileName))


        



bot.polling(none_stop=True)

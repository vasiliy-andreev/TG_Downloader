import requests
import json
import telebot
import time

ChatID = []
token = ""
proxies=dict(http='')
bot = telebot.TeleBot(token, threaded=False)
telebot.apihelper.proxy = proxies

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
    return torrents.json()['result']['torrents']

def notLoaded(delugeInfo):
    data = dict()
    for entry in list(delugeInfo.keys()):
        if delugeInfo[entry]['progress'] != 100:
            data[delugeInfo[entry]['name']] = round(delugeInfo[entry]['progress'],2)
    return data

oldQueue = notLoaded(getTorrents())
#print('mark 0, oldQueue is', oldQueue)
while True:
    time.sleep(6)
    queue = notLoaded(getTorrents())
    #print('mark 05, queue is ',queue)
    if len(oldQueue) == 0 and len(queue) != 0:
        oldQueue = queue.copy()
        #print ('mark 1, oldQueue is ', oldQueue)
    done = set(list(oldQueue.keys())) - set(list(queue.keys()))
    #print('mark 2, done is', done)
    if len(done) != 0:
        for entry in list(done):
            #print('mark 3, entry is', entry)
            try:
                bot = telebot.TeleBot(token, threaded=False)
                telebot.apihelper.proxy = proxies
                for Chat in ChatID:
                    bot.send_message(Chat, 'Completed:    {0}'.format(str(entry)))
            except:
                time.sleep(2)
                for Chat in ChatID:
                    bot.send_message(Chat, 'Completed:    {0}'.format(str(entry)))
        done = set()
        #print ('mark 4, done is',done)
        oldQueue = queue.copy()
        #print ('mark 5, oldQueue is ',oldQueue)




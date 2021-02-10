import pyppeteer
import asyncio
import random
import queue
import json
import string
from time import sleep
from datetime import datetime
from npyscreen import wrapper_basic
from threading import Thread,Event
from interface import Form

names = ['bot']
count = 6
temp = open('words.txt','r')
words = temp.read().split('\n')
temp.close()

def flip_coin():
    if random.randint(0,2) == 0:
        return True
    else:
        return False

def randomString(stringLength):
	lettersAndDigits = string.ascii_letters + string.digits
	return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

class bot:
    def __init__(self,queue,name='',url='https://skribbl.io/'):
        self.since_last_msg_time = datetime.now()
        self.url = url
        self.name = name
        self.words = []
        self.queue = queue
        self.valid_bots = []
        self.player_count = 0
        self.player_list = []
        self.flags = [
        '--no-sandbox',
        '--mute-audio',
        '--disable-blink-features',
        '--disable-setuid-sandbox',
        '--disable-infobars',
        '--window-position=0,0',
        '--ignore-certifcate-errors',
        '--ignore-certifcate-errors-spki-list',
        '--deterministic-fetch',
        "--proxy-server='direct://'",
        '--proxy-bypass-list=*']

    async def start(self):
        self.browser = await pyppeteer.launcher.launch({'args': self.flags,'ignoreHTTPSErrors' : True, 'headless' : True,'handleSIGINT':False,'handleSIGTERM':False,'handleSIGHUP':False})
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(60000)
        self.queue.put('START')

    async def join(self):
        #self.name = randomString(10)
        self.name = random.choice(names)
        await self.page.goto(self.url)
        await self.page.evaluate(f'() => document.getElementById("inputName").value = "{self.name}"')
        randomize = await self.page.waitFor('//*[@id="buttonAvatarCustomizerRandomize"]')
        join_button = await self.page.waitFor('//*[@id="formLogin"]/button[1]')
        await randomize.click()
        await join_button.click()

    async def send_chat(self,message):
        chat_input = await self.page.waitFor('//*[@id="inputChat"]')
        await self.page.evaluate(f'() => document.getElementById("inputChat").value = "{message}"')
        await chat_input.press('Enter')

    async def get_player_count(self):
        element = await self.page.waitFor('//*[@id="containerGamePlayers"]')
        player_box = await element.boxModel()
        if self.player_count != int(player_box['height'] / 48):
            self.player_count = int(player_box['height'] / 48)
            self.queue.put(f'[{self.player_count} PLAYERS_COUNT]')

    async def drawing_check(self):
        text = await self.page.evaluate('() => document.getElementById("currentWord").innerText')
        if (not text) or ('_' in text):
            return False
        else:
            return True

    async def antibot(self):
        chat = await self.page.evaluate('() => document.getElementById("boxMessages").innerText')
        chat = chat.split('\n')[-20:]
        self.valid_bots = []
        for bot in self.player_list:
            lines = [string for string in chat if bot+':' in string]
            autoguess = [line for line in lines if any(word in line for word in words)]
            mentions = [line for line in lines if self.name in line]
            if (mentions != []) or (len(autoguess) > 3):
                self.valid_bots.append(bot)
            else:
                continue
    async def get_player_list(self):
        names = []
        try: #If this function gets run when a player leaves, it will return an exception.
            for i in range(self.player_count):
                name = await self.page.evaluate(f'() => document.getElementsByClassName("info")[{i+1}].innerText')
                if self.name in name:
                    continue
                name = name.replace('\n','')
                x = name.find('Points')
                name = str(name[:x])
                names.append(name)
            if names != self.player_list:
                self.player_list = names
        except:
            pass

    async def check_spam(self):
        try:
            chat = await self.page.evaluate('() => document.getElementById("boxMessages").innerText')
            text = chat.split('\n')
            text = str(text[-3:])
        except:
            text = ''
        if "Spam detected!" in text:
            return True
        else:
            return False
    async def chat_spam(self):
        temp = open('messages/normal.txt','r')
        self.normal_messages = temp.read().split('\n')
        temp.close()
        temp = open('messages/targetted.txt','r')
        self.targetted_messages = temp.read().split('\n')
        temp.close()
        temp = open('messages/antibot.txt','r')
        self.antibot_messages = temp.read().split('\n')
        temp.close()
        while int(str(datetime.now() - self.since_last_msg_time)[2:4]) < 1:
            try:
                random.shuffle(self.normal_messages)
                for message in self.normal_messages:
                    await asyncio.gather(self.get_player_count(),self.get_player_list(),self.votekick(),self.antibot())
                    if self.valid_bots == []:
                        if (flip_coin() == True) and (self.player_list != []):
                            player = str(random.choice(self.player_list))
                            await self.send_chat(random.choice(self.targetted_messages).replace('placeholder',player))
                            await asyncio.sleep(0.8)
                        await self.send_chat(message)
                        await asyncio.sleep(0.8)
                    else:
                        try:
                            await self.send_chat(random.choice(self.antibot_messages).replace('placeholder',random.choice(self.valid_bots)))
                            await asyncio.sleep(0.7)
                        except:
                            pass
                    if await self.check_spam():
                        await asyncio.sleep(5)
                    if self.player_count < 2:
                        raise Exception('not enough players')
                        break
                    if await self.drawing_check():
                        raise Exception('chosen to draw')
                        break
            except Exception as e:
                if ('NoneType' in str(e)) or ('Node' in str(e)):
                    self.queue.put("EXCEPTION: force disconnect due to kick")
                    self.player_count = 1
                else:
                    self.queue.put("EXCEPTION: "+str(e))
                break

    async def chat_updates(self):
        chat_history = ''
        while int(str(datetime.now() - self.since_last_msg_time)[2:4]) < 1:
            try:
                if self.player_count < 2:
                    break
                if await self.drawing_check():
                    break
                chat = await self.page.evaluate('() => document.getElementById("boxMessages").innerText')
                chat = chat.split('\n')
                # chat = [sub.replace(self.name,'YOU') for sub in chat]
                if chat != chat_history:
                    data = chat[len(chat_history):]
                    self.queue.put(data)
                    self.since_last_msg_time = datetime.now()
                    chat_history = chat
            except Exception as e:
                break

    async def votekick(self):
        element = await self.page.waitFor('//*[@id="containerPlayerlist"]/div[2]')
        await element.click()

    async def run(self):
        while True:
            try:
                await self.start()
                while True:
                    while True:
                        await self.join()
                        await asyncio.sleep(10)
                        try:
                            await self.get_player_count()
                        except Exception as e:
                            self.player_count = 1
                            continue
                        if self.player_count > 1:
                            self.queue.put('JOINED GAME')
                            self.since_last_msg_time = datetime.now()
                            break
                    await asyncio.gather(self.chat_spam(),self.chat_updates())
                    self.queue.put('LEFT GAME')
                    self.player_count = 0
                    self.player_list = []
                    self.valid_bots = []
            except Exception as e:
                self.queue.put("EXCEPTION: "+str(e))
            await self.browser.close()
            continue

def interface(*args):
	f = Form()
	f.create()
	while True:
		f.update_values(queues)

def wrapper(queues,count):
    wrapper_basic(interface)

def loop_thread_run(bot):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bot.run())

queues = []
threads = []
for i in range(count):
    q = queue.Queue()
    queues.append(q)
    b = bot(queue=q,name=random.choice(names))
    thread = Thread(target=loop_thread_run,args=(b,))
    threads.append(thread)
    thread.start()

thread = Thread(target=wrapper,args=(queues,count,))
thread.setDaemon(True)
thread.start()

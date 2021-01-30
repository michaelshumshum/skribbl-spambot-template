import pyppeteer
import asyncio
import random
import queue
import json
from time import sleep
from npyscreen import wrapper_basic
from threading import Thread,Event
from interface import Form

name = ''
count = 6
messages = ['']

class bot:
    def __init__(self,queue,name='',url='https://skribbl.io/'):
        self.url = url
        self.name = name
        self.queue = queue
        self.player_count = 0
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
        return int(player_box['height'] / 48)

    async def check_spam(self):
        try:
            chat = await self.page.evaluate('() => document.getElementById("boxMessages").innerText')
            text = chat.split('\n')
            text = str(text[-2:])
        except:
            text = ''
        if "Spam detected!" in text:
            return True
        else:
            return False

    async def chat_spam(self):
        while True:
            try:
                random.shuffle(messages)
                for message in messages:
                    await self.votekick()
                    await self.send_chat(message)
                    await asyncio.sleep(0.4)
                    player_count = await self.get_player_count()
                    if await self.check_spam():
                        await asyncio.sleep(5)
                    if player_count < 2:
                        raise Exception('disconnected')
                        break
            except Exception as e:
                break

    async def chat_updates(self):
        chat_history = ''
        while True:
            try:
                player_count = await self.get_player_count()
                if player_count < 2:
                    break
                if self.player_count != player_count:
                    self.player_count = player_count
                    self.queue.put(f'[{self.player_count} PLAYERS_COUNT]')
                chat = await self.page.evaluate('() => document.getElementById("boxMessages").innerText')
                chat = chat.split('\n')
                chat = [sub.replace(self.name,'YOU') for sub in chat]
                if chat != chat_history:
                    data = chat[len(chat_history):]
                    self.queue.put(data)
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
                            player_count = await self.get_player_count()
                        except Exception as e:
                            player_count = 1
                            continue
                        if player_count > 1:
                            self.queue.put('JOINED GAME')
                            break
                    await asyncio.gather(self.chat_spam(),self.chat_updates())
                    self.queue.put('LEFT GAME')
                    self.player_count = 0
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
    b = bot(queue=q,name=name)
    thread = Thread(target=loop_thread_run,args=(b,))
    threads.append(thread)
    thread.start()

thread = Thread(target=wrapper,args=(queues,count,))
thread.setDaemon(True)
thread.start()

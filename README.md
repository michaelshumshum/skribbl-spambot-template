# skribbl-spambot-template
torment children...for fun!
## about
use this if you are, like me for some reason, looking to create spam bots for skribblio. i have made a few in the past using selenium, but i decided to switch to pyppeteer, which is, my experience, more efficient at this task. you can do whatever you want with this template and use it however you like. if you merely want to make a quick bot with no additinal features, you can change the name of the bots, the messages the bots send, and the number of bots. though, there is still quite a little bit of potential with this, for example draw bots and autoguessers, but i haven't had the intention of doing that, so feel free to do that yourself.

it is uncertain how long the bots can run. i have run them overnight multiple times and it ranges from a couple hours to pretty much infinitely. 

## prerequisites
install the npyscreen and pyppeteer modules. you can also just run `pip3 install -r requirements.txt` on the provided file. after that, make sure to run `pyppeteer-install` to install the required chromium version for pyppeteer. 

## usage
in the code, indicate the name and messages for the bot. if the name is left blank, skribbl will generate a random name. the default number of bots is 6, but you can change this. though, when changing this, you have to change the `count` variable in both `bot.py` and the `self.count` variable in `Form` class within `interface.py`. as of now, the interface only supports 4+ bots as i haven't implemented single row layouts, which is something i plan to do in the next few days. there is potentially limit on the number of bots, it's only limited by the power of your computer. 

in the 'messages' folder, there are three text files where the respective messages are stored. separate the messages by line breaks. for the targetted and antibot messages, use `placeholder` as the literal placeholder for the target. the bots will automatically replace those `placeholder` with the name of the target. 
#### how the bots decide what messages to send
one 'cycle' can be considered to be all the normal messages. for every message that is sent, there is a 1/3 chance that the bot will also send a targetted message. this can be easily changed by changing the values in the `flip_coin` function. if there is another bot present in the game, the bot will send an antibot message no matter what. 

all other changes to the code will not guarantee it to work, so anything you do with it outside of those few variables is for you to figure out. though, i am happy to get suggestions and some ideas on what to add/change to the template.

## some questions you may have:
#### why did i do this?
i like making bots. it's fun.
#### what's better about this than other bots?
nothing really.  but i do believe most bots do not have player count detection, which i think is quite nifty. it also comes with a simple 'interface' that gets you some information of the games the bots are in and hihglights them.
#### why does it use pyppeteer?
in the past, i used selenium for the bots because i had not known about pyppeteer, a puppeteer port to python. selenium is completely capable of making these bots, but after using pyppeteer, it was apparent how much more efficient pyppeteer was, especially dealing with so many instances of it. some benefits i found were:
- fewer crashes and exceptions
- faster execution in general
- better headless mode
- supports and requires asyncio, which is a lot more reliable in my opinion
- allows javascript evaluation, which is exponentially useful for typing in text and getting text

by far, pyppeteer is a lot quicker and consistent. you can compare it to my older bots and see how often those bots crash and how slow they were. if you plan to do any sort of web scraping or crawling, i would highly recommend using pyppeteer due to its versatility and benefits overall.
#### what else can this bot do?
not much. it doesn't have any "hack" features and just meant to be annoying. though, since it uses pyppeteer, which has mousemovement support, a drawbot is possible. a guessing bot is would be pretty easy as it just uses the chat.
#### why not use requests and sockets?
the devs implemented recaptcha v2 to the game, meaning only connections from real devices that can send recaptcha cookies can connect. luckily, it recaptcha v2, which doesn't have the image selection bs, so using automated web-browsers is possible, which is what we are doing. we only need to tweak some of the chromium settings so that recaptcha can't detec we are using automation. unless somebody manages to find a method to generate recaptcha cookies reliably, which i extremeley doubt, and have it be unknown to google, we are stuck with using web browsers for bots and are limited to the number of bots we can run.

## disclaimer
the entire concept of this is for malicious activity, meant to direcly annoy or even offend people. however you, the user, implement it is all your responsibility. any reprecussions such as but no limited IP blacklisting, hatespeech, or even legal action, is not liable on me. 

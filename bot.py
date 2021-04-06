# bot.py
import os

import discord
from dotenv import load_dotenv
import re
import random

load_dotenv(dotenv_path=".envvars")
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

inc_form_mess = 'Input is in incorrect format, somewhere near "'

listen_val = "!r "
explode_val = "!rd "

def getRealName(event):
    try:
        if event.author.nick != None:
            return event.author.nick
        else:
            return event.author.name
    except:
        return event.author.name

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    if (message.content.startswith("!rhelp")):
        await message.author.create_dm()
        await message.author.dm_channel.send("To roll dice, type something like `!r 2d10+2`")
        await message.author.dm_channel.send("Use `+`, `-`, `adv`, `dis`, `advantage`, or `disadvantage` to add advantage or disadvantage, as in `!r + d20 + 2`")
        await message.author.dm_channel.send("Use `!rd` instead or `!r` for damage rolls, which allows for explosions")
    
    if (message.content.startswith(listen_val) or (message.content.startswith(explode_val))):
        rest = ""
        toBreak = False
        if message.content.startswith(listen_val) and (len(message.content) <= len(listen_val)):
            toBreak = True
        if message.content.startswith(explode_val) and (len(message.content) <= len(explode_val)):
            toBreak = True
        if (not toBreak):
            isGoodToCalc = True
            explodes = False
            if message.content.startswith(listen_val):
                rest = message.content[len(listen_val):]
            if message.content.startswith(explode_val):
                rest = message.content[len(explode_val):]
                explodes = True
            rest = re.sub(' +', ' ', rest)
            splits = rest.split(" ",1)
            allRest = ""
            adv = False
            dis = False
            #print(splits)
            if (splits[0].strip() == "adv" or splits[0].strip() == "+" or splits[0].strip() == "advantage"):
                adv = True
                allRest = splits[1].strip()
            elif(splits[0].strip() == "dis" or splits[0].strip() == "-" or splits[0].strip() == "disadvantage"):
                dis = True
                allRest = splits[1].strip()
            else:
                allRest = rest
            
            allRest = re.sub(' +', ' ', allRest)
            
            print(allRest)
            print(rest)
            
            if (len(allRest) > 0):
                strParts = []
                currentString = ""
                for i in allRest:
                    if (i=="+"):
                        strParts.append(currentString)
                        currentString = ""
                    elif (i==" "):
                        if (currentString != ""):
                            strParts.append(currentString)
                        currentString = ""
                    elif (i=="-"):
                        strParts.append(currentString)
                        currentString = "-"
                    else:
                        currentString += i
                strParts.append(currentString)
                #print(strParts)
                
                tVal = 0
                rolls = []
                isInText = True
                text = ""
                isCrit = []
                isCritFail = []
                for p in strParts:
                    val = 0
                    if (not bool(re.match("([0-9]*d[0-9]+)|((\\+)*[0-9]+)|((\\-)*[0-9]+)",p)) and isInText):
                        text += p + " "
                    else:
                        isInText = False
                        text=text.strip()
                        try:
                            val = int(p)
                        except:
                            val = 0
                            if bool(re.match("([0-9])*d([0-9])+",p)):
                                ps = p.split("d")
                                n = 1
                                if (ps[0]==""):
                                    n = 1
                                else:
                                    n = int(ps[0])
                                s = int(ps[1])
                                if (n>0 and s>0):
                                    t = 0
                                    for i in range(n):
                                        thisroll = random.randint(1,s)
                                        if adv:
                                            roll2 = random.randint(1,s)
                                            if (roll2 > thisroll):
                                                thisroll = roll2
                                        if dis:
                                            roll2 = random.randint(1,s)
                                            if (roll2 < thisroll):
                                                thisroll = roll2
                                        if (explodes and (thisroll == s)):
                                            keepGoing = True
                                            while keepGoing:
                                                roll2 = random.randint(1,s)
                                                thisroll += roll2
                                                if (roll2 != s):
                                                    keepGoing = False
                                        t += thisroll
                                        rolls.append(thisroll)
                                        if (s == 20 and thisroll == 20):
                                            isCrit.append(True)
                                            isCritFail.append(False)
                                        elif (s == 20 and thisroll == 1):
                                            isCritFail.append(True)
                                            isCrit.append(False)
                                        else:
                                            isCritFail.append(False)
                                            isCrit.append(False)
                                    val += t
                                
                                else:
                                    isGoodToCalc = False
                                    await message.channel.send("Cannot roll dice containing 0s")
                            else:
                                isGoodToCalc = False
                                await message.channel.send(inc_form_mess+p+'"')
                        tVal += val
                if (isGoodToCalc):
                    #print(isCrit)
                    #print(isCritFail)
                    uName = getRealName(message)
                    tTotal = "*"+uName+" roll"
                    if text != "":
                        tTotal += " for " + text
                    if adv:
                        tTotal+=" (with adv)"
                    elif dis:
                        tTotal+=" (with dis)"
                    tTotal += ":* "+str(tVal)
                    rollT = "*["
                    for i in range(len(rolls)):
                        if isCrit[i] or isCritFail[i]:
                            rollT += "__**"
                        rollT += (str(rolls[i]))
                        if isCrit[i] or isCritFail[i]:
                            rollT += "**__"
                        rollT += ", "
                    tTotal += " " + rollT[:-2] + "]*"
                    await message.channel.send(tTotal)
            else:
                isGoodToCalc = False
                await message.channel.send(inc_form_mess+message.content+'"')


client.run(TOKEN)
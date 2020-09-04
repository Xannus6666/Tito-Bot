import discord
from discord.ext import commands, tasks
import random
from discord.utils import get
import os
from pyperclip import copy
import pymongo
from pymongo import MongoClient
import youtube_dl
import datetime
import shutil
import time
import aiohttp


# Tito Bot, a bot with db functionalities, levelling system, economy system, voice commands, mod commands.
# Developed by tamrol077.
# To host it, follow the steps in the readme.


connection_string = str(open("connection_string.txt", "r").readline())


cluster = MongoClient(connection_string.strip())
db = cluster["TitoBot"]
collection = db["prefixes"]
levelcollection = db["levels"]
moneycollection = db["money"]
statuscollection = db["userstatus"]


def get_prefix(client, message):
    results = collection.find({"_id": str(message.guild.id)})
    for result in results:
        return result["prefix"]


print(discord.__version__)


token = str(open("token.txt", "r").readline())


TOKEN = token.strip()
PREFIX = get_prefix


players = {}
queues = {}


client = commands.Bot(command_prefix=PREFIX)
client.remove_command('help')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('.help'))
    print("Tito-Bot is active.")
    client.reaction_roles = []


@client.event
async def on_message(message):
    results = levelcollection.find({"_id": str(message.author.id)})
    xpneeded = 1000
    salveciao = 1000 + 60
    for result in results:
        xpnumber = result["xp"]
        userlevel = result["level"]
    userid = message.author.id
    if message.author == client.user:
        return
    if client.user.mention in message.content.split():
        await message.channel.send("u mentioned")
    else:

        levelcollection.update_one({"_id": str(userid)}, {"$inc": {"xp": 40}})
    if userlevel == 1:
        if xpnumber >= salveciao:
            levelcollection.update_one({"_id": str(userid)}, {"$set": {"xp": 0}})
            levelcollection.update_one({"_id": str(userid)}, {"$inc": {"level": 1}})
            await message.channel.send(f"{message.author} just levelled to level 2!")
    elif userlevel > 1:
        salve = 60 * userlevel
        newxp = xpneeded + salve
        if xpnumber >= newxp:
            levelcollection.update_one({"_id": str(userid)}, {"$set": {"xp": 0}})
            ciao = userlevel + 1
            levelcollection.update_one({"_id": str(userid)}, {"$inc": {"level": 1}})
            if message.guild.id == 264445053596991498:
                print("CHina")
            else:
                await message.channel.send(f"{message.author} just levelled to level {ciao}")

    await client.process_commands(message)


@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 739496644319379496:
        print(payload.emoji.name)
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)
        if payload.emoji.name == "cpp":
            role = discord.utils.get(guild.roles, name="C++")
        if payload.emoji.name == "C_":
            role = discord.utils.get(guild.roles, name="C")
        if payload.emoji.name == "csharp":
            role = discord.utils.get(guild.roles, name="C#")

        if role is not None:
            print(f"{role.name} was found")
            print(role.id)
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            await member.add_roles(role)
            print("done")


@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == 'id':
        print(payload.emoji.name)

        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)

        if role is not None:
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            await member.remove_roles(role)
            print("done")


@client.event
async def on_member_join(member):
    try:
        post_level = {"_id": str(member.id), "xp": 0, "level": 1}
        levelcollection.insert_one(post_level)
        post_money = {"_id": str(member.id), "money": 0}
        moneycollection.insert_one(post_money)
        post_status = {"_id": str(member.id), "status": "standard"}
        statuscollection.insert_one(post_status)
    except pymongo.errors.DuplicateKeyError:
        print("Already in the db.")


@client.command(aliases=["chnick", "changenick"])
async def changenickname(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed to {nick} for {member.mention} ')


m = {}


@client.event
async def on_guild_join(guild):
    post_guild = {"_id": str(guild.id), "prefix": "."}
    collection.insert_one(post_guild)
    global m
    if len(m) == 0:
        m = {}
        for member in client.get_guild(guild.id).members:
            try:
                post_status = {"_id": str(member.id), "status": "standard"}
                statuscollection.insert_one(post_status)
                post_level = {"_id": str(member.id), "xp": 0, "level": 1}
                levelcollection.insert_one(post_level)
                post_money = {"_id": str(member.id), "money": 0}
                moneycollection.insert_one(post_money)
            except pymongo.errors.DuplicateKeyError:
                print("Member already registered in the MongoDB database.")


@client.event
async def on_guild_remove(guild):
    collection.delete_one({"_id": str(guild.id)})


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        commandnotfoundembed = discord.Embed(title='**Command not Found!**',
                                             description=f'{ctx.author} try looking at the help command for the list of all commands!',
                                             color=0x000000)
        await ctx.send(embed=commandnotfoundembed)


# Level Commands:


@client.command(aliases=["userlevel","lvl"])
async def level(ctx, member:discord.Member):
    results = levelcollection.find({"_id": str(member.id)})
    xpneeded = 1000
    for result in results:
        xpnumber = result["xp"]
        userlevel = result["level"]
    salve = 60 * userlevel
    xpthatuneed = xpneeded + salve
    results = statuscollection.find({"_id": str(member.id)})
    for result in results:
        status = result["status"]
    if status == "standard":
        levelEmbed = discord.Embed(title=f"{member} level in Tito-Bot",description="Levelling system of Tito-Bot, made by tamrol073#6998(tamrol077 on github)",color=0xBEBEBE)
        levelEmbed.add_field(name=f"**Level: {userlevel}**", value=f"{xpnumber} XP / {xpthatuneed} XP ")
        levelEmbed.set_footer(text="Bot created by tamrol073#6998")
        levelEmbed.set_thumbnail(url=member.avatar_url)
    if status == "premium":
        levelEmbed = discord.Embed(title=f"{member} (Premium tier of Tito Bot) level in Tito-Bot",description="Levelling system of Tito-Bot, made by tamrol073#6998(tamrol077 on github)",color=0xFFD700)
        levelEmbed.add_field(name=f"**Level: {userlevel}**", value=f"{xpnumber} XP / {xpthatuneed} XP ")
        levelEmbed.set_footer(text="Bot created by tamrol073#6998")
        levelEmbed.set_thumbnail(url=member.avatar_url)


    await ctx.send(embed=levelEmbed)


@level.error
async def levelError(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        member = ctx.author
        results = levelcollection.find({"_id": str(member.id)})
        xpneeded = 1000
        for result in results:
            xpnumber = result["xp"]
            userlevel = result["level"]
        salve = 60 * userlevel
        xpthatuneed = xpneeded + salve
        results = statuscollection.find({"_id": str(member.id)})
        for result in results:
            status = result["status"]
        if status == "standard":
            levelEmbed = discord.Embed(title=f"{member} (Premium tier of tito bot) level in Tito-Bot",description="Levelling system of Tito-Bot, made by tamrol073#6998(tamrol077 on github)",color=0xBEBEBE)
            levelEmbed.add_field(name=f"**Level: {userlevel}**", value=f"{xpnumber} XP / {xpthatuneed} XP ")
            levelEmbed.set_footer(text="Bot created by tamrol073#6998")
            levelEmbed.set_thumbnail(url=member.avatar_url)
        if status == "premium":
            levelEmbed = discord.Embed(title=f"{member} (Premium member of tito bot) level in Tito-Bot",description="Levelling system of Tito-Bot, made by tamrol073#6998(tamrol077 on github)",color=0xFFD700)
            levelEmbed.add_field(name=f"**Level: {userlevel}**", value=f"{xpnumber} XP / {xpthatuneed} XP ")
            levelEmbed.set_footer(text="Bot created by tamrol073#6998")
            levelEmbed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=levelEmbed)


# Money Commands:


@client.command(aliases=["bal", "balanc"])
async def balance(ctx, member:discord.Member):
    results = moneycollection.find({"_id":str(member.id)})
    for result in results:
        money = result["money"]
    results = statuscollection.find({"_id": str(member.id)})
    for result in results:
        status = result["status"]
    if status == "standard":
        MoneyEmbed = discord.Embed(title=f"Balance of {member}", description=f"Money that {member} has. ", color=0xBEBEBE)
        MoneyEmbed.set_thumbnail(url=member.avatar_url)
        MoneyEmbed.add_field(name="**Yugoslav Dinars:**", value=f"{money}", inline=False)
        MoneyEmbed.set_footer(text="Bot made by tamrol073#6998")
        await ctx.send(embed=MoneyEmbed)
    if status == "premium":
        MoneyEmbed = discord.Embed(title=f"Balance of {member} (Premium tier of tito bot)", description=f"Money that {member} has. ", color=0xFFD700)
        MoneyEmbed.set_thumbnail(url=member.avatar_url)
        MoneyEmbed.add_field(name="**Yugoslav Dinars:**", value=f"{money}", inline=False)
        MoneyEmbed.set_footer(text="Bot made by tamrol073#6998")
        await ctx.send(embed=MoneyEmbed)


@balance.error
async def balance_error(ctx, error):
    member = ctx.author
    results = moneycollection.find({"_id": str(member.id)})
    for result in results:
        money = result["money"]
    results = statuscollection.find({"_id": str(member.id)})
    for result in results:
        status = result["status"]
    if status == "standard":
        MoneyEmbed = discord.Embed(title=f"Balance of {member}", description=f"Money that {member} has. ", color=0xBEBEBE)
        MoneyEmbed.set_thumbnail(url=member.avatar_url)
        MoneyEmbed.add_field(name="**Yugoslav Dinars:**", value=f"{money}", inline=False)
        MoneyEmbed.set_footer(text="Bot made by tamrol073#6998")
        await ctx.send(embed=MoneyEmbed)
    if status == "premium":
        MoneyEmbed = discord.Embed(title=f"Balance of {member} (Premium tier of tito bot)",description=f"Money that {member} has. ", color=0xFFD700)
        MoneyEmbed.set_thumbnail(url=member.avatar_url)
        MoneyEmbed.add_field(name="**Yugoslav Dinars:**", value=f"{money}", inline=False)
        MoneyEmbed.set_footer(text="Bot made by tamrol073#6998")
        await ctx.send(embed=MoneyEmbed)


@client.command()
async def give(ctx,member:discord.Member,amount):
    amount = int(amount)
    results = moneycollection.find({"_id": str(ctx.author.id)})
    for result in results:
        money = result["money"]
    nuovimoney = money - amount
    if nuovimoney > 0:
        moneycollection.update_one({"_id": str(ctx.author.id)}, {"$set": {"money": nuovimoney}})
        moneycollection.update_one({"_id": str(member.id)}, {"$inc": {"money": amount}})
        await ctx.send(f"{ctx.author.mention} gave {amount} money to {member.mention}")
    else:
        await ctx.send(f"{ctx.author.mention}, you dont have enough money")


@give.error
async def give_error(ctx,error):
    giveErrorEmbed = discord.Embed(title=f"{ctx.author}, you need to specify the amount of money and/or the user that you want to give the money to.",description="Check the syntax of the command in the help command.",color=0x000000)
    await ctx.send(embed=giveErrorEmbed)


@client.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def work(ctx):
    salve = random.randint(50, 100)
    moneycollection.update_one({"_id": str(ctx.author.id)}, {"$inc": {"money": salve}})
    await ctx.send(f"{ctx.author.mention} worked and gained {salve} money")


@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You need to wait {int(round(error.retry_after)):,.2f} seconds to work again. ")


@client.command()
@commands.cooldown(1, 8, commands.BucketType.user)
async def beg(ctx):
    salve = random.randint(20, 80)
    probability = random.randint(0, 10)
    if probability > 5:
        moneycollection.update_one({"_id": str(ctx.author.id)}, {"$inc": {"money": salve}})
        await ctx.send(f"{ctx.author.mention} begged for money and received {salve} money")
    else:
        await ctx.send("Nobody gave u money, because youre a deserterska, bige sad.")


@beg.error
async def beg_error(ctx,error):
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send(f"You need to wait {int(round(error.retry_after)):,.2f} seconds to beg again. ")


@client.command()
@commands.cooldown(1, 50, commands.BucketType.user)
async def crime(ctx):
    results = moneycollection.find({"_id": str(ctx.author.id)})
    for result in results:
        money = result["money"]
    salve = random.randint(40, 80)
    probability = random.randint(0, 10)
    if probability > 8:
        moneycollection.update_one({"_id": str(ctx.author.id)}, {"$inc": {"money": salve}})
        await ctx.send(f"{ctx.author.mention} committed a crime and earned {salve} money")
    else:
        amount = money - salve
        await ctx.send(f"U committed a crime and yugoslav police subtracted you {salve} money.")
        moneycollection.update_one({"_id": str(ctx.author.id)}, {"$set": {"money": amount}})


@client.command(aliases=["steal"])
@commands.cooldown(1, 60, commands.BucketType.user)
async def rob(ctx, member:discord.Member):
    probability = random.randint(0, 10)
    amount = random.randint(0, 100)
    results = moneycollection.find({"_id": str(ctx.author.id)})
    for result in results:
        author_money = result["money"]
    results = moneycollection.find({"_id": str(member.id)})
    for result in results:
        member_money = result["money"]
    nuovimoney = member_money - amount
    if probability > 6:
        moneycollection.update_one({"_id": str(member.id)}, {"$set": {"money": nuovimoney}})
        moneycollection.update_one({"_id": str(ctx.author.id)}, {"$inc": {"money": amount}})
        await ctx.send(f"{ctx.author.mention} stole {amount} money from {member.mention}")
    else:
        await ctx.send(f"{ctx.author.mention}, police stole you {amount} money for trying to rob {member}")


@rob.error
async def rob_error(ctx,error):
    if isinstance(error,commands.CommandOnCooldown):
        await ctx.send(f"You need to wait {int(round(error.retry_after)):,.2f} seconds to rob again. ")
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author}, make sure to ping someone.")


@crime.error
async def crime_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You need to wait {int(round(error.retry_after)):,.2f} seconds to commit a crime again. ")


@client.command()
async def shop(ctx):
    shopEmbed = discord.Embed(title="Tito Bot shop:", description="Object shop of tito bot.", color=0x000000)
    shopEmbed.add_field(name="Tito-Bot Premium status",
                        value="100000 yugoslav dinars. Buy the premium status to have gold appearance and perks.",
                        inline=False)
    shopEmbed.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    await ctx.send(embed=shopEmbed)


@client.command()
async def buy(ctx,object):
    results = moneycollection.find({"_id": str(ctx.author.id)})
    for result in results:
        money = result["money"]
    if str(object).lower() == "premiumstatus" or str(object).lower() == "premium status":
        amount = 100000
        nuovoamount = int(money) - amount
        if int(money) < amount:
            await ctx.send("You dont have enough money to buy that item")
        if int(money) >= amount:
            results = statuscollection.find({"_id": str(ctx.author.id)})
            for result in results:
                status = result["status"]
            if status == "premium":
                await ctx.send("Youre already a tito bot premium member.")
            else:
                moneycollection.update_one({"_id": str(ctx.author.id)}, {"$set": {"money": nuovoamount}})
                statuscollection.update_one({"_id": str(ctx.author.id)}, {"$set": {"status": "premium"}})
                await ctx.send(f"You have now tito bot premium status,{ctx.author.mention}, congratulations! In commands that display your profile (like balance or level) you will now have gold appearance and they will say that youre a tito bot premium member. You can also check if youre a premium member of tito bot with the command status.")
    else:
        await ctx.send("Make sure you spelled the object right.")


@buy.error
async def buy_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Make sure that you specify an item to buy in order to use the command.")


@client.command(aliases=["userstatus","amIpremium"])
async def status(ctx, member : discord.Member):
    results = statuscollection.find({"_id": str(member.id)})
    for result in results:
        status = result["status"]
    if status.lower() == "premium":
        premiumEmbed = discord.Embed(title=f"is {member} premium?", description=f"{member} status: Premium", color=0xFFD700)
        await ctx.send(embed=premiumEmbed)
    else:
        standardEmbed = discord.Embed(title=f"is {member} premium?", description=f"{member} status: Standard", color=0xBEBEBE)
        await ctx.send(embed=standardEmbed)


@status.error
async def status_error(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        member = ctx.author
        results = statuscollection.find({"_id": str(member.id)})
        for result in results:
            status = result["status"]
        if status.lower() == "premium":
            premiumEmbed = discord.Embed(title=f"is {member} premium?", description=f"{member} status: Premium",color=0xFFD700)
            await ctx.send(embed=premiumEmbed)
        else:
            standardEmbed = discord.Embed(title=f"is {member} premium?", description=f"{member} status: Standard",color=0xBEBEBE)
            await ctx.send(embed=standardEmbed)


# Fun Commands:


@client.command()
async def kill(ctx, member : discord.Member, *,reason="we dont know"):
    killembed1 = discord.Embed(title=f'{ctx.author} kills {member}',
                               description=f'{ctx.author} kills {member.mention} because {reason}',
                               color=0x000000)
    killembed1.set_image(url='https://i.makeagif.com/media/1-01-2016/wXy365.gif')
    killembed1.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    killembed2 = discord.Embed(title=f'{ctx.author} kills {member}',
                               description=f'{ctx.author} kills {member.mention} because {reason}',
                               color=0x000000)
    killembed2.set_image(url='https://media0.giphy.com/media/lnakxcfG2MFy/giphy.gif?cid=ecf05e472df4670f3de1b99cf0d4c74fda21a320f909db8f&rid=giphy.gif')
    killembed2.set_footer(text='*Bot created (tamrol077 on github)(Discord: tamrol073#6998)*')
    killembed3 = discord.Embed(title=f'{ctx.author} kills {member}',
                               description=f'{ctx.author} kills {member.mention} because {reason}',
                               color=0x000000)
    killembed3.set_image(url='https://media3.giphy.com/media/129bQn91wmtjiw/giphy.gif')
    killembed3.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    killembed4 = discord.Embed(title=f'{ctx.author} kills {member}',
                               description=f'{ctx.author} kills {member.mention} because {reason}',
                               color=0x000000)
    killembed4.set_image(url='https://www.gif-maniac.com/gifs/30/30172.gif')
    killembed4.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    listakill = [killembed1, killembed2, killembed3, killembed4]
    if member == ctx.author:
        suicideembed = discord.Embed(title=f'{ctx.author} kills himself', description="He's probably sad", color=0x000000)
        suicideembed.set_image(
            url='https://media1.giphy.com/media/c6DIpCp1922KQ/giphy.gif')
        suicideembed.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
        suicideembed2 = discord.Embed(title=f'{ctx.author} kills himself',
                                      description="He's probably sad",
                                      color=0x000000)
        suicideembed2.set_image(
            url='https://media1.tenor.com/images/041dddf7d24b9ba3d591e0bed2ce38c7/tenor.gif?itemid=4524247')
        suicideembed2.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
        suicideembed3 = discord.Embed(title=f'{ctx.author} kills himself',
                                      description="He's probably sad",
                                      color=0x000000)
        suicideembed3.set_image(url='https://i.makeagif.com/media/9-14-2015/vyNnjt.gif')
        suicideembed3.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
        suicideembed4 = discord.Embed(title=f'{ctx.author} kills himself',
                                      description="He's probably sad",
                                      color=0x000000)
        suicideembed4.set_image(url='https://thumbs.gfycat.com/SnarlingTameEquine-max-1mb.gif')
        suicideembed4.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
        suicideembed5 = discord.Embed(title=f'{ctx.author} commits kermit suicide',
                                      description="He's probably sad",
                                      color=0x000000)
        suicideembed5.set_image(url='https://media2.giphy.com/media/13kJc5CTOnqdQk/giphy.gif')
        suicideembed5.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
        suicidio = [suicideembed, suicideembed2, suicideembed3, suicideembed4, suicideembed5]
        await ctx.send(embed=random.choice(suicidio))
    else:
        await ctx.send(embed=random.choice(listakill))


@kill.error
async def killerror(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        errore = discord.Embed(title=f'{ctx.author},you need to provide the right arguments',description=f'Check the syntax of the command in the help command.',color=0x000000)
        errore.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
        await ctx.send(embed=errore)


@client.command()
async def suicide(ctx):
    suicideembed = discord.Embed(title=f'{ctx.author} kills himself', description="He's probably sad", color=0x000000)
    suicideembed.set_image(url='https://media1.giphy.com/media/c6DIpCp1922KQ/giphy.gif')
    suicideembed.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998))*')
    suicideembed2 = discord.Embed(title=f'{ctx.author} kills himself', description="He's probably sad", color=0x000000)
    suicideembed2.set_image(
        url='https://media1.tenor.com/images/041dddf7d24b9ba3d591e0bed2ce38c7/tenor.gif?itemid=4524247')
    suicideembed2.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    suicideembed3 = discord.Embed(title=f'{ctx.author} kills himself', description="He's probably sad", color=0x000000)
    suicideembed3.set_image(url='https://i.makeagif.com/media/9-14-2015/vyNnjt.gif')
    suicideembed3.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    suicideembed4 = discord.Embed(title=f'{ctx.author} kills himself', description="He's probably sad", color=0x000000)
    suicideembed4.set_image(url='https://thumbs.gfycat.com/SnarlingTameEquine-max-1mb.gif')
    suicideembed4.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    suicideembed5 = discord.Embed(title=f'{ctx.author} commits kermit suicide',
                                  description="He's probably sad",
                                  color=0x000000)
    suicideembed5.set_image(url='https://media2.giphy.com/media/13kJc5CTOnqdQk/giphy.gif')
    suicideembed5.set_footer(text='*Bot created by (tamrol077 on github)(Discord: tamrol073#6998)*')
    suicidio = [suicideembed, suicideembed2, suicideembed3, suicideembed4, suicideembed5]
    await ctx.send(embed=random.choice(suicidio))


@client.command()
async def shot(ctx):
    salve = random.randint(1,15)
    boss = [f'{ctx.author} remains sober after {salve} shots!',f'{ctx.author} gets drunk after {salve} shots!']
    poo = random.choice(boss)
    deshqiperine = ['https://media1.tenor.com/images/4a6e5632592a753d5ddd4ecef30357e6/tenor.gif?itemid=3558432','https://media1.tenor.com/images/8e830da5d0e3e08ae2469e9bf6afc5c9/tenor.gif?itemid=8561333']
    if salve > 7:
        embed = discord.Embed(title=f'{ctx.author} drinks a shot like a true slav!', description=f'{ctx.author.mention} drinks a shot like true slav', color=0x000000)
        embed.add_field(name='Very epic, hes a true slav', value=poo, inline=False)
        embed.set_image(url=random.choice(deshqiperine))
        embed.set_footer(text='Bot made by (tamrol077 on github)(Discord: tamrol073#6998)')
    else:
        embed = discord.Embed(title=f'{ctx.author} drinks a shot like a true slav!', description=f'{ctx.author.mention} drinks a shot like true slav', color=0x000000)
        embed.add_field(name=f'{ctx.author} gets drunk after {salve} shots!', value='What a big shame', inline=False)
        embed.set_image(url=random.choice(deshqiperine))
        embed.set_footer(text='Bot made by (tamrol077 on github)(Discord: tamrol073#6998)')
    await ctx.send(embed=embed)


@client.command(aliases=['pp', 'pen', 'pene'])
async def penis(ctx, member: discord.Member):
    if ctx.channel.is_nsfw():
        value = random.randint(0, 10)
        lunghezza = '=' * value
        penis = f'8{lunghezza}D'
        salvetutti = discord.Embed(title=f"{member}'s penis", description=f"{member.mention}'s penis, requested by {ctx.author.mention}", color=0x000000)
        salvetutti.set_footer(text='Bot made by (tamrol077 on github)(Discord: tamrol073#6998)')
        if value >= 6:
            salvetutti.add_field(name=penis, value=f'{member.mention} has a big dick', inline=False)
        else:
            salvetutti.add_field(name=penis, value=f'{member.mention} has small pp', inline=False)
        await ctx.send(embed=salvetutti)
    else:
        nsfwEmbed = discord.Embed(title="You need to go in the channel settings and put the nsfw on.", description="Make sure that the channel is nsfw to use this command. For obvious reasons you cant use it in general chats.", color=0x000000)
        nsfwEmbed.set_image(url="https://scontent.cdninstagram.com/v/t51.2885-15/e15/s640x640/116783875_1444899985696850_8576624780265343485_n.jpg?_nc_ht=scontent.cdninstagram.com&_nc_cat=102&_nc_ohc=k4nGOekMDdcAX_pVj1g&oh=9b4c6ecf60a48e140d0689935fea972b&oe=5F537D06&ig_cache_key=MjM2OTY5NTIzOTkwNzg4MDUwNg%3D%3D.2")
        nsfwEmbed.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=nsfwEmbed)


@penis.error
async def peniserror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        member = ctx.author
        if ctx.channel.is_nsfw():
            value = random.randint(0, 10)
            lunghezza = '=' * value
            penis = f'8{lunghezza}D'
            salvetutti = discord.Embed(title=f"{member}'s penis",
                                       description=f"{member.mention}'s penis, requested by {ctx.author.mention}", color=0x000000)
            salvetutti.set_footer(text='Bot made by (tamrol077 on github)(Discord: tamrol073#6998)')
            if value >= 6:
                salvetutti.add_field(name=penis, value=f'{member.mention} has a big dick', inline=False)
            else:
                salvetutti.add_field(name=penis, value=f'{member.mention} has small pp', inline=False)
            await ctx.send(embed=salvetutti)
        else:
            nsfwEmbed = discord.Embed(title="You need to go in the channel settings and put the nsfw on.",
                                      description="Make sure that the channel is nsfw to use this command. For obvious reasons you cant use it in general chats.",
                                      color=0x000000)
            nsfwEmbed.set_image(url="https://scontent.cdninstagram.com/v/t51.2885-15/e15/s640x640/116783875_1444899985696850_8576624780265343485_n.jpg?_nc_ht=scontent.cdninstagram.com&_nc_cat=102&_nc_ohc=k4nGOekMDdcAX_pVj1g&oh=9b4c6ecf60a48e140d0689935fea972b&oe=5F537D06&ig_cache_key=MjM2OTY5NTIzOTkwNzg4MDUwNg%3D%3D.2")
            nsfwEmbed.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
            await ctx.send(embed=nsfwEmbed)


@client.command()
async def coinflip(ctx, scelta):
    variable = [
        'tails',
        'heads',
        'side',
    ]
    randomica = random.choice(variable)
    coinflipembed = discord.Embed(title='Coin Flip!',
                                  description='If the choice youve made matchs with the result, you win',
                                  color=0x000000)
    coinflipembed.set_image(url='https://media1.tenor.com/images/938e1fc4fcf2e136855fd0e83b1e8a5f/tenor.gif?itemid=5017733')
    coinflipembed.set_footer(text='Bot made by (tamrol077 on github)(Discord: tamrol073#6998)')
    await ctx.send(embed=coinflipembed)
    randomembed = discord.Embed(title=f'{randomica}',description='I hope that it is what you chose',color=0x000000)
    await ctx.send(embed=randomembed)
    if randomica == scelta.lower():
        vittoria = discord.Embed(title=f'{ctx.author},You won, nice!', description='Good job', color=0x000000)
        await ctx.send(embed=vittoria)
    else:
        perdita=discord.Embed(title=f'{ctx.author}, Haha you lose unlucky deserterska!',description='You lose', color=0x000000)
        await ctx.send(embed=perdita)


@coinflip.error
async def coinfliperror(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        salvini = discord.Embed(title=f'{ctx.author}, check the syntax of the command, you need to also write your choice after the command',
                                description='The choice can be; tails,heads or side',
                                color=0x000000)
        await ctx.send(embed=salvini)


@client.command()
async def dance(ctx):
    dance1 = discord.Embed(title=f'{ctx.author} dances',
                           description='Hes probably very happy because yugoslavia reunited',
                           color=0x000000)
    dance1.set_image(url='https://media1.tenor.com/images/75f0038c50cc4e2262077eef48f576c3/tenor.gif?itemid=12740205')
    dance1.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
    dance2 = discord.Embed(title=f'{ctx.author} dances',
                           description='Hes probably very happy because yugoslavia reunited',
                           color=0x000000)
    dance2.set_image(url='https://media.tenor.com/images/c3b9522dbfe8be78ff4dc305c999013e/tenor.gif')
    dance2.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
    dance3 = discord.Embed(title=f'{ctx.author} dances',
                           description='Hes probably very happy because yugoslavia reunited',
                           color=0x000000)
    dance3.set_image(url='https://media1.tenor.com/images/d736d9c410f88cb56a0f44a455e46464/tenor.gif?itemid=12740209')
    dance3.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
    dance4 = discord.Embed(title=f'{ctx.author} dances',
                           description='Hes probably very happy because yugoslavia reunited',
                           color=0x000000)
    dance4.set_image(url='https://media1.tenor.com/images/61cf901b1c520204c5c185d4a4244b78/tenor.gif?itemid=13410605')
    dance4.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
    dances = [dance1, dance2, dance3, dance4]
    await ctx.send(embed=random.choice(dances))


@client.command()
async def beep(ctx):
    beep = discord.Embed(title='Boop', description=f'{ctx.author.mention} boop!', color=0x000000)
    beep.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
    await ctx.send(embed=beep)


@client.command(aliases=['kis', 'k'])
async def kiss(ctx, member: discord.Member):
    bacio = discord.Embed(title=f'{ctx.author} kisses {member}', description=f'Very epic', color=0xFF4AC2)
    bacio.set_image(url='https://media1.tenor.com/images/e7036cbfd163f0925f0dc54d2b61dc61/tenor.gif?itemid=13795595')
    bacio.set_footer(text='Bot made by lormat770(Discord: tamrol073#6998)')
    bacio2 = discord.Embed(title=f'{ctx.author} kisses {member}', description=f'Very epic', color=0xFF4AC2)
    bacio2.set_image(
        url='https://media1.tenor.com/images/31362a548dc7574f80d01a42a637bc93/tenor.gif?itemid=13985240')
    bacio2.set_footer(text='Bot made by lormat770(Discord: tamrol073#6998)')
    bacio3 = discord.Embed(title=f'{ctx.author} kisses {member}', description=f'Very epic', color=0xFF4AC2)
    bacio3.set_image(
        url='https://media3.giphy.com/media/VFeZTupc68qrK/giphy.gif')
    bacio3.set_footer(text='Bot made by lormat770(Discord: tamrol073#6998)')
    bacio4 = discord.Embed(title=f'{ctx.author} kisses {member}', description=f'Very epic', color=0xFF4AC2)
    bacio4.set_image(
        url='https://media1.tenor.com/images/3241781470bb44b3ba0522da068dd964/tenor.gif?itemid=10528635')
    bacio4.set_footer(text='Bot made by lormat770(Discord: tamrol073#6998)')
    bacio5 = discord.Embed(title=f'{ctx.author} kisses {member}', description=f'Very epic', color=0xFF4AC2)
    bacio5.set_image(
        url='https://media1.tenor.com/images/b1189e353db0bed3521885bec284264b/tenor.gif?itemid=11453877')
    bacio5.set_footer(text='Bot made by lormat770(Discord: tamrol073#6998)')
    bacio6 = discord.Embed(title=f'{ctx.author} kisses {member}', description=f'Very epic', color=0xFF4AC2)
    bacio6.set_image(
        url='https://media1.tenor.com/images/a51e4d58d20a9636416549431e693ec1/tenor.gif?itemid=8534709')
    bacio6.set_footer(text='Bot made by lormat770(Discord: tamrol073#6998)')
    listabaci = [bacio, bacio2, bacio3, bacio4, bacio5, bacio6]
    if member == ctx.author:
        await ctx.send('Bro, do you need someone to kiss you?')
    else:
        await ctx.send(embed=random.choice(listabaci))


@kiss.error
async def kisserror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        bashar = discord.Embed(title=f'{ctx.author} check the syntax, you are missing arguments, you need to ping someone!',
                               description=f'The syntax is: kiss [user], check the syntax in the help command.',
                               color=0x000000)
        await ctx.send(embed=bashar)


@client.command()
async def howdeserterska(ctx, member: discord.Member):
    value = random.randint(0, 101)
    embed1 = discord.Embed(title=f'{member} is {value}% deserterska',
                           description=f'{member} is {value}% deserterska',
                           color=0x000000)
    embed2 = discord.Embed(title='\nGo to Goli Otok, u deserterska!I bet u are a stalinist!',
                           description=f'{member} is a dirty stalinist!', color=0x000000)
    embed2.set_image(url='https://media.giphy.com/media/2SYqI3k9PtXUhP5BRF/giphy.gif ')
    embed3 = discord.Embed(title='\n You are not so bad, but still you are a bit deserterska, btw you are still my fellow yugoslav comrade.',
                           description=f'{member} is yugoslav', color=0x000000)
    link = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.giphy.com%2Fmedia%2F3ohzdRXhwNSMt2hkYM%2Fgiphy.gif&f=1&nofb=1"
    embed3.set_image(url=link)
    embed4 = discord.Embed(title='\n You are a really good yugoslav man, Tito is proud of you!', description=f'{member}is a true Yugoslav comrade man!', color=0x000000)
    embed4.set_image(url='https://media1.tenor.com/images/5a58eea17b1a098944b8940d74dc1a6d/tenor.gif?itemid=8414357')
    await ctx.send(embed=embed1)
    if member.mention == '<@518500006588579840>':
        await ctx.send("He's too much yugoslav to be even 1% deserterska")
    if value >= 50:
        await ctx.send(embed=embed2)
    if value in range(20, 50):
        await ctx.send(embed=embed3)
    if value <= 20:
        await ctx.send(embed=embed4)


@howdeserterska.error
async def desertererror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embedmandare = discord.Embed(title=f'{ctx.author} check the syntax of the command, you need to ping an user!',
                                     description=f'The syntax is howdeserterska [user]',
                                     color=0x000000)
        await ctx.send(embed=embedmandare)


@client.command()
async def howchad(ctx, member: discord.Member):
    value = random.randint(0,101)
    yugoslav = discord.Embed(title=f'How much is {member} a chad?', description='We will find out', color=0xF09A3C)
    await ctx.send(embed=yugoslav)
    if value >= 50:
        nuovoembed = discord.Embed(title=f'{member} is {value}% chad, hes a true chad! Hes a true slav!',
                                   description='Congratulations! Tito is proud of you!',
                                   color=0x000000)
        nuovoembed.set_image(
            url='https://media3.giphy.com/media/BCIoXfA95d1ba/giphy.gif')
        await ctx.send(embed=nuovoembed)
    else:
        altroembed = discord.Embed(title=f'{member} is {value}% chad, hes a virgin! Hes not a true chad slav , send him to goli otok!', description='Tito is furious!', color=0x000000)
        altroembed.set_image(url='https://media1.tenor.com/images/6dfae6a92249e00eedc16e012f0f8a17/tenor.gif')
        await ctx.send(embed=altroembed)


@howchad.error
async def chaderror(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        member = ctx.author
        value = random.randint(0, 101)
        yugoslav = discord.Embed(title=f'How much is {member} a chad?', description='We will find out',
                                 color=0xF09A3C)
        await ctx.send(embed=yugoslav)
        if value >= 50:
            nuovoembed = discord.Embed(
                title=f'{member} is {value}% chad, hes a true chad! Hes a true slav!',
                description='Congratulations! Tito is proud of you!', color=0x000000)
            nuovoembed.set_image(url='https://media3.giphy.com/media/BCIoXfA95d1ba/giphy.gif')
            await ctx.send(embed=nuovoembed)
        else:
            altroembed = discord.Embed(
                title=f'{member} is {value}% chad, hes a virgin! Hes not a yugoslav, send him to goli otok!',
                description='Tito is furious!', color=0x000000)
            altroembed.set_image(url='https://media1.tenor.com/images/6dfae6a92249e00eedc16e012f0f8a17/tenor.gif')
            await ctx.send(embed=altroembed)


@client.command()
async def sex(ctx, member: discord.Member):
    if ctx.channel.is_nsfw():
        output_1 = discord.Embed(title='Hard sex',
                                 description='\n {} fucks hard {}'.format(ctx.author, member.mention),
                                 color=0x00ff00)
        output_1.set_image(
            url='https://images-ext-2.discordapp.net/external/okN6ZZZsSqaFF92uFpyPAJukf-wgqSrueZZVrkmUCVg/https/cdn.nekos.life/classic/classic141.gif')
        output_1.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_2 = discord.Embed(title='Hard Sex',
                                 description='\n {} creampies {}'.format(ctx.author, member.mention),
                                 color=0x00ff00)
        output_2.set_image(
            url='https://images-ext-1.discordapp.net/external/Oy3j7uuL-Vct6g39BnHW9BTlHzj1bLyXfY-wJeiqums/https/cdn.nekos.life/cum/Cum_196.gif')
        output_2.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_3 = discord.Embed(title='Hard Sex',
                                 description='\n {} cums because of {}s dick'.format(member.mention, ctx.author),
                                 color=0x00ff00)
        output_3.set_image(
            url='https://images-ext-1.discordapp.net/external/RrtzLevCiKH5_nXh_tCKViiST1ieI6iCQiUAgywOwww/https/cdn.nekos.life/cum/Cum_019.gif')
        output_3.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_4 = discord.Embed(title='Hard Sex',
                                 description='\n {} jumps on {}s dick'.format(member.mention, ctx.author),
                                 color=0x00ff00)
        output_4.set_image(
            url='https://images-ext-2.discordapp.net/external/fHilyKvmF6A8CFA5Bk2_2aQu5Irrmo2SUgUj9XD_Suo/https/cdn.nekos.life/classic/classic076.gif')
        output_4.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_5 = discord.Embed(title='Hard Sex', description='\n {} smashes {}s pussy'.format(ctx.author, member.mention), color=0x00ff00)
        output_5.set_image(
            url='https://images-ext-1.discordapp.net/external/PqSkBVBNg2YC7zJp-kpzBdqdx5OJvhvDScZfN0-oEbo/https/cdn.nekos.life/cum/cum30.gif')
        output_5.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_6 = discord.Embed(title='Hard Sex',
                                 descritpion='\n {}s pussy is full of {}s cum'.format(member.mention, ctx.author),
                                 color=0x00ff00)
        output_6.set_image(
            url='https://images-ext-2.discordapp.net/external/iK8fVtpVDh3FOKehMjE-tAL8JOHiVjhiMy-guoXj-CQ/https/cdn.nekos.life/cum/cum05.gif')
        output_6.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_7 = discord.Embed(title='Hard Sex',
                                 description='\n {} fucks furiously {}'.format(ctx.author, member.mention),
                                 color=0x00ff00)
        output_7.set_image(
            url='https://images-ext-1.discordapp.net/external/ztmY08IvGh5BeafNIpcAnmi8dOUL824zQvA9QFg1VBU/https/cdn.nekos.life/classic/classic266.gif')
        output_7.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_8 = discord.Embed(title='Mad Sex yes yes',
                                 description='\n{} smashes {} like Poland.'.format(ctx.author, member.mention),
                                 color=0x00ff00)
        output_8.set_image(
            url='https://images-ext-2.discordapp.net/external/_aTmeyYcVvmHlzQFx3DkJG6yi5zd1IRLebJ7BY9poQc/https/cdn.nekos.life/classic/classic_101.gif')
        output_8.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_9 = discord.Embed(title='Sex',
                                 description='\n{} smashes {} like maginot line'.format(ctx.author, member.mention),
                                 color=0x00ff00)
        output_9.set_image(
            url='https://images-ext-1.discordapp.net/external/Tn_5hNXmV7xPBYXq0kFUntI7CfysKKKUvmSbfHOFt5I/https/cdn.boob.bot/Gifs/15FB.gif')
        output_9.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_10 = discord.Embed(title='Sex',
                                  description='\n {} fucks {}'.format(ctx.author, member.mention),
                                  color=0x00ff00)
        output_10.set_image(
            url='https://images-ext-1.discordapp.net/external/OOgTjeOeBqE5GOPi3Ol66X4YyKUTzoPIuNnVwQv0p9o/https/cdn.boob.bot/Gifs/1847.gif')
        output_10.set_footer(text='*Bot created by tamrol073#6998(github: tamrol077)*')
        output_11 = discord.Embed(title='Sex',
                                  description="\n {} puts his dick in {}'s mouth".format(ctx.author, member.mention),
                                  color=0x00ff00)
        output_11.set_image(
            url='https://images-ext-2.discordapp.net/external/Z_PCeXhWwn3YneNPXhQg8Lrz-eb-Ntj8eFmarfGntsM/https/cdn.boob.bot/Gifs/1853.gif')
        output_11.set_footer(text='*Bot created by lormat770(Discord: tamrol077#3458)*')
        output_list = [output_1, output_2, output_3, output_4, output_5, output_6, output_7, output_8, output_9, output_10, output_11]
        if member == ctx.author:
            await ctx.send('You cant fuck yourself!')
        elif member != ctx.author:
            await ctx.send(embed=random.choice(output_list))

    else:
        nsfwembed = discord.Embed(title="You need to go in the channel settings and put the nsfw on.",
                                  description="Make sure that the channel is nsfw to use this command. For obvious reasons you cant use it in general chats.",
                                  color=0x000000)
        nsfwembed.set_image(
            url="https://scontent.cdninstagram.com/v/t51.2885-15/e15/s640x640/116783875_1444899985696850_8576624780265343485_n.jpg?_nc_ht=scontent.cdninstagram.com&_nc_cat=102&_nc_ohc=k4nGOekMDdcAX_pVj1g&oh=9b4c6ecf60a48e140d0689935fea972b&oe=5F537D06&ig_cache_key=MjM2OTY5NTIzOTkwNzg4MDUwNg%3D%3D.2")
        nsfwembed.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=nsfwembed)


@sex.error
async def sex_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed= discord.Embed(
            title='Give all the required arguments to the bot',
                             description='Give all the required arguments',
                             color=0x00ff00)
        embed.add_field(name=f'The sintax is: sex [user]',
                        value='The command will not run if you dont give the right sintax',
                        inline=False)
        await ctx.send(embed=embed)


# Various Commands:


@client.command(aliases=["fox"])
async def randomfox(ctx):
    async with ctx.channel.typing():
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://randomfox.ca/floof/") as r:
                data = await r.json()
                embed = discord.Embed(title="Random Fox")
                embed.set_image(url=data["image"])
                embed.set_footer(text="http:randomfox.ca/")
                await ctx.send(embed=embed)


@client.command(aliases=["dog"])
async def randomdog(ctx):
    async with ctx.channel.typing():
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://random.dog/woof.json") as r:
                data = await r.json()
                embed = discord.Embed(title="Random Dog")
                embed.set_image(url=data["url"])
                embed.set_footer(text="https://random.dog/")
                await ctx.send(embed=embed)


@client.command(aliases=["inv"])
async def invite(ctx):
    inviteEmbed = discord.Embed(title="Tito bot invite",
                                description="[Click here](https://discord.com/oauth2/authorize?client_id=740866037645443134&scope=bot&permissions=1174528) to invite the bot",
                                color=0x000000)
    inviteEmbed.set_thumbnail(
        url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
    await ctx.send(embed=inviteEmbed)


@client.command(aliases=["h"])
async def help(ctx,*,sector="0"):
    results = collection.find({"_id": str(ctx.guild.id)})
    for result in results:
        prefissoepico = result["prefix"]
    if str(sector) == "1":
        helpEmbed1 = discord.Embed(title="Help 1: **Various commands**", description="Tito Bot made with discord.py. [] are required arguments, () are optional arguments.",color=0x036ffc)
        helpEmbed1.add_field(name="Prefix:",
                             value=f"The actual prefix in the server is: **{prefissoepico}**",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}getprefix",
                             value="Returns the actual prefix in the server. You can change it with the next command.",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}changeprefix [new prefix]",
                             value="You change the prefix in the server, and you specify a new one to use.",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}ping",
                             value="Returns the bot latency",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}members",
                             value="Returns the number of members in the server.",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}serverinfo",
                             value="Returns info about the server youre currently in.", inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}userinfo [user]",
                             value="Returns info about a specific user",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}info/bot-info",
                             value="Get info about the bot and the dev of the bot",
                             inline=False)
        helpEmbed1.add_field(name=f"⚪ {prefissoepico}invite",
                             value="Returns the bot invite, to invite tito to your server.",
                             inline=False)
        helpEmbed1.set_thumbnail(
            url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
        helpEmbed1.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=helpEmbed1)
    elif str(sector) == "2":
        helpEmbed2 = discord.Embed(
            title="Help 2: **Levels/Money commands**",
                                   description="Tito Bot made with discord.py.[] are required arguments, () are optional arguments.",
                                   color=0x036ffc)
        helpEmbed2.add_field(name="Prefix:",
                             value=f"The actual prefix in the server is: **{prefissoepico}**",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}level",
                             value="Shows your level in the server",
                             inline=False)
        helpEmbed2.add_field(name=f"To increase your xp, just write in text chats",
                             value="And then your level will increase.",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}balance (user)",
                             value="Shows how many money you have.",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}work",
                             value="Work to gain money.",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}beg",
                             value="Beg for money. You can get money, but its not sure",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}crime",
                             value="Commit crime, you have low probability of getting money and yugoslav police can fine you.",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}give [user] [amount]",
                             value="Gives an amount of money to an user.", inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}shop",
                             value="Shows the shop of tech squad bot. Cool things to buy.", inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}rob [user]",
                             value="Steals the money from an user.",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}buy [item]",
                             value="Buys an item in the shop.",
                             inline=False)
        helpEmbed2.add_field(name=f"⚪ {prefissoepico}status",
                             value="Show if your tito bot status is premium or standard. To buy the premium status, go in the shop and buy it.",
                             inline=False)
        helpEmbed2.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        helpEmbed2.set_thumbnail(
            url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
        await ctx.send(embed=helpEmbed2)
    elif str(sector) == "3":
        helpEmbed3 = discord.Embed(title="Help 3: **Moderation Commands**",
                                   description="Tito Bot made with discord.py. [] are required arguments, () are optional arguments. ",
                                   color=0x036ffc)
        helpEmbed3.add_field(name="Prefix:",
                             value=f"The actual prefix in the server is: **{prefissoepico}**",
                             inline=False)
        helpEmbed3.add_field(name=f"⚪ {prefissoepico}kick [user]",
                             value="The bot kicks the specified user.",
                             inline=False)
        helpEmbed3.add_field(name=f"⚪ {prefissoepico}ban [user]",
                             value="The bot bans the specified user.",
                             inline=False)
        helpEmbed3.add_field(name=f"⚪ {prefissoepico}unban [user]",
                             value="The bot unbans the specified user.",
                             inline=False)
        helpEmbed3.add_field(name=f"⚪ {prefissoepico}clear [number of messages]",
                             value="The bot clears the specified number of messages",
                             inline=False)
        helpEmbed3.add_field(name=f"⚪ {prefissoepico}changenickname [user] [new nickname]",
                             value="The bot clears the specified number of messages",
                             inline=False)
        helpEmbed3.set_thumbnail(
            url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
        helpEmbed3.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=helpEmbed3)
    elif str(sector) == "4":
        helpEmbed4 = discord.Embed(title="Help 4: **Fun Commands**",
                                   descriptioN="Tito Bot made with discord.py. [] are required arguments, () are optional arguments. ",
                                   color=0x036ffc)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}suicide",
                             value="If youre sad you can kill yourself with the suicide command",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}kill [user] (reason) ",
                             value="Kills an user.",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}coinflip [choice]  ",
                             value="Play coinflip.",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}penis [user]  ",
                             value="Lenght of pp of an user.This command can be used only in nsfw commands. ",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}shot ",
                             value="Drink a shot of vodka like true slav!",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}howchad [user] ",
                             value="How chad a user is?. If he is a chad he is a true yugoslav, cuz yugoslav is chad.",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}howdeserterska [user] ",
                             value="Check if the user likes tito. If he is a deserterska send him to goli otok!",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}dance ",
                             value="Dance if you're happy cuz yugoslavia reunited.",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}beep ",
                             value="Returns boop!",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}kiss [user] ",
                             value="You kiss an user!",
                             inline=False)
        helpEmbed4.add_field(name=f"⚪ {prefissoepico}sex [user] ",
                             value="You fuck an user. This command can be used ONLY in nsfw commands.",
                             inline=False)
        helpEmbed4.set_thumbnail(
            url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
        helpEmbed4.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=helpEmbed4)
    elif str(sector) == "5":
        helpEmbed5 = discord.Embed(title="Help 5: **Img Commands**",
                                   description="Tito Bot made with discord.py. [] are required arguments, () are optional arguments.",
                                   color=0x036ffc)
        helpEmbed5.add_field(name=f"⚪ {prefissoepico}randomdog",
                             value="Send image of random dog.",
                             inline=False)
        helpEmbed5.add_field(name=f"⚪ {prefissoepico}randomfox ",
                             value="Send image of random fox.",
                             inline=False)
        helpEmbed5.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=helpEmbed5)

    elif str(sector) == "0":
        helpEmbed = discord.Embed(title="Help: **Tito Bot Help Command**",
                                  description="The Bot was made with discord.py by tamrol073#6998(tamrol077 on github).The bot has: various commands, fun commands, prefix commands, moderation commands and level/money system. [] are required arguments, () are optional arguments. Write help [the number you want] to get help about that specific topic. If you dont use the bot, youre a deserterska. ",
                                  color=0x036ffc)
        helpEmbed.add_field(name="Prefix:",
                            value=f"The actual prefix in the server is: **{prefissoepico}**",
                            inline=False)
        helpEmbed.add_field(name=f"**1: Various commands**",
                            value=f"Write {prefissoepico}help 1 to view various commands help",
                            inline=False)
        helpEmbed.add_field(name=f"**2: Level/Money Commands**",
                            value=f"Write {prefissoepico}help 2 to view Money/Level commands help",
                            inline=False)
        helpEmbed.add_field(name=f"**3: Moderation commands**",
                            value=f"Write {prefissoepico}help 3 to view Moderation commands help, you can use them only if you have moderator role.",
                            inline=False)
        helpEmbed.add_field(name=f"**4: Fun commands**",
                            value=f"Write {prefissoepico}help 4 to view Fun Commands",
                            inline=False)
        helpEmbed.add_field(name=f"**5: Img commands**",
                            value=f"Write {prefissoepico}help 5 to view Img Commands help",
                            inline=False)
        helpEmbed.set_thumbnail(
            url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
        helpEmbed.set_footer(text="*Bot created by tamrol073#6998(github: tamrol077)*")
        await ctx.send(embed=helpEmbed)


@client.command(aliases=["bot-info"])
async def info(ctx):
    infoEmbed = discord.Embed(title="Tito Bot 2.0 Info:",
                              description="Information and descrtiption about tito bot, a bot developed by tamrol073#6998",
                              color=0xFF0000)
    infoEmbed.add_field(name="Brief description of Tito Bot:",
                        value="The bot is a simply meme/fun bot with commands mainly about politics and yugoslavia. It has various features like: levelling/economy and mod commands.", inline=False)
    infoEmbed.add_field(name="Library used:",
                        value="The bot was developed with discord.py",
                        inline=False)
    infoEmbed.add_field(name="Help Command:",
                        value=".help",
                        inline=False)
    infoEmbed.add_field(name="Support server:",
                        value="[Click here to join](https://discord.gg/dd9U7hS)",
                        inline=False)
    infoEmbed.add_field(name="Bot Invite link:",
                        value="[Click here to invite the bot in your server](https://discord.com/oauth2/authorize?client_id=740866037645443134&scope=bot&permissions=1174528)",
                        inline=False)
    infoEmbed.add_field(name="Bot owner:",
                        value="tamrol073 #6998",
                        inline=False)
    infoEmbed.set_footer(
        text="Bot created by tamrol073#6998(github: tamrol077)")
    infoEmbed.set_thumbnail(
        url="https://kickasshistory.files.wordpress.com/2014/07/josip_broz_tito_official_portrait.jpg")
    await ctx.send(embed=infoEmbed)


@client.command()
async def getprefix(ctx):
  results = collection.find({"_id": str(ctx.guild.id)})
  for result in results:
    chinamad = result["prefix"]
  await ctx.send(f"The actual prefix in the server is: **{chinamad}**")


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency *1000)}ms')


@client.command(aliases=["cp", "changep", "prefixchange"])
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, new_prefix):
    collection.update_one({"_id": str(ctx.guild.id)}, {"$set": {"prefix": str(new_prefix)}})
    await ctx.send(f"Prefix changed to {new_prefix} ")


@changeprefix.error
async def prefixerror2(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        errorEmbed2 = discord.Embed(title="You dont have permissions",
                                    description=f"You need admin permissions to use this command,{ctx.author}",
                                    color=0xFF0000)
        await ctx.send(embed=errorEmbed2)
    if isinstance(error, commands.BotMissingPermissions):
        errorEmbed2 = discord.Embed(title="You dont have permissions",
                                    description=f"You need admin permissions to use this command,{ctx.author}",
                                    color=0xFF0000)
        await ctx.send(embed=errorEmbed2)


@changeprefix.error
async def prefixerror(ctx, error):
    errorEmbed = discord.Embed(title="Command error",
                               description=f"{ctx.author},you need to specify the new prefix, you havent specified any.",
                               color=0xFF0000)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=errorEmbed)


# Mod commands:


@client.command()
@commands.has_permissions(administrator=True)
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"I purged {amount} messages! 🛢 ")
    time.sleep(2)
    await ctx.channel.purge(limit=1)


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send('I dont have the permission to use this command, try give me admin permissions.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You probably dont have perms to use this command.")


@client.command()
@commands.has_permissions(administrator=True)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    banembed = discord.Embed(title=f'{member} banned from the server by {ctx.author}.',
                             description=f'Reason: {reason}', color=0x000041)
    await ctx.send(embed=banembed)


@ban.error
async def error2(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        noargument = discord.Embed(title='You need to ping an user',
                                   description=f'The syntax is {PREFIX}ban [user]', color=0x000000)
        noargument.set_footer(text='*Bot created by lormat770(Discord: tamrol077#3458)*')
        await ctx.send(embed=noargument)


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        nopermessi = discord.Embed(title='I dont have permission to use this command.',
                                   description='Give me admin permission to make me use this command', color=0x000000)
        nopermessi.set_footer(text='*Bot created by lormat770(Discord: tamrol077#3458)*')
        await ctx.send(embed=nopermessi)


@client.command()
@commands.has_permissions(administrator=True)
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return


@client.command()
@commands.has_permissions(administrator=True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    kickembed = discord.Embed(title=f'{member} kicked from the server by {ctx.author}.',
                              description=f'Reason: {reason}', color=0x000041)
    await ctx.send(embed=kickembed)


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        salve = discord.Embed(title=f'I cant use this command,{ctx.author}, because I dont have permissions',
                              description='Try to give me: \nPermission to kick members\nAdmin permissions',
                              color=0x000000)
        await ctx.send(embed=salve)
    if isinstance(error, commands.BotMissingPermissions):
        salve2 = discord.Embed(title=f'I cant use this command,{ctx.author}, because I dont have permissions',
                               description='Try to give me: \nPermission to kick members\nAdmin permissions',
                               color=0x000000)
        await ctx.send(embed=salve2)
    if isinstance(error, commands.MissingPermissions):
        salve3 = discord.Embed(title=f'Check ur perms,{ctx.author} to use this command',
                               description='You need to have admin permissions.', color=0x000000)
        await ctx.send(embed=salve3)


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        salve = discord.Embed(title=f'Specify a person to kick,{ctx.author}.',
                              description='Try watching the command syntax in the help command', color=0x000000)
        await ctx.send(embed=salve)


#Info Commands:


@client.command(aliases=["uinfo", "u-info"])
async def userinfo(ctx, member: discord.Member):
    roles = [role for role in member.roles]

    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

    embed.set_author(name=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

    embed.add_field(name="User ID:", value=member.id)
    embed.add_field(name="Member name:", value=member.display_name)
    embed.add_field(name='Boosted:', value= str(bool(member.premium_since)))

    embed.add_field(name="Account Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
    embed.add_field(name="Top role:", value=member.top_role.mention)

    embed.add_field(name="Is he a bot?", value=member.bot)

    await ctx.send(embed=embed)

@userinfo.error
async def userError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        member = ctx.author
        roles = [role for role in member.roles]

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name="User ID:", value=member.id)
        embed.add_field(name="Member name:", value=member.display_name)
        embed.add_field(name='Boosted:', value=str(bool(member.premium_since)))

        embed.add_field(name="Account Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Top role:", value=member.top_role.mention)

        embed.add_field(name="Is he a bot?", value=member.bot)

        await ctx.send(embed=embed)


@client.command(aliases=["sinfo", "s-info"])
async def serverinfo(ctx):
    header = f'Server Information: {ctx.guild.name}'
    embedman = discord.Embed(title=header, description='Discord Server information by: Tito Bot', color=0x000000)
    embedman.add_field(name='Name:', value=f'{ctx.guild.name}')
    embedman.add_field(name='ID:', value=f'{ctx.guild.id}')
    embedman.add_field(name='Region:', value=f'{ctx.guild.region}')
    embedman.add_field(name='Owner:', value=f'{ctx.guild.owner.display_name}')
    embedman.add_field(name='Shard ID:', value=f'{ctx.guild.shard_id}')
    embedman.add_field(name='Created on:', value=ctx.guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embedman.add_field(name='Number of Members:', value=f'{len(ctx.guild.members)}')
    embedman.set_thumbnail(url=ctx.guild.icon_url)
    embedman.set_footer(text='Bot made by tamrol077(Discord:  tamrol077#3458')
    await ctx.send(embed=embedman)


@client.command(aliases=["servermembers", "users"])
async def members(ctx):
    await ctx.send(f"The server has: {len(ctx.guild.members)} members!")


# Voice Commands:


@client.command(pass_context=True, aliases=['j', 'joi', 'J'])
async def join(ctx):
    channel = ctx.author.voice.channel
    if channel:
        await channel.connect()
        await ctx.send('🔊Im entering the voice chat...')
    else:
        await ctx.send('Noo no man')


@client.command(pass_context=True, aliases=['l', 'L', 'leav'])
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send('🙋‍♂️Im exiting the voice channel!')


@client.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("You need to put a link")
        return

    await ctx.send("▶Now playing...")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"▶Playing: {nname[0]}")
    print("playing\n")


@client.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("⏸Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing. Failed pause. Try to play some music")


@client.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("🔊Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("🔊Music is not paused, pause it first to resume it!")


@client.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("🛑Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")


@client.command()
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        await ctx.send("The bot is not connected to a voice channel.")

    ctx.voice_client.source.volume = volume / 100
    await ctx.send("Changed volume to {}%".format(volume))


@volume.error
async def volumeerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        volumeerrorembed = discord.Embed(title="Volume command Error.",
                                         description=f"{ctx.author}, you need to specify the volume", color=0xfc032d)
        await ctx.send(embed=volumeerrorembed)


client.run(TOKEN)

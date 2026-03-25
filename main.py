import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

JAIL_CHANNEL_NAME = "prigione"


@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} è online!")


@bot.command()
@commands.has_permissions(administrator=True)
async def jail(ctx, member: discord.Member):
    """Manda un utente in prigione e gli dà il ruolo Maranza"""
    jail_channel = discord.utils.get(ctx.guild.voice_channels, name=JAIL_CHANNEL_NAME)
    maranza_role = discord.utils.get(ctx.guild.roles, name="Maranza")

    if maranza_role:
        try:
            # Aggiunge SEMPRE il ruolo Maranza
            await member.add_roles(maranza_role)
            print(f"Ruolo Maranza aggiunto a {member.name}")

            # Sposta in prigione SOLO se è già in vocale
            if member.voice and jail_channel:
                await member.move_to(jail_channel)
                print(f"{member.name} spostato in prigione")

        except Exception as e:
            print(f"ERRORE jail: {e}")


@bot.command()
@commands.has_permissions(administrator=True)
async def free(ctx, member: discord.Member):
    """Libera un utente dalla prigione e rimuove il ruolo Maranza"""
    maranza_role = discord.utils.get(ctx.guild.roles, name="Maranza")
    jail_channel = discord.utils.get(ctx.guild.voice_channels, name=JAIL_CHANNEL_NAME)

    try:
        # Rimuovi il ruolo Maranza
        if maranza_role:
            await member.remove_roles(maranza_role)
            print(f"Ruolo Maranza rimosso da {member.name}")

        # Se l'utente è in prigione, disconnettilo dalla vocale
        if member.voice and member.voice.channel == jail_channel:
            await member.move_to(None)  # Disconnette dalla vocale
            print(f"{member.name} disconnesso dalla prigione")

    except Exception as e:
        print(f"ERRORE free: {e}")


@bot.event
async def on_voice_state_update(member, before, after):
    """Controlla gli utenti con ruolo Maranza e li sposta in prigione"""
    jail_channel = discord.utils.get(member.guild.voice_channels, name=JAIL_CHANNEL_NAME)
    maranza_role = discord.utils.get(member.guild.roles, name="Maranza")

    # Se l'utente si connette a un canale vocale E ha il ruolo Maranza
    if after.channel and not before.channel and maranza_role in member.roles:
        if jail_channel and after.channel != jail_channel:
            try:
                await member.move_to(jail_channel)
                print(f"{member.name} automaticamente spostato in prigione")
            except:
                pass

    # Mantiene i prigionieri in prigione (codice originale)
    elif jail_channel and before.channel == jail_channel and after.channel != jail_channel:
        try:
            await member.move_to(jail_channel)
            print(f"{member.name} cercato di uscire dalla prigione, riportato indietro")
        except:
            pass


@jail.error
async def jail_error(ctx, error):
    pass


@free.error
async def free_error(ctx, error):
    pass


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
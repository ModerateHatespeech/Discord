"""
Toxicity Content Bot by ModerateHatespeech.com
@description Scans Discord server for content that is considered toxic and reports the messages to moderators
@version 1.0.0
@last_updated 6/8/2022
"""
from discord.ext import commands
import discord
import json
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument
import requests
import re

def load_config():
  """ Load configuration file """
  with open("config.json", "r") as f:
    config = json.load(f)
    missing = ["bot_token", "api_token", "channel_id", "threshold"] - config.keys()
    if len(missing) > 0:
      raise KeyError("Missing keys in config.json {0}".format(str(missing)))
    return config

def flush_config(config):
  with open("config.json", "w") as f:
    config = json.dump(config, f)
    
def moderate(text, thresh):
  """ Call API and return response list with boolean & confidence score """
  text = re.sub(r'>[^\n]+', "", text) # strip out quotes
  response = requests.post("https://api.moderatehatespeech.com/api/v1/toxic/", json={"token":config['api_token'], "text":text}).json()

  if response['response'] != "Success":
    if response['response'] != "Authentication failure":
      raise AttributeError('Invalid response: {0}'.format(response['response']))
    else:
      raise RuntimeError('Fatal response: {0}'.format(response['response']))

  if response['class'] == "flag" and float(response['confidence']) > thresh:
    return [True, round(float(response['confidence']), 3)]

  return [False, round(float(response['confidence']), 3)]

""" Helper functions for messages """
async def send_error(ctx, message):
  await ctx.send(
    embed = discord.Embed(title="Error", description=message, color=discord.Color.red())
  )

async def send_success(ctx, message):
  await ctx.send(
    embed = discord.Embed(title="Success!", description=message, color=discord.Color.green())
  )
  
bot = commands.Bot(command_prefix='$')

""" 
Define event handlers for bot
- On login, send welcome message
- When a message sent, run pre-request checks, then send message to API
"""
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
  if message.author == bot.user:
      return
    
  await bot.process_commands(message)

  global config
  if config['status']:
    response = moderate(message.content, config['threshold'])
    if response[0]:
      channel, stripped = await bot.fetch_channel(config['channel_id']), message.content.replace('\n', '\n> ')
      resp = discord.Embed(title="Detected: Toxic Message", url=message.jump_url, description=f"> {stripped}\n\n{response[1]*100}% Confidence", color=discord.Color.orange())
      resp.set_footer(text="Analyzed by ModerateHatespeech's AI")
      await channel.send(
        embed = resp
      )

""" 
Define command handlers for bot
- Configure settings on the fly
- Enable/Disable bot
- Show help screen
"""
@bot.command()
@has_permissions(ban_members=True)
async def cminit(ctx, channel, confidence):
  global config
  try:
    config['channel_id'], config['threshold'] = channel, float(confidence)
    flush_config(config)
    await send_success(ctx, f"You've successfully set the configuration for the bot.")
  except ValueError:
    await send_error(ctx, "Invalid confidence threshold: must be a number 0 to 1")

@bot.command()
@has_permissions(ban_members=True)
async def status(ctx, status):
  if status not in ['enabled', 'disabled']:
    await send_error(ctx, "Please choose set the status to `enabled` to `disabed`")
  else:
    global config
    config['status'] = False if status == "disabled" else True
    flush_config(config)
    await send_success(ctx, f"You've successfully {status} the bot.")

bot.remove_command("help")

@bot.command()
@has_permissions(ban_members=True)
async def help(ctx):
  await ctx.send(
    embed = discord.Embed(title="ContentMod Help", description="**Purpose:** Automate the detection of hateful and uncivil content on your server.\n\n**Commands:**\n`$cminit [channel_id] [threshold]`\nConfigure the channel to send reports to, and confidence level (from 0 to 1) to report at\n\n`$status [enabled|disabled]`\nEnable or disable message reports\n\n**Privacy:** We do not and will never log any messages submitted to our API. [Details](https://moderatehatespeech.com/terms-and-privacy/)")
  )

""" 
Define command error handlers for bot
- When a user doesn't have valid permissions to manage the bot
- When a user fails to pass the required arguments
"""
@cminit.error
async def cminit_error(ctx, error):
    if isinstance(error, MissingPermissions):
      await send_error(ctx, "You need `ban_members` permission to do that.")
    elif isinstance(error, MissingRequiredArgument):
      await send_error(ctx, "Please include the `channel_id` to send reports to and then the `confidence threshold` (0-1) to report on.")

@status.error
async def status_error(ctx, error):
  if isinstance(error, MissingPermissions):
    await send_error(ctx, "You need `ban_members` permission to do that.")
  elif isinstance(error, MissingRequiredArgument):
    await send_error(ctx, "Please choose set the status to `enabled` to `disabed`")

config = load_config()

bot.run(config['bot_token'])

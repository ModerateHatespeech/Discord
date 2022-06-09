# Discord
Automatically moderate subreddits via API

## Purpose
The following python script runs a Discord bot that will auto-report content flagged as "Toxic" by our API to a channel. Follow the instructions below to self-host. Note: only add the self-hosted bot to servers you trust. 

If you're just looking to add the bot to your server, use the following link: [https://discord.com/api/oauth2/authorize?client_id=984268119797276682&permissions=68608&scope=bot](https://discord.com/api/oauth2/authorize?client_id=984268119797276682&permissions=68608&scope=bot)

## Requirements
Install requirements:
```apt-get install python3
pip3 install discord.py requests
```

Required config.json file:
```json
{
  "api_token": "MODERATE_HATESPEECH_API_TOKEN",
  "bot_token": "DISCORD_BOT_TOKEN"
}
```


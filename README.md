# Discord
Automatically moderate subreddits via API

## Purpose
The following python script runs a Discord bot that will auto-report content flagged as "Toxic" by our API to a channel.

## Requirements
Install requirements:
```apt-get install python3
pip3 install discord.py requests
```

Required config.json file:
```json
{
  "api_token": "MODERATE_HATESPEECH_API_TOKEN",
}
```


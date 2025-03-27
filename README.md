# Discord Message Deletion Tool

*A simple open-source tool for deleting messages in a Discord channel. Provide a Discord bot token, channel ID, and user ID to remove messages sent by a specific user.*

## Features
- Deletes messages from a specified user in a given channel.
- Uses Discord API for efficient bulk deletion.
- Simple command-line interface.

## Requirements
- Python 3.x
- `requests` library (install with `pip install requests`)

## Config
- ``--token``: Your bot's/your authentication token.
- ``--channel`` : The channel ID from which messages will be deleted.
- ``--user``: The user ID whose messages will be deleted.

## Disclaimer
- Deleting messages in bulk is against Discord's API Terms of Service if done improperly. Use responsibly.
- If you're using a bot, it must have the necessary permissions in the server and channel.

# ChatBot-TeleBot

The same thing as [ChatBot CLI](https://github.com/FINN-2005/ChatBot-CLI) but as a Telegram Bot.

## Functionality

To chat, just start the `ollama` service and then run the Python bot file.

## Commands

- `/start` — Start the bot and get a welcome message.
- `/help` — Show all available commands.
- `/clear` — Clear your chat context/history.
- `/clear_all` — Clear all users' chat contexts (admin only).
- `/bye` — Stop talking to the bot.
- `/change_model` — Change the current Ollama model (admin only).

## Setup

1. Clone this repo.
```bash
git clone https://github.com/FINN-2005/ChatBot-TeleBot.git
```
2. Create a `data.json` file based on the provided template and fill in your bot token, whitelist, models, and settings.
```json
{
    "bot_token" : "0123456789:PutBotTokenHere012345678901_abcdefgh",
    "whitelist" : {
        "finn" : 1234567890
    },
    "admin" : "finn",
    "model_list" : {
        "gemma3" : "gemma3:1b",
        "gemma3 4" : "gemma3:4b",
        "spicy" : "unfiltered"
    },
    "model_name" : "gemma3",
    "system_prompt" : ""
}
```
3. Install dependencies.
```bash
pip install telepot jsonschema ollama
```
4. Start your Ollama service.
```bash
ollama serve
```
5. Run the bot.
```bash
python telebot_ai.py
```
or
```bash
python streaming_telebot_ai.py
```

### NOTE: The Streaming version is far from perfect. 
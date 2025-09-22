import time
import telepot
from telepot.loop import MessageLoop
import ollama
import re

import json
from jsonschema import validate

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "bot_token": {"type": "string", "pattern": "^[0-9]+:.+"},
        "whitelist": {"type": "object",
                      "additionalProperties": {"type": "integer"}},
        "admin": {"type": "string"},
        "model_list": {"type": "object",
                       "additionalProperties": {"type": "string"}},
        "model_name": {"type": "string"},
        "system_prompt": {"type": "string"}  # optional
    },
    "required": ["bot_token", "whitelist", "admin", "model_list", "model_name"],
    "additionalProperties": False
}

def validate_config(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    validate(instance=data, schema=CONFIG_SCHEMA)
    if data["admin"] not in data["whitelist"]:
        raise ValueError("admin must be in whitelist")
    if data["model_name"] not in data["model_list"]:
        raise ValueError("model_name must be one of model_list keys")
    return data

class Bot:
    def __init__(self) -> None:
        data = validate_config('data.json')
        self.bot_token = data['bot_token']
        self.whitelist = data['whitelist']
        self._admin = data['admin']

        # Ollama thingys
        self.model_list = data['model_list']
        self.model_name = self.model_list[data['model_name']]
        self.context = {self.whitelist[id]: [] for id in self.whitelist.keys()}
        self.system_prompt = data.get('system_prompt', '')
        self.user_prompt = ''
        
        # Telebot thingys
        self.bot = telepot.Bot(self.bot_token)
        MessageLoop(self.bot, self.handle).run_as_thread()
        
        self.commands = {
            '/start': self.command_start,
            '/help': self.command_help,
            '/clear': self.command_clear,
            '/clear_all': self.command_clear_all,
            '/bye': self.command_bye,
            '/change_model': self.command_change_model,
            }
        
        self.start_message = 'Hi!\nStart Typing Messages to Chat!'
        self.bye_message = 'See ya\n'
        self.change_model_message = "\n".join(self.model_list.keys())
        
        self.running = True
        self.changing_model = False
        self.run_for_ever()
        
    def handle(self, msg):
        content_type, _, chat_id = telepot.glance(msg)
        
        if content_type == 'text':
            if chat_id in self.whitelist.values():
                # Handle model change
                if self.changing_model and chat_id == self.whitelist[self._admin]:
                    if msg['text'].lower() in self.model_list.keys():
                        self.model_name = self.model_list[msg['text'].lower()]
                        self.changing_model = False
                        self.command_clear(chat_id, msg)
                        if self.model_list[msg['text'].lower()] == self.model_name:
                            self.bot.sendMessage(chat_id, 'Model has been updated')
                        elif msg['text'] == 'Cancel':
                            self.changing_model = False
                            self.bot.sendMessage(chat_id, 'Model updation cancelled')
                        else:
                            self.bot.sendMessage(chat_id, 'Failed to change model')
                    else:
                        self.bot.sendMessage(chat_id, 'Incorrect model name!\nSay "Cancel" to cancel')
                
                else:
                    if chat_id == self.whitelist[self._admin] and msg['text'] in self.commands.keys():
                        self.commands[msg['text']](chat_id, msg)
                    else:
                        self.lummma(chat_id, msg)
            else:
                self.bot.sendMessage(chat_id, 'You are not authorized to command this bot')
    
    def command_start(self,chat_id,_msg):
        self.bot.sendMessage(chat_id,self.start_message)
    
    def command_help(self,chat_id,_msg):
        self.bot.sendMessage(chat_id,"\n".join(self.commands.keys()))

    def command_clear(self, chat_id, _msg):
        self.context[chat_id].clear()
        self.bot.sendMessage(chat_id,'Your context has been deleted.')
    
    def command_clear_all(self, chat_id, _msg):
        for id in self.context:
            self.context[id].clear()
        self.bot.sendMessage(chat_id,'All context has been deleted.')
    
    def command_change_model(self, chat_id, msg):
        self.changing_model = True
        self.bot.sendMessage(chat_id,'Please choose a model:')
        self.bot.sendMessage(chat_id,self.change_model_message)
    
    def command_bye(self, chat_id, _msg):
        self.bot.sendMessage(chat_id,self.bye_message)
        self.running = False
    
    def lummma(self,chat_id,msg):
        self.user_prompt = msg['text']
        response = ollama.generate(model=self.model_name, prompt=self.user_prompt, system=self.system_prompt, context=self.context[chat_id])
        self.context[chat_id] = response['context']
        for message in self.check_message_too_long(response['response'], 1000):
            self.bot.sendMessage(chat_id, message)
    
    def run_for_ever(self):
        try: 
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print('---------------------------------------------------------------------------------------------------------------------------------')
            
    def check_message_too_long(self, message, max_length=2000):
        sentences = re.split(r'(?<=[.!?]) +', message)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " "
                current_chunk += sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
            
if __name__ == "__main__":
    Bot()

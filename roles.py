import telegram
import json
import copy
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue
from abc import ABC, abstractmethod
from chat import Chat
from player import Player

class Role:
    @staticmethod
    def json_to_dict(json_input) -> dict:
        json_input = json_input.replace("\'", "\"")
        json_input = json_input.replace('"is_bot": False', '"is_bot": "False"') # replace boolean in json with string
        json_input = json_input.replace('"is_bot": True', '"is_bot": "True"')
        return json.loads(json_input)

    @staticmethod
    def button_change(time: int, reply_markup, msg: Message) -> None : 
        token = "5517840013:AAE41tDz97NjTHmT5b_2_pZNyzfF073yEoY"
        updater = Updater(token, use_context=True)
        jobqueue = updater.job_queue
        def change(context: telegram.ext.CallbackContext) -> None :
            msg.edit_reply_markup(reply_markup=reply_markup)
        jobqueue.run_once(callback=change, when=time, context=None, name=None, job_kwargs=None)
        jobqueue.start()

    @staticmethod
    def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu

    @abstractmethod
    def from_dict(self, source: dict):
        pass

    def update_attribute(self, chat_ref, chat_id: int, target: int) :
        pass
    
class Town(Role):
    pass

class Mafia(Role):
    pass
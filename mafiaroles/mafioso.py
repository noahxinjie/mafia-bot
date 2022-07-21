from roles import *
from player import Player
from chat import Chat
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue
    
class Mafioso(Mafia):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]

    @staticmethod
    def info() -> str :
        return "Mafioso is part of the Mafia. There is at most 1 mafioso in a game. The mafioso can use their ability during the "\
                "night to kill someone. However, if the Godfather is alive, the mafioso will attack the "\
                    "godfather's target for the godfather instead."
    
    
    # Kill someone
    def ability(self, bot: Bot, chat: Chat, chat_ref, player_ref, chat_id: int) -> None:
        temp_alive = copy.deepcopy(chat.alive)
        temp_town = copy.deepcopy(chat.town)
        options = []
        count = 0
        for x in temp_alive :
            if x in temp_town :
                name = chat.players[str(x)]["name"]
                options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
                count += 1
        reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
        msg = bot.send_message(chat_id=self.user_id, text='Who do you want to kill tonight?', reply_markup=reply)
        options1 = []
        options1.append(InlineKeyboardButton(text='Night time is over.', callback_data="nothing"))
        reply1 = InlineKeyboardMarkup([options1])
        Role.button_change(time=75, reply_markup=reply1, msg=msg)
from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Framer(Mafia):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]

    @staticmethod
    def info() -> str :
        return "Framer is part of the Mafia. There are at most 3 framers in a game. The framer can use can use their ability "\
            "during the night to frame someone to tamper with investigative results related to their target."
    
    
    # Frames someone as guilty
    def ability(self, bot: Bot, chat: Chat, chat_ref, player_ref, chat_id: int) -> None:
        temp_alive = copy.deepcopy(chat.alive)
        temp_alive.remove(self.user_id)
        options = []
        for x in temp_alive :
            name = chat.players[str(x)]["name"]
            options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
        reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
        msg = bot.send_message(chat_id=self.user_id, text='Who do you want to frame tonight?', reply_markup=reply)
        options1 = []
        options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
        reply1 = InlineKeyboardMarkup([options1])
        Role.button_change(time=75, reply_markup=reply1, msg=msg)
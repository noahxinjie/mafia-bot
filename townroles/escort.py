from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Escort(Town):
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
        return "Escort is part of the Town. There are at most 3 escorts in a game. The escort can use their ability during "\
            "the night to block another player's ability."
    
    # Prevent someone from using role
    def ability(self, bot: Bot, alive_list: list, graveyard_list: list, town_list: list, mafia_list: list, player_ref, chat_ref) -> None:
        temp_alive = copy.deepcopy(alive_list)
        temp_alive.remove(self.user_id)
        options = []
        for x in temp_alive :
            player = Player(0, 0, "")
            doc = player_ref.document(str(x)).get()
            player.from_dict(doc.to_dict())
            name = player.name
            options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
        reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
        msg = bot.send_message(chat_id=self.user_id, text='Who do you want to roleblock tonight?', reply_markup=reply)
        options1 = []
        options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
        reply1 = InlineKeyboardMarkup([options1])
        Role.button_change(time=75, reply_markup=reply1, msg=msg)

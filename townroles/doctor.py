from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Doctor(Town):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0
        self.heal_self = 1

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            "heal_self": self.heal_self
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]
        self.heal_self = source["heal_self"]

    @staticmethod
    def info() -> str :
        return "Doctor is part of the Town. There are at most 3 doctors in a game. The doctor can use their ability during the "\
            "night to heal someone, preventing them from dying. The doctor can also choose to heal themself for "\
                "only 1 time."
    
   # Save someone from dying
    def ability(self, bot: Bot, chat: Chat, chat_ref, player_ref, chat_id: int) -> None:
        temp_alive = copy.deepcopy(chat.alive)
        if self.heal_self == 0 :
            #remove user from list
            temp_alive.remove(self.user_id)
        options = []
        for x in temp_alive :
            name = chat.players[str(x)]["name"]
            options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
        reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
        msg = bot.send_message(chat_id=self.user_id, text='Who do you want to heal tonight? ' +
            'You can also heal yourself, but only once.', reply_markup=reply)
        options1 = []
        options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
        reply1 = InlineKeyboardMarkup([options1])
        Role.button_change(time=75, reply_markup=reply1, msg=msg)

    def update_attribute(self, chat_ref, chat_id: int, target: int):
        if target == self.user_id :
            self.heal_self -= 1
            key_string = "players." + str(self.user_id) + ".instance"
            chat_ref.document(str(chat_id)).update({key_string : str(self)})
        

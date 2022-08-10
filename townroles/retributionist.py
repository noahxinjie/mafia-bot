from roles import *
from player import Player
from chat import Chat
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Retributionist(Town):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0
        self.revive = 1

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            "revive": self.revive
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]
        self.revive = source["revive"]

    @staticmethod
    def info() -> str :
        return "Retributionist is part of the Town. There are at most 2 retributionists in a game. The retributionist can use "\
            "their ability during the night to revive a dead Town player for a maximum of 1 time."

   # Revive a dead Town player
    def ability(self, bot: Bot, chat: Chat, chat_ref, player_ref, chat_id: int) -> None:
        temp_graveyard = copy.deepcopy(chat.graveyard)
        temp_town = copy.deepcopy(chat.town)
        if self.revive == 1 :
            if len(temp_graveyard) == 0 :
                bot.send_message(chat_id=self.user_id, text= 'There is no one in the graveyard that you can revive yet.')
            else :
                options = []            
                temp_cleaned = copy.deepcopy(chat.cleaned)

                for x in temp_graveyard :
                    if x in temp_town and x not in temp_cleaned:
                        name = chat.players[str(x)]["name"]
                        options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
                reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
                msg = bot.send_message(chat_id=self.user_id, text='Who do you want to revive? You can only revive someone once', reply_markup=reply)
                options1 = []
                options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
                reply1 = InlineKeyboardMarkup([options1])
                Role.button_change(time=75, reply_markup=reply1, msg=msg)

        else :
            bot.send_message(chat_id=self.user_id, text= 'You have already revived someone before.')
        
    def update_attribute(self, chat_ref, chat_id: int, target: int):
        self.revive -= 1
        key_string = "players." + str(self.user_id) + ".instance"
        chat_ref.document(str(chat_id)).update({key_string : str(self)})
        

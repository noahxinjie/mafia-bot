from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Vigilante(Town):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0
        self.bullets = 3
        self.guilt = 0

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            "bullets": self.bullets,
            "guilt": self.guilt
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]
        self.bullets = source["bullets"]
        self.guilt = source["guilt"]
    
    @staticmethod
    def info() -> str :
        return "Vigilante is part of the Town. There are at most 2 vigilantes in a game. The vigilante can use their ability "\
            "during the night to shoot a person, for a maximum of 3 times. The vigilante can't use their ability on the first night."\
            "\nThe Vigilante will become guilt-ridden if they shot a Town member previously and lose all their bullets."

    # can shoot up to 3 people
    # cannot shoot on 1st night
    def ability(self, bot: Bot, alive_list: list, graveyard_list: list, town_list: list, mafia_list: list, player_ref, chat_ref) -> None:
        temp_alive = copy.deepcopy(alive_list)
        temp_alive.remove(self.user_id)
        if self.guilt == 1 :
            bot.send_message(chat_id=self.user_id, text= 'You are too guilt-ridden to pick up your gun again after shooting a fellow Town member.')
        else : 
            if self.bullets != 0 :
                options = []
                for x in temp_alive :
                    player = Player(0, 0, "")
                    doc = player_ref.document(str(x)).get()
                    player.from_dict(doc.to_dict())
                    name = player.name
                    options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
                reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
                msg = bot.send_message(chat_id=self.user_id, text='Who do you want to shoot tonight?\n' +
                    f'Number of bullets left: {self.bullets}', reply_markup=reply)
                options1 = []
                options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
                reply1 = InlineKeyboardMarkup([options1])
                Role.button_change(time=75, reply_markup=reply1, msg=msg)
            else :
                bot.send_message(chat_id=self.user_id, text= 'You have run out of bullets.')

    def update_attribute(self, player_ref, player: Player, target: int):
        self.bullets -= 1
        player.role_instance = str(self)
        player_ref.document(str(self.user_id)).set(player.to_dict())
        

from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Veteran(Town):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0
        self.alerts = 3

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            "alerts": self.alerts
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]
        self.alerts = source["alerts"]

    @staticmethod
    def info() -> str :
        return "Veteran is part of the Town. There are at most 2 veterans in a game. The veteran can use their ability during "\
            "the night to go on alert for a maximum of 3 times. While on alert, the Veteran is immune to attacks"\
            "and kills everyone who visits them."
    
    
    # Goes on alert to gain immunity and shoot everyone who visits him
    def ability(self, bot: Bot, alive_list: list, graveyard_list: list, town_list: list, mafia_list: list, player_ref, chat_ref) -> None:
        player = Player.get_player(id=self.user_id, player_db=player_ref)
        self.immunity = 0
        player.role_instance = str(self)
        player_ref.document(str(self.user_id)).set(player.to_dict())
        if self.alerts != 0 :
            options = []
            options.append(InlineKeyboardButton(text='Yes', callback_data='Ability:1'))
            options.append(InlineKeyboardButton(text='No', callback_data='Ability:2'))
            reply = InlineKeyboardMarkup([options])
            msg = bot.send_message(chat_id=self.user_id, text='Do you wish to go on alert tonight?\n' +
                f'Number of alerts left: {self.alerts}', reply_markup=reply)
            options1 = []
            options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
            reply1 = InlineKeyboardMarkup([options1])
            Role.button_change(time=75, reply_markup=reply1, msg=msg)

        else :
            bot.send_message(chat_id=self.user_id, text='You have already gone on alert for 3 times.')

    def update_attribute(self, player_ref, player: Player, target: int):
        if target == 1 :
            self.alerts -= 1
            self.immunity += 1
            player.role_instance = str(self)
            player_ref.document(str(self.user_id)).set(player.to_dict())
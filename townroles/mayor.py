from roles import *
from chat import Chat
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Mayor(Town):
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
        return 'Mayor leads the Town. There is at most 1 mayor in a game. The mayor can use their ability anytime during '\
            'the day to triple his voting power during voting and judgement phases. However, they will be revealed as the' \
                'Mayor to everyone.'

    def ability(self, bot: Bot) -> None:
        if self.votes == 1:
            options = []
            options.append(InlineKeyboardButton(text='Yes', callback_data='Ability:1'))
            reply = InlineKeyboardMarkup([options])
            msg = bot.send_message(chat_id=self.user_id, text='Click the button below any time during the day phase to reveal ' + 
                'yourself as Mayor to triple your voting power. ', reply_markup=reply)
            
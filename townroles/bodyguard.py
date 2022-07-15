from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Bodyguard(Town):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0
        self.vest = 1

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            "vest": self.vest
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]
        self.vest = source["vest"]

    @staticmethod
    def info() -> str :
        return "Bodyguard is part of the Town. There are at most 3 bodyguards in a game. The bodyguard can use their ability during "\
            "the night to protect someone from death. They will kill someone who attacks their protectee and die in the process." \
                "The bodyguard can choose to vest up to protect themself for only 1 time."
    
    # protect someone and kill his attacker if he is attacked
    def ability(self, bot: Bot, alive_list: list, graveyard_list: list, town_list: list, mafia_list: list, player_ref, chat_ref) -> None:
        temp_alive = copy.deepcopy(alive_list)
        if self.vest == 0 :
            # remove user from the list
            temp_alive.remove(self.user_id)
        options = []
        for x in temp_alive :
            player = Player(0, 0, "")
            doc = player_ref.document(str(x)).get()
            player.from_dict(doc.to_dict())
            name = player.name
            options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
        reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
        msg = bot.send_message(chat_id=self.user_id, text='Who do you want to protect tonight? ' +
        'You can also choose to protect yourself by putting on a bulletproof vest, but only once.', reply_markup=reply)
        options1 = []
        options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
        reply1 = InlineKeyboardMarkup([options1])
        Role.button_change(time=75, reply_markup=reply1, msg=msg)

    def update_attribute(self, player_ref, player: Player, target: int):
        if target == self.user_id :
            self.vest -= 1
            player.role_instance = str(self)
            player_ref.document(str(self.user_id)).set(player.to_dict())

    
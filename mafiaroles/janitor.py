from roles import *
from player import Player
import telegram
import json
import copy
import time
from telegram import Bot, InlineKeyboardButton, Update, ForceReply, User, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue

class Janitor(Mafia):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.votes = 1
        self.immunity = 0
        self.cleans = 3

    def __str__(self):
        dict1 = dict(
            {"user_id": self.user_id,
            "votes": self.votes,
            "immunity": self.immunity,
            "cleans": self.cleans
            }
        )

        return json.dumps(dict1)

    def from_dict(self, source: dict):
        self.user_id = source["user_id"]
        self.votes = source["votes"]
        self.immunity = source["immunity"]
        self.cleans = source["cleans"]
    
    @staticmethod
    def info() -> str :
        return "Janitor is part of the Mafia. There are at most 2 janitors in a game. The janitor can use their ability during "\
            "the night to clean up a dead body killed by the Mafia. Such bodies cannot be revived by a Retributionist "\
                "and information about them will not be available. The janitor can only use their ability for a maximum " \
                    "of 3 times."

    # Prevent someone from using role
    # Cleans up someone killed by mafia
    # The corpse's role cannot be deduced
    def ability(self, bot: Bot, alive_list: list, graveyard_list: list, town_list: list, mafia_list: list, player_ref, chat_ref) -> None:
        temp_alive = copy.deepcopy(alive_list)
        temp_alive.remove(self.user_id)
        options = []
        for x in temp_alive :
            player = Player.get_player(id=x, player_db=player_ref)
            name = player.name
            options.append(InlineKeyboardButton(text=f'{name}', callback_data='Ability:' + str(x)))
        reply = InlineKeyboardMarkup(Role.build_menu(options, n_cols=1))
        msg = bot.send_message(chat_id=self.user_id, text='Whose body, if he is killed, do you wish to clean tonight?', reply_markup=reply)
        options1 = []
        options1.append(InlineKeyboardButton(text='Ability time is over.', callback_data="nothing"))
        reply1 = InlineKeyboardMarkup([options1])
        Role.button_change(time=75, reply_markup=reply1, msg=msg)

    def update_attribute(self, player_ref, player: Player, target: int):
        self.cleans -= 1
        player.role_instance = str(self)
        player_ref.document(str(self.user_id)).set(player.to_dict())
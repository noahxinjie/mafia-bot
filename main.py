from calendar import c
from cgitb import text
from email.mime import message
from genericpath import exists
from heapq import merge
from itertools import count
from multiprocessing.connection import wait
from pickle import TRUE
import statistics
import logging
import time
import math
from multiprocessing import context
from chat import Chat
from player import Player
from settings import Settings
from townroles import *
from mafiaroles import *
from townroles.doctor import Doctor
from townroles.mayor import Mayor
from townroles.bodyguard import Bodyguard
from townroles.escort import Escort
from townroles.investigator import Investigator
from townroles.lookout import Lookout
from townroles.retributionist import Retributionist
from townroles.sheriff import Sheriff
from townroles.transporter import Transporter
from townroles.veteran import Veteran
from townroles.vigilante import Vigilante
from mafiaroles.consigliere import Consigliere
from mafiaroles.consort import Consort
from mafiaroles.framer import Framer
from mafiaroles.godfather import Godfather
from mafiaroles.janitor import Janitor
from mafiaroles.mafioso import Mafioso
import json
import copy
import os
import random
import telegram
import firebase_admin
import investigative_results
from result_handling import result_handling
from update_stats import update_stats
from check_win_condition import check_win_condition

PORT = int(os.environ.get('PORT', '8443'))
#CRED = "C:/Users/noahx/OneDrive/Desktop/Orbital/tgmafiabot-angklxinjie-firebase-adminsdk-txg45-0fb49aa518.json"
CRED = "/Users/me/Downloads/tgmafiabot-angklxinjie-firebase-adminsdk-txg45-0fb49aa518.json"

from telegram import Bot, CallbackQuery, InlineKeyboardButton, Message, Update, ForceReply, User, InlineKeyboardMarkup, Poll
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext, JobQueue, CallbackQueryHandler,
ContextTypes, PollAnswerHandler, PollHandler)
from firebase_admin import credentials, firestore

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#token = "5214730582:AAF8DlfXooiQf3qgilICfM3kp6u2e6jNFNA"
token = "5517840013:AAE41tDz97NjTHmT5b_2_pZNyzfF073yEoY"

#cred = credentials.Certificate(json.load(open(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))))
cred = credentials.Certificate(CRED)
firebase_admin.initialize_app(cred)

bot = telegram.Bot(token)
database = firestore.client()

chat_ref = database.collection("Chat Groups")
player_ref = database.collection("Players")
setting_ref = database.collection("Settings")
global_doc1 = database.collection("Global").document("stats for games with fewer than 8 players")
global_doc2 = database.collection("Global").document("stats for games with more than 8 players")

roles_dict = {1:'Mayor', 2:'Escort', 3:'Transporter', 4:'Retributionist', 5:'Vigilante', 6:'Veteran', 7:'Bodyguard', 8:'Doctor',
    9:'Investigator', 10:'Sheriff', 11:'Lookout', 12:'Godfather', 13:'Mafioso', 14:'Consort', 15:'Consigliere', 
        16:'Janitor', 17:'Framer'}

dups = {1:1, 2:3, 3:2, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:3, 11:3, 12:1, 13:1, 14:3, 15:1, 16:2, 17:3}

role_instance_dict = {1: Mayor(0), 2: Escort(0), 3: Transporter(0), 4: Retributionist(0), 5: Vigilante(0), 6: Veteran(0), 
    7: Bodyguard(0), 8: Doctor(0), 9: Investigator(0), 10: Sheriff(0), 11: Lookout(0), 12: Godfather(0), 13: Mafioso(0), 
        14: Consort(0), 15: Consigliere(0), 16: Janitor(0), 17: Framer(0)}

# Define a few command handlers. These usually take the two arguments update and
# context.

def json_to_dict(x) -> dict:
    x = x.replace("\'", "\"")
    x = x.replace('"is_bot": False', '"is_bot": "False"') # replace boolean in json with string
    x = x.replace('"is_bot": True', '"is_bot": "True"')
    return json.loads(x)

def remove_from_list(list1, removed) -> None:
    y = json_to_dict(str(removed))
    removed_id = y["id"]
    for x in list1 :
        z = json_to_dict(x)
        z_id = z["id"]
        if removed_id == z_id :
            list1.remove(x)
            break

def join(update : Update, _: CallbackContext) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id
    name = user.full_name
    if chat_id == user_id :
        update.message.reply_text("Invalid command. Please use /join in a group chat.")
    else :
        player_doc = player_ref.document(str(user_id)).get()
        if not player_doc.exists :
            player_ref.document(str(user_id)).set(Player(user_id, chat_id, name).to_dict())
        else :
            player = Player(0, 0, "")
            player.from_dict(player_doc.to_dict())
            if player.chat_id != chat_id :
                player.chat_id = chat_id
                player_ref.document(str(user_id)).set(player.to_dict())
        doc = chat_ref.document(str(chat_id)).get()
        if not doc.exists :
            update.message.reply_text('There is no ongoing game now. Use /start to initialize a new game.')
        else :
            chat = Chat()
            chat.from_dict(doc.to_dict())
            if chat.game_state == 0 :
                update.message.reply_text('There is no ongoing game now. Use /start to initialize a new game.')
            elif chat.game_state == 1 :
                if user_id in chat.alive :
                    update.message.reply_text(f'{name} has already joined the game!')
                else :
                    current_chat_ref = chat_ref.document(str(chat_id))
                    s = "players." + str(user_id)
                    if len(chat.players) < 14 : 
                        current_chat_ref.update({s : 0})                      
                        current_chat_ref.update({"alive": firestore.ArrayUnion([user_id])})
                        doc = chat_ref.document(str(chat_id)).get()
                        chat.from_dict(doc.to_dict())
                        update_msg = f'{name} has joined the game. *For first-time users, do use /start in a private message to the Mafia Moderator Bot.*\nNumber of people in game lobby now: {len(chat.players)}\nPeople in the game lobby:'
                        count = 1
                        for x in chat.alive :
                            player = Player(0, 0, "")
                            player_doc = player_ref.document(str(x)).get()
                            player.from_dict(player_doc.to_dict())
                            update_msg += f'\n{count}. {player.name}'
                            count += 1
                        bot.send_message(chat_id=chat_id, text=update_msg, parse_mode=telegram.ParseMode.MARKDOWN)
                    elif len(chat.players) == 14 :
                        current_chat_ref.update({s : 0})
                        current_chat_ref.update({"alive": firestore.ArrayUnion([user_id])})
                        update.message.reply_text(
                            fr'{name} joined the game. Lobby is full now, use /start to start the game.')
                    else :
                        update.message.reply_text(
                        fr'{name} cannot join the game as the lobby is full. Use /start to start the game.')  
            else :
                update.message.reply_text(
                    f'{name} cannot join the game as it has already started.')      

def start(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id == user_id :
        update.message.reply_text('Welcome to Mafia Bot. This chat is the place where you make individual decisions during games.')
    else :
        doc = chat_ref.document(str(chat_id)).get()
        if not doc.exists :
            chat_ref.document(str(chat_id)).set(Chat().to_dict())
            setting_ref.document(str(chat_id)).set(Settings().to_dict())
        doc = chat_ref.document(str(chat_id)).get()
        chat = Chat()
        chat.from_dict(doc.to_dict())    
        if chat.game_state == 0 :
            chat.game_state = 1
            chat_ref.document(str(chat_id)).set(chat.to_dict())
            update.message.reply_text('Game is initialized. At least 4 people must join before the game can be started.' +
                ' Use /join to join the game. When everyone that will be playing (up to a cap of 15 people) ' +
                    'has joined, use /start to start the game.')
        elif chat.game_state == 1:
            if len(chat.players) < 1 :
                update.message.reply_text('At least 4 people must join before the game can be started.' +
                    ' Use /join to join the game. When everyone that will be playing (up to a cap of 15 people) ' +
                        'has joined, use /start to start the game.')
            else :
                chat.game_state = 2
                chat_ref.document(str(chat_id)).set(chat.to_dict())
                update.message.reply_text('Game is starting.')

                number_of_players = len(chat.alive)
                if number_of_players >= 6 :
                    tbd = 0.3 * number_of_players
                else :
                    tbd = 0.25 * number_of_players

                digit = math.floor(tbd)
                decimal = tbd % 1
                random_number = random.randint(0, 9)
                if random_number < decimal:
                    extra = 1
                else:
                    extra = 0

                number_of_mafia_players = digit + extra
                number_of_town_players = number_of_players - number_of_mafia_players

                #Creating random list of players
                random_list = copy.deepcopy(chat.alive)
                random.shuffle(random_list)
                dups1 = copy.deepcopy(dups)

                def role(number: int, id: int) -> None:
                    role1 = roles_dict.get(number) # name of role
                    dups1[number] = dups1[number] - 1 # updating role duplicate pool
                    chat.players[str(id)] = number 
                    chat_ref.document(str(chat_id)).set(chat.to_dict())
                    # retrieving player instance mapped to id
                    player = Player(0, 0, "")
                    doc = player_ref.document(str(id)).get()
                    player.from_dict(doc.to_dict())
                    # creating role instance and updating player instance with it
                    instance = role_instance_dict.get(number) 
                    instance1 = copy.deepcopy(instance)
                    instance1.user_id = id
                    player.role_instance = str(instance1)
                    player_ref.document(str(id)).set(player.to_dict())
                    bot.send_message(id, f'Your role is {role1}.')
                
                if number_of_players > 7 :
                    # GUARANTEED ROLES
                    #Choosing support
                    #support_id = random_list.pop(0)
                    #chat.town.append(support_id)
                    #number = random.randint(1, 4)
                    #role(number, support_id)

                    #Choosing killing
                    #killing_id = random_list.pop(0)
                    #chat.town.append(killing_id)
                    #number = random.randint(5, 6)
                    #role(number, killing_id)

                    #Choosing protective
                    #protective_id = random_list.pop(0)
                    #chat.town.append(protective_id)
                    #number = random.randint(7, 8)
                    #role(number, protective_id)
                        
                    #Choosing investigative
                    #investigative_id = random_list.pop(0)
                    #chat.town.append(investigative_id)
                    #number = random.randint(9, 11)
                    #role(number, investigative_id)

                    number_of_random_town_players = number_of_town_players - 4  
                            
                #Choosing mafia killing
                #maf_killing_id = random_list.pop(0)
                #chat.mafia.append(maf_killing_id)
                #number = random.randint(12, 13)
                #role(number, maf_killing_id)
                
                # Define assign function
                def assign(number: int) -> None:
                    if dups1.get(number) != 0 :
                        next_player_id = random_list.pop(0)
                        if number < 12 :
                            chat.town.append(next_player_id)
                        else :
                            chat.mafia.append(next_player_id)
                        role(number, next_player_id)
                    else :
                        if number < 12 :
                            number = random.randint(1, 11)
                            assign(number)
                        else :
                            number = random.randint(12, 17)
                            assign(number)
                
                # Assign remaining town players 
                #for x in range(number_of_random_town_players): 
                number = random.randint(6, 6)
                assign(number)

                # Assign remaining mafia players            
                #for x in range(number_of_mafia_players - 1):
                number = random.randint(12, 12)
                assign(number)

                #Sending a message of mafia list to all in mafia faction
                msg = 'People who are part of the Mafia are:'
                count = 1
                for x in chat.mafia :
                    role_name = roles_dict.get(chat.players[str(x)])
                    player = Player(0, 0, "")
                    player_doc = player_ref.document(str(x)).get()
                    player.from_dict(player_doc.to_dict())
                    name = player.name
                    msg += f'\n{count}. {name} Role: {role_name}'
                    count += 1                   
                
                for x in chat.mafia:
                    bot.send_message(x, msg)

                def check_game_state() -> bool :
                    chat1 = Chat()
                    chat_doc = chat_ref.document(str(chat_id)).get()
                    chat1.from_dict(chat_doc.to_dict())
                    if chat1.game_state == -1 :                           
                        chat = Chat()
                        chat_ref.document(str(chat_id)).set(chat.to_dict())
                        return True                    
                    return False
     
                #Day1
                if check_game_state() :
                    return

                chat_settings = Settings()
                settings_doc = setting_ref.document(str(chat_id)).get()
                chat_settings.from_dict(settings_doc.to_dict())
                discussion_time = chat_settings.discussion
                bot.send_message(chat_id=chat_id, text=f'Day 1 is starting now. Discussion time: {discussion_time} seconds')
                
                #sending ability message to mayor
                #finding mayor from players dict
                def mayor_ability() -> None:
                    if dups1[1] == 0 :
                        list1 = [*chat.players.keys()]
                        list2 = [*chat.players.values()]
                        mayor_id_string = list1[list2.index(1)]
                        a = [int(s) for s in mayor_id_string.split() if s.isdigit()]
                        mayor_id = a[0]
                        if mayor_id in chat.alive :
                            #retrieving player instance of mayor
                            player = Player(0, 0, "")
                            doc = player_ref.document(str(mayor_id)).get()
                            player.from_dict(doc.to_dict())
                            #retrieving role instance of mayor
                            z = player.role_instance
                            dict1 = json_to_dict(z)
                            instance = role_instance_dict.get(1) # getting dummy role instance
                            instance1 = copy.deepcopy(instance)
                            instance1.from_dict(dict1)
                            instance1.ability(bot=bot)
                
                mayor_ability()

                y = discussion_time / 10

                for x in range(int(y)) :
                    if check_game_state() :
                        return
                    if x == y - 2 and y > 2:
                        bot.send_message(chat_id=chat_id, text='20 seconds till end of discussion.')
                    time.sleep(10)

                bot.send_message(chat_id=chat_id, text='Day 1 has ended.')
      
                # Night 1
                if check_game_state() :
                    return
                chat.game_state = 3
                chat_ref.document(str(chat_id)).set(chat.to_dict())
                night_time = chat_settings.night
                bot.send_message(chat_id=chat_id, text=f'Night 1 is starting now. Decision time: {night_time} seconds. Use this time to ' +
                    'decide how to use your ability.')
                for x in chat.alive :
                    role_number = chat.players[str(x)]
                    # retrieving player instance mapped to current iteration
                    player = Player(0, 0, "")
                    doc = player_ref.document(str(x)).get()
                    player.from_dict(doc.to_dict())
                    # retrieving role instance
                    z = player.role_instance
                    dict1 = json_to_dict(z)
                    instance = role_instance_dict.get(role_number) # getting dummy role instance
                    instance1 = copy.deepcopy(instance)
                    instance1.from_dict(dict1)
                    if len(chat.players) < 8 :
                        # if mafia killing
                        if role_number == 12 or role_number == 13 :
                            bot.send_message(chat_id=x, text="You decide to relax for a night as it is a small Town around here.")
                        # if vigilante
                        elif role_number == 5 :
                            bot.send_message(chat_id=x, text="You decide to wait a night before shooting.")
                        # else if not mayor
                        elif role_number != 1 :
                            instance1.ability(bot, chat.alive, chat.graveyard, chat.town, chat.mafia, player_ref, chat_ref) 
                    else :
                        if role_number == 5 :
                            bot.send_message(chat_id=x, text="You decide to wait a night before shooting.")
                        elif role_number != 1 :
                            instance1.ability(bot, chat.alive, chat.graveyard, chat.town, chat.mafia, player_ref, chat_ref) 
                    
                y = night_time / 10
                
                for x in range(int(y)) :
                    if check_game_state() :
                        return
                    if x == y - 2 and y > 2 :
                        bot.send_message(chat_id=chat_id, text='20 seconds till end of Night 1')
                    time.sleep(10)

                bot.send_message(chat_id=chat_id, text='Night 1 has ended.')
      
                doc = chat_ref.document(str(chat_id)).get()
                chat.from_dict(doc.to_dict())
                day_message = result_handling(chat_ref=chat_ref, chat_id=chat_id, chat=chat, player_ref=player_ref, bot=bot)

                doc = chat_ref.document(str(chat_id)).get()
                chat.from_dict(doc.to_dict())

                def mafia_promotion() -> None :
                    killing_present = False
                    for x in chat.mafia :
                        if chat.players[str(x)] == 12 or chat.players[str(x)] == 13 :
                            killing_present = True
                            break
                    if killing_present == False :
                        if len(chat.mafia) != 0 :
                            random_choice = random.choice(chat.mafia)
                            chat.players[str(random_choice)] = 13
                            chat_ref.document(str(chat_id)).set(chat.to_dict())
                            player = Player(0, 0, "")
                            doc = player_ref.document(str(random_choice)).get()
                            player.from_dict(doc.to_dict())
                            player.role_instance = str(Mafioso(random_choice))
                            player_ref.document(str(random_choice)).set(player.to_dict())
                            name = player.name
                            for y in chat.mafia :  
                                if y == random_choice :
                                    bot.send_message(chat_id=y, text="You have been promoted to Mafioso!")
                                else :
                                    bot.send_message(chat_id=y, text=f"{name} has been promoted to Mafioso!")
                
                # Check if at least one mafia killing is still alive
                mafia_promotion()
                # Check if any faction has won/died out at this point
                check_win_condition(number=1, player_ref=player_ref, chat_ref=chat_ref, chat=chat, role_instance_dict=role_instance_dict, chat_id=chat_id)

                doc = chat_ref.document(str(chat_id)).get()
                chat.from_dict(doc.to_dict())

                day = 2
                while chat.game_state != 0 and chat.deathless_phases < 6:
                    # Check game state at start of every day
                    if check_game_state() :
                        return
                    chat.game_state = 2
                    chat_ref.document(str(chat_id)).set(chat.to_dict())
                    #Discussion
                    bot.send_message(chat_id=chat_id, text=f'Day {day} is starting now.')
                    bot.send_message(chat_id=chat_id, text=day_message)
                    day_message = ""
                    bot.send_message(chat_id=chat_id, text=f'Use this time to discuss what happened yesterday night. Discussion time: {discussion_time} seconds')
                    # sending ability message to mayor
                    # finding mayor from players dict
                    mayor_ability()
                    
                    y = discussion_time / 10
                    
                    for x in range(int(y)) :
                        if check_game_state() :
                            return
                        if x == y - 2 and y > 2 :
                            bot.send_message(chat_id=chat_id, text='20 seconds till end of discussion.')
                        time.sleep(10)

                    bot.send_message(chat_id=chat_id, text='Discussion has ended.')
      
                    
                    #Voting
                    if check_game_state() :
                        return
                    voting_time = chat_settings.voting
                    bot.send_message(chat_id=chat_id, text=f'Voting is starting now. Time: {voting_time} seconds')

                    chat.voting = {}
                    chat.defendant = -1
                    chat_ref.document(str(chat_id)).set(chat.to_dict())

                    def button_change(time: int, reply_markup, msg: Message) -> None : 
                        updater = Updater(token, use_context=True)
                        job1 = updater.job_queue
                        def change(context: telegram.ext.CallbackContext) -> None :
                            msg.edit_reply_markup(reply_markup=reply_markup)
                        job1.run_once(callback=change, when=time, context=None, name=None, job_kwargs=None)
                        job1.start()
                    
                    def voting_poll() -> None :
                        temp_list = copy.deepcopy(chat.alive)
                        options = []
                        voting_threshold = math.floor(len(chat.alive)/2) + 1
                        voting_msg = f"Day {day} Voting\n{voting_threshold} votes are needed to vote someone to the stand."
                        voting_msg += "\nDo note that your vote will be voided if you vote for yourself"\
                        " or if you are not a currently alive player."
                        for x in temp_list:                            
                            player = Player(0, 0, "")
                            doc = player_ref.document(str(x)).get()
                            player.from_dict(doc.to_dict())
                            name = player.name
                            options.append(name)
                        message = bot.send_poll(
                            chat_id=update.effective_chat.id,
                            question=voting_msg,
                            options=options,
                            is_anonymous=False, 
                            allows_multiple_answers=False,
                            open_period=30)

                        payload = {
                            message.poll.id: {
                                "message_id": message.message_id,
                                "chat_id": update.effective_chat.id,
                            }
                        }
                        context.bot_data.update(payload)

                    voting_poll()
                       
                    y = voting_time / 10
                    
                    for x in range(int(y)) :
                        if check_game_state() :
                            return
                        if x == y - 2 and y > 2 :
                            bot.send_message(chat_id=chat_id, text='20 seconds till end of voting.')
                        time.sleep(10)

                    bot.send_message(chat_id=chat_id, text='Voting has ended.')
      

                    doc = chat_ref.document(str(chat_id)).get()
                    chat.from_dict(doc.to_dict())
                        
                    if chat.defendant != -1 :
                        #Defence
                        if check_game_state() :
                            return
                        defendant_id = chat.defendant
                        player = Player(0, 0, "")
                        doc = player_ref.document(str(defendant_id)).get()
                        player.from_dict(doc.to_dict())
                        defendant_name = player.name
                        defence_time = chat_settings.defence
                        bot.send_message(chat_id=chat_id, text=f'{defendant_name} has been voted to the stand. Defence time: {defence_time} seconds. ' +
                            f'{defendant_name}, use this time to defend yourself.')
                        
                        y = defence_time / 10
                    
                        for x in range(int(y)) :
                            if check_game_state() :
                                return
                            if x == y - 2 and y > 2 :
                                bot.send_message(chat_id=chat_id, text='20 seconds till end of defence.')
                            time.sleep(10)
                        
                        bot.send_message(chat_id, 'Defence time has ended.')
                        #Judgement
                        if check_game_state() :
                            return
                        judgement_time = chat_settings.judgement
                        bot.send_message(chat_id=chat_id, text='Judgement is starting now. Please vote guilty or innocent or abtain ' +
                            f'Time: {judgement_time} seconds')
                        
                        chat.innocent = []
                        chat.guilty = []
                        chat_ref.document(str(chat_id)).set(chat.to_dict())

                        #Sending individual prompt to alive players except defendant on their judgement choice
                        def judgement(id: int) -> None:
                            button1 = InlineKeyboardButton(text='Innocent', callback_data=f'Judgement:1')
                            button2 = InlineKeyboardButton(text='Guilty', callback_data=f'Judgement:2')
                            button3 = InlineKeyboardButton(text='Abstain', callback_data=f'Judgement:3')
                            reply = InlineKeyboardMarkup([[button1], [button2], [button3]])
                            msg = bot.send_message(chat_id=id, text=f'Determine if {defendant_name} is innocent or ' +
                                'guilty. You can also choose to abstain from the vote.', reply_markup=reply)
                            button4 = InlineKeyboardButton(text='Voting time is over', callback_data='nothing')
                            reply1 = InlineKeyboardMarkup([[button4]])
                            button_change(15, reply1, msg)

                        list = copy.deepcopy(chat.alive)
                        # exclude the one voted on stand
                        list.remove(defendant_id)
                    
                        for x in list :
                            judgement(x)

                        y = judgement_time / 10
                    
                        for x in range(int(y)) :
                            if check_game_state() :
                                return
                            if x == y - 2 and y > 2 :
                                bot.send_message(chat_id=chat_id, text='20 seconds till end of judgement.')
                            time.sleep(10)
                        
                        bot.send_message(chat_id, 'Judgement has ended.')

                        doc = chat_ref.document(str(chat_id)).get()
                        chat.from_dict(doc.to_dict())

                        #If a defendant is guilty
                        if len(chat.guilty) > len(chat.innocent) :
                            if defendant_id in chat.town :
                                chat.town.remove(defendant_id)
                            else :
                                chat.mafia.remove(defendant_id)
                            
                            chat.alive.remove(defendant_id)
                            chat.graveyard.append(defendant_id)
                            defendant_role_number = chat.players[str(defendant_id)]
                            defendant_role = roles_dict.get(defendant_role_number)
                            chat.deathless_phases = 0
                            bot.send_message(chat_id, f'{defendant_name} is voted guilty and is lynched. ' +
                                f' His role is {defendant_role}.')
                        else :
                            chat.deathless_phases += 1
                            bot.send_message(chat_id, f'{defendant_name} is voted innocent and is spared.')
                    
                        chat_ref.document(str(chat_id)).set(chat.to_dict())
                    
                    # no defendant
                    else :
                        chat.deathless_phases += 1
                        chat_ref.document(str(chat_id)).set(chat.to_dict())
                        bot.send_message(chat_id=chat_id, text='No one has been voted up the stand.')

                    mafia_promotion()

                    # checking if a faction has won
                    if check_win_condition(number=2, player_ref=player_ref, chat_ref=chat_ref, chat=chat, role_instance_dict=role_instance_dict, chat_id=chat_id) :
                        doc = chat_ref.document(str(chat_id)).get()
                        chat.from_dict(doc.to_dict())
                        break

                    doc = chat_ref.document(str(chat_id)).get()
                    chat.from_dict(doc.to_dict())
                    
                    if chat.deathless_phases == 6 :
                        break

                    #Night
                    if check_game_state() :
                        return
                    chat.game_state = 3
                    chat_ref.document(str(chat_id)).set(chat.to_dict())
                    bot.send_message(chat_id, f'Night {day} is starting now. Decision time: {night_time} seconds. Use this time to ' +
                    'decide how to use your ability.')

                    #ability usage
                    for x in chat.alive :
                        role_number = chat.players[str(x)]
                        # checking if role of current iteration is mayor
                        if role_number != 1 :
                            # retrieving player instance mapped to current iteration
                            player = Player(0, 0, "")
                            doc = player_ref.document(str(x)).get()
                            player.from_dict(doc.to_dict())
                            # retrieving role instance
                            z = player.role_instance
                            dict1 = json_to_dict(z)
                            instance = role_instance_dict.get(role_number) # getting dummy role instance
                            instance1 = copy.deepcopy(instance)
                            instance1.from_dict(dict1)
                            instance1.ability(bot, chat.alive, chat.graveyard, chat.town, chat.alive, player_ref, chat_ref)
                    
                    y = night_time / 10
                    
                    for x in range(int(y)) :
                        if check_game_state() :
                            return
                        if x == y - 2 and y > 2 :
                            bot.send_message(chat_id=chat_id, text=f'20 seconds till end of Night {day}.')
                        time.sleep(10)

                    bot.send_message(chat_id=chat_id, text=f'Night {day} has ended.')

                    doc = chat_ref.document(str(chat_id)).get()
                    chat.from_dict(doc.to_dict())
                    # Computing combined results of ability usage and updating database...
                    day_message = result_handling(chat_ref=chat_ref, chat_id=chat_id, chat=chat, player_ref=player_ref, bot=bot)

                    doc = chat_ref.document(str(chat_id)).get()
                    chat.from_dict(doc.to_dict())

                    #checking if a faction has won
                    mafia_promotion()

                    check_win_condition(number=1, player_ref=player_ref, chat_ref=chat_ref, chat=chat, role_instance_dict=role_instance_dict, chat_id=chat_id)

                    doc = chat_ref.document(str(chat_id)).get()
                    chat.from_dict(doc.to_dict())

                
                    day += 1

                if day_message != "" :
                    bot.send_message(chat_id=chat_id, text=day_message)
                
                role_reveal_msg = ""
                for k, v in chat.players.items() :
                    role_name = roles_dict.get(v)
                    player = Player(0, 0, "")
                    doc = player_ref.document(k).get()
                    player.from_dict(doc.to_dict())
                    name = player.name
                    role_reveal_msg += f"{name}'s role was {role_name}.\n"

                victory_msg = "The following players have won:\n"
                number_of_winners = 1

                if chat.deathless_phases == 6 :
                    update_stats(3, player_ref, chat_ref, chat, global_doc1, global_doc2)
                    # auto draw
                    if chat.game_state == 0 :
                        bot.send_message(chat_id, 'Game has automatically ended in a draw!')
                    else :
                        bot.send_message(chat_id, "There has been 3 consecutive days and nights without any deaths. The game has ended in a stalemate.")
                    
                else :
                    if len(chat.town) == 1 and len(chat.mafia) == 1 :
                        # when Mafia auto-wins in the scenario where 2 people are left
                        chat.alive.remove(chat.town[0])
                        chat.graveyard.append(chat.town[0])
                        chat.town = []
                        chat_ref.document(str(chat_id)).set(chat.to_dict())
                        chat.game_state = -1
            
                    if len(chat.town) == 0 and len(chat.mafia) == 0 :
                        update_stats(3, player_ref, chat_ref, chat, global_doc1, global_doc2)
                        bot.send_message(chat_id, 'The place has gone eerily silent...\nas no one seems to be alive! Game has ended in a draw!')

                    elif len(chat.town) == 0 :
                        for k in chat.mafia :
                            player = Player(0, 0, "")
                            doc = player_ref.document(str(k)).get()
                            player.from_dict(doc.to_dict())
                            name = player.name
                            victory_msg += f"{number_of_winners}: {name}\n"
                            number_of_winners += 1

                        update_stats(2, player_ref, chat_ref, chat, global_doc1, global_doc2) 
                        if chat.game_state == -1 :
                            # mafia auto won      
                            bot.send_message(chat_id, 'The game has ended in an automatic win for the Mafia. Congratulations to the Mafia for winning this game.')
                        else :
                            bot.send_message(chat_id, 'Game has ended. Congratulations to the Mafia for winning this game.')
                        
                        bot.send_message(chat_id, victory_msg)                    
                        number_of_winners = 1 # reset back to 1 

                    else :
                        for k in chat.town :
                            player = Player(0, 0, "")
                            doc = player_ref.document(str(k)).get()
                            player.from_dict(doc.to_dict())
                            name = player.name
                            victory_msg += f"{number_of_winners}: {name}\n"
                            number_of_winners += 1

                        update_stats(1, player_ref, chat_ref, chat, global_doc1, global_doc2)
                        bot.send_message(chat_id, 'Game has ended. Congratulations to the Town for winning this game.')
                        bot.send_message(chat_id, victory_msg)     
                        number_of_winners = 1

                chat = Chat()
                chat_ref.document(str(chat_id)).set(chat.to_dict())
                bot.send_message(chat_id, role_reveal_msg)
                bot.send_message(chat_id, 'Use /start to start a new game.')

        else :
            update.message.reply_text('An active game is ongoing now!')


def judge_callback(update:Update, _: CallbackContext) -> None :
    reply = InlineKeyboardMarkup([[InlineKeyboardButton(text='You have successfully voted.', callback_data='1')]])
    update.callback_query.edit_message_reply_markup(reply_markup=reply)
    choice = update.callback_query.data
    user = update.effective_user
    doc1 = player_ref.document(str(user.id)).get()
    player = Player(0, 0, "")
    player.from_dict(doc1.to_dict())
    chat_id = player.chat_id
    current_chat_ref = chat_ref.document(str(chat_id))
    doc = current_chat_ref.get()
    chat = Chat()
    chat.from_dict(doc.to_dict())
    number = ord(choice[10]) - 48
    #if user voted innocent
    if number == 1 :
        if chat.players[str(user.id)] == 1 :
            instance = Mayor(0)
            instance.from_dict(json_to_dict(player.role_instance))
            if instance.votes == 3 :
                current_chat_ref.update({"innocent": firestore.ArrayUnion([-1])})
                current_chat_ref.update({"innocent": firestore.ArrayUnion([-2])})
            current_chat_ref.update({"innocent": firestore.ArrayUnion([user.id])})
        else :
            current_chat_ref.update({"innocent": firestore.ArrayUnion([user.id])})
    #if user voted guilty
    elif number == 2 :
        if chat.players[str(user.id)] == 1 :
            instance = Mayor(0)
            instance.from_dict(json_to_dict(player.role_instance))
            if instance.votes == 3 :
                current_chat_ref.update({"guilty": firestore.ArrayUnion([-1])})
                current_chat_ref.update({"guilty": firestore.ArrayUnion([-2])})
            current_chat_ref.update({"guilty": firestore.ArrayUnion([user.id])})
        else :
            current_chat_ref.update({"guilty": firestore.ArrayUnion([user.id])})

def vote_handling(update: Update, context) -> None :
    answer = update.poll_answer
    answered_poll = context.bot_data[answer.poll_id]
    selected_options = answer.option_ids
    user_id = answer.user.id
    doc1 = player_ref.document(str(user_id)).get()
    player = Player(0, 0, "")
    player.from_dict(doc1.to_dict())
    chat_id = player.chat_id
    doc = chat_ref.document(str(chat_id)).get()
    chat = Chat()
    chat.from_dict(doc.to_dict())
    current_chat_ref = chat_ref.document(str(chat_id))
    #  only process votes by alive players
    if user_id in chat.alive :
        if len(selected_options) == 0 : # retract vote update
            s = "voting." + str(user_id)
            current_chat_ref.update({s : -1})
        else :
            #checking if user voted for himself
            if selected_options[0] != chat.alive.index(user_id) :
                selected_id = chat.alive[selected_options[0]]
                s = str(user_id)
                #checking if user is mayor and if he used his ability
                if chat.players[str(user_id)] == 1 :
                    instance = Mayor(0)
                    instance.from_dict(json_to_dict(player.role_instance))
                    if instance.votes == 3 :
                        player.last_vote_count = 3
                        current_chat_ref.set({"voting": {s: selected_id}}, merge=True)
                    else :
                        player.last_vote_count = 1
                        current_chat_ref.set({"voting": {s: selected_id}}, merge=True)
                    player_ref.document(str(user_id)).set(player.to_dict())
                else :
                    current_chat_ref.set({"voting": {s: selected_id}}, merge=True)
                #checking if vote threshold has been breached
                doc = chat_ref.document(str(chat_id)).get()
                chat.from_dict(doc.to_dict())
                vote_list = []
                for x in chat.voting.keys() :
                    if chat.voting[x] != -1 :
                        if chat.players[x] == 1 :
                            doc2 = player_ref.document(x).get()
                            player1 = Player(0, 0, "")
                            player1.from_dict(doc2.to_dict())
                            if player1.last_vote_count == 3 :
                                vote_list += 3 * [chat.voting[x]]
                        else :
                            vote_list.append(chat.voting[x])
                mode = statistics.mode(vote_list)
                count = vote_list.count(mode)
                if count > math.floor(len(chat.alive)/2) :
                    chat.defendant = mode
                    chat_ref.document(str(chat_id)).set(chat.to_dict())
                    context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
            
def ability_callback(update: Update, _: CallbackContext) -> None :
    choice = update.callback_query.data
    user = update.effective_user
    doc1 = player_ref.document(str(user.id)).get()
    player = Player(0, 0, "")
    player.from_dict(doc1.to_dict())
    chat_id = player.chat_id
    doc = chat_ref.document(str(chat_id)).get()
    chat = Chat()
    chat.from_dict(doc.to_dict())
    current_chat_ref = chat_ref.document(str(chat_id))
    target = choice[8:]
    a = [int(s) for s in target.split() if s.isdigit()]
    s = str(user.id)
    #Mayor ability handling
    if chat.players[str(user.id)] == 1 :
        if chat.game_state > 2 and chat.game_state % 2 == 1:
            reply = InlineKeyboardMarkup([[InlineKeyboardButton(text='You cannot use your ability at night.', callback_data='nothing')]])
            update.callback_query.edit_message_reply_markup(reply_markup=reply)
        else :
            instance = Mayor(0)
            instance.from_dict(json_to_dict(player.role_instance))
            if instance.votes == 3 :
                reply = InlineKeyboardMarkup([[InlineKeyboardButton(text='You have already used your ability', callback_data='nothing')]])
                update.callback_query.edit_message_reply_markup(reply_markup=reply)
            else :
                reply = InlineKeyboardMarkup([[InlineKeyboardButton(text='You have successfully used your ability', callback_data='nothing')]])
                update.callback_query.edit_message_reply_markup(reply_markup=reply)
                instance.votes = 3
                player.role_instance = str(instance)
                player_ref.document(str(user.id)).set(player.to_dict())
                bot.send_message(chat_id=chat_id, text=f'{player.name} has revealed themself as the Mayor. They now have triple the ' +
                    'voting power.')
    #transporter handling
    elif chat.players[str(user.id)] == 3 :
        if chat.ability_targets.get(str(user.id)) is None : # nothing there yet, update is bringing the 1st target
            reply_markup = Transporter.ability_part2(alive_list=chat.alive, first_choice=a[0], player_ref=player_ref)
            update.callback_query.edit_message_text(text='You have successfully chosen your first target. Please choose your second target.')
            update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
            translist = []
            translist.append(a[0])
            current_chat_ref.set({"ability_targets": {s: translist}}, merge=True)
        else : # update is bringing the 2nd target
            translist = chat.ability_targets.get(str(user.id))
            reply = InlineKeyboardMarkup([[InlineKeyboardButton(text='You have successfully used your ability', callback_data='nothing')]])
            update.callback_query.edit_message_reply_markup(reply_markup=reply)   
            translist.append(a[0])
            t = "ability_targets." + str(user.id)
            current_chat_ref.update({t : firestore.ArrayUnion([a[0]])})
    #Ability handling for rest of roles
    else :
        reply = InlineKeyboardMarkup([[InlineKeyboardButton(text='You have successfully used your ability', callback_data='nothing')]])
        update.callback_query.edit_message_reply_markup(reply_markup=reply)
        current_chat_ref.set({"ability_targets": {s: a[0]}}, merge=True)
        role_number = chat.players[str(user.id)]
        instance = role_instance_dict.get(role_number)
        instance1 = copy.deepcopy(instance)
        instance1.from_dict(json_to_dict(player.role_instance))
        instance1.update_attribute(player_ref=player_ref, player=player, target=a[0])


def do_nothing(update: Update, _: CallbackContext) -> None :
    pass

def stats(update: Update, _: CallbackContext) -> None :
    user_id = update.effective_user.id
    player = Player(0, 0, "")
    player_doc = player_ref.document(str(user_id)).get()
    if not player_doc.exists :
        update.message.reply_text(text="You haven't played any games yet! Play one to start seeing your player stats.")
    player.from_dict(player_doc.to_dict())
    msg = player.show_stats()
    msg += " \n"
    msg += "Use /global_stats to view stats of games across all chat groups."
    update.message.reply_text(text=msg)

def global_stats(update: Update, _: CallbackContext) -> None :
    chat_id = update.effective_chat.id
    stats_msg = ""
    global_stats_dict = global_doc1.get().to_dict()
    if global_stats_dict["total number of games"] == 0 :
        stats_msg += "There have been no recorded games with fewer than 8 players so far.\n"
    else :
        stats_msg += "*For games with fewer than 8 players:*  \n"
        town_win_percentage = global_stats_dict["town win rate"] * 100
        town_win_percentage = round(town_win_percentage, 2)
        stats_msg += f'Town win percentage: {town_win_percentage}% \n'
        mafia_win_percentage = global_stats_dict["mafia win rate"] * 100
        mafia_win_percentage = round(mafia_win_percentage, 2)
        stats_msg += f'Mafia win percentage: {mafia_win_percentage}% \n'
        draw_percentage = global_stats_dict["draw rate"] * 100
        draw_percentage = round(draw_percentage, 2)
        stats_msg += f'Draw percentage: {draw_percentage}% \n'
    stats_msg += " \n"
    
    global_stats_dict = global_doc2.get().to_dict()
    if global_stats_dict["total number of games"] == 0 :
        stats_msg += "There have been no recorded games with more than 8 players so far.\n"
    else :
        stats_msg += "*For games with more than 8 players:* \n"
        town_win_percentage = global_stats_dict["town win rate"] * 100
        town_win_percentage = round(town_win_percentage, 2)
        stats_msg += f'Town win percentage: {town_win_percentage}% \n'
        mafia_win_percentage = global_stats_dict["mafia win rate"] * 100
        mafia_win_percentage = round(mafia_win_percentage, 2)
        stats_msg += f'Mafia win percentage: {mafia_win_percentage}% \n'
        draw_percentage = global_stats_dict["draw rate"] * 100
        draw_percentage = round(draw_percentage, 2)
        stats_msg += f'Draw percentage: {draw_percentage}% \n'

    bot.send_message(chat_id=chat_id, text=stats_msg, parse_mode=telegram.ParseMode.MARKDOWN)

def help(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(text='1. Use /start to start the game when everyone (minimum: 4 maximum: 15) that' + 
        ' will be playing has joined the game.\n2. Use /join to indicate that you are going to play the game.\n' +
        '3. Use /roles for a list of roles and related information.\n' +
        '4. Use /rules to know more about the general game rules and proceedings.\n'
        '5. Use /alive for a list of alive players during a game.\n' +
        '6. Use /graveyard for a list of players who died and their respective roles.\n' +
        '7. Use /stop to stop an ongoing game.')

def rules(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    explanation_text = "*General Game Rules and Proceedings* \n"
    explanation_text += " \n"
    explanation_text += "The game runs in Day-Night cycles. \n"
    explanation_text += "Each day has a *discussion* phase, a *voting* phase and a *judgement* phase, except for Day 1 which only has a discussion phase. \n"
    explanation_text += "Players can discuss during the discussion phase. \n"
    explanation_text += "Players can vote for the person they are suspicious of in a non-anonymous poll. \n"
    explanation_text += "If a person gets enough votes (number of players/2 rounded down, plus 1), they will get voted up the stand"\
    " and the judgement phase will kick in. \n"
    explanation_text += "During the judgement phase, the person on the stand will have time to defend themself, "\
    "before every alive player votes for his fate privately with the bot. \n"
    explanation_text += "Based on the votes, the person will either be lynched or spared."
    bot.send_message(chat_id=chat_id, text=explanation_text, parse_mode=telegram.ParseMode.MARKDOWN)
    explanation_text = ""
    explanation_text = "During each *night*, players will use their abilities. \n"
    explanation_text += "However, the Vigilante cannot shoot on Night 1. \n"
    explanation_text += "Also, the Mafia cannot kill on Night 1 if there are fewer than 8 players. \n"
    explanation_text += "After each night, the results are tabulated and if there are any deaths, "\
    "they will be announced the next day."
    bot.send_message(chat_id=chat_id, text=explanation_text, parse_mode=telegram.ParseMode.MARKDOWN)

def roles(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(text='1. /roles_mayor Maximum of mayor in a game: 1' +
        '\n2. /roles_escort Maximum number of Escorts in a game: 3' +
        '\n3. /roles_transporter Maximum number of Transporters in a game: 2' +
        '\n4. /roles_retributionist Maximum number of Retributionists in a game: 2' +
        '\n5. /roles_vigilante Maximum number of Vigilantes in a game: 2' +
        '\n6. /roles_veteran Maximum number of Veterans in a game: 2' +
        '\n7. /roles_bodyguard Maximum number of Bodyguards in a game: 3' +
        '\n8. /roles_doctor Maximum number of Doctors in a game: 3' +
        '\n9. /roles_investigator Maximum number of Investigatorss in a game: 3' +
        '\n10. /roles_sheriff Maximum number of Sheriffs in a game: 3' +
        '\n11. /roles_lookout Maximum number of Lookouts in a game: 3' +
        '\n12. /roles_godfather Maximum number of Godfather in a game: 1' +
        '\n13. /roles_mafioso Maximum number of Mafioso in a game: 1' +
        '\n14. /roles_consort Maximum number of Consorts in a game: 3' +
        '\n15. /roles_consigliere Maximum number of Consigliere in a game: 1' +
        '\n16. /roles_janitor Maximum number of Janitors in a game: 2' +
        '\n17. /roles_framer Maximum number of Framers in a game: 3')

def settings(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id == user_id :
        bot.send_message(chat_id=chat_id, text='Invalid command. Please edit the game settings in a group chat.')
    else :
        chat_settings = Settings()
        settings_doc = setting_ref.document(str(chat_id)).get()
        chat_settings.from_dict(settings_doc.to_dict())
        if chat_settings.check_default() :
            settings_msg = "The current settings are the default durations of each phase: \n"
        else :
            settings_msg = "Current settings are: \n"
        settings_msg += "Day: \n"
        settings_msg += f'Discussion: {chat_settings.discussion}s   Use /settings_discussion to edit the duration.\n'
        settings_msg += f'Voting: {chat_settings.voting}s   Use /settings_voting to edit the duration.\n'
        settings_msg += f'Defence: {chat_settings.defence}s  Use /settings_defence to edit the duration.\n'
        settings_msg += f'Judgement: {chat_settings.judgement}s    Use /settings_judgement to edit the duration.\n'
        settings_msg += "Night: \n"
        settings_msg += f'Night: {chat_settings.night}s Use /settings_night to edit the duration.\n'
        update.message.reply_text(settings_msg)
        settings_msg = ""
        settings_msg += "To change the duration of any of the above phases, type /settings underscore phasename, followed by a space"\
        " and then the new duration in seconds. E.g. /settings_night 60 \n"
        settings_msg += "Do note that for each phase, there is a lower limit of 10 seconds and upper limit of 10 seconds \n"
        settings_msg += "Duration given must be in multiples of ten. \n"
        settings_msg += "\n"
        settings_msg += "Use /reset_settings to return to default durations of the phases."
        update.message.reply_text(settings_msg)

def change_settings(chat_id: int, user_id: int, msg: str, phase: str) -> None:
    input = msg.split('/settings_' + phase + ' ')
    if len(input) == 1 :
        bot.send_message(chat_id=chat_id, text='Please type the new duration of the ' + phase + ' phase as well when using the command.')
    elif len(input) == 2 :
        a = input[1]
        if len(a.split()) == 1 and a.split()[0].isdigit() :
            b = [int(s) for s in a.split() if s.isdigit()]
            new_duration = b[0]
            chat = Chat()
            chat_doc = chat_ref.document(str(chat_id)).get()
            chat.from_dict(chat_doc.to_dict())
            if chat_id == user_id :
                bot.send_message(chat_id=chat_id, text='Invalid command. Please edit the game settings in a group chat.')
            else :
                if not setting_ref.document(str(chat_id)).get().exists :
                    setting_ref.document(str(chat_id)).set(Settings().to_dict())
                if chat.game_state > 1 :
                        bot.send_message(chat_id=chat_id, text='Settings cannot be changed in the middle of a game!')
                else :
                    if new_duration < 10 or new_duration > 100 or new_duration % 10 != 0:
                        bot.send_message(chat_id=chat_id, text='Invalid input. Please choose a duration between 10s and 100s inclusive that is of a multiple of 10.')
                    else :
                        setting_doc = setting_ref.document(str(chat_id))
                        setting_doc.update({phase : new_duration})
                        bot.send_message(chat_id=chat_id, text="Duration of " + phase + f" has been successfully changed to {new_duration} seconds.")
        else :
             bot.send_message(chat_id=chat_id, text='Invalid input. Please type /settings_' + phase + ' followed by a space and then the new duration in seconds.')
    else :
        bot.send_message(chat_id=chat_id, text='Invalid input. Please type /settings_' + phase + ' followed by a space and then the new duration in seconds.')


def settings_discussion(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    msg = update.message.text
    change_settings(chat_id=chat_id, user_id=user_id, msg=msg, phase='discussion')
    
def settings_voting(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    msg = update.message.text
    change_settings(chat_id=chat_id, user_id=user_id, msg=msg, phase='voting')

def settings_judgement(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    msg = update.message.text
    change_settings(chat_id=chat_id, user_id=user_id, msg=msg, phase='judgement')

def settings_defence(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    msg = update.message.text
    change_settings(chat_id=chat_id, user_id=user_id, msg=msg, phase='defence')

def settings_night(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    msg = update.message.text
    change_settings(chat_id=chat_id, user_id=user_id, msg=msg, phase='night')

def reset_settings(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id == user_id :
        bot.send_message(chat_id=chat_id, text='Invalid command. Please edit the game settings in a group chat.')
    else :
        setting_ref.document(str(chat_id)).set(Settings().to_dict())
        bot.send_message(chat_id=chat_id, text='Game settings have been successfully returned to default settings.')


def stop(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    doc = chat_ref.document(str(chat_id)).get()
    if chat_id == user_id :
        update.message.reply_text('Invalid command.')
    elif not doc.exists :
        update.message.reply_text("There is no ongoing game right now!")
    else :
        chat = Chat()
        chat.from_dict(doc.to_dict())
        if chat.game_state == 0 or chat.game_state == 1 :
                update.message.reply_text("There is no ongoing game right now!")
        else :
            if chat.stop_state == 0 :
                chat.stop_state = 1
                chat_ref.document(str(chat_id)).set(chat.to_dict())
                update.message.reply_text('Use /stop again to confirm stoppage of the game. Use /continue to abort stoppage ' +
                        'of game and continue with the current game.')
            else :
                chat.game_state = -1
                chat.stop_state = 0
                chat_ref.document(str(chat_id)).set(chat.to_dict())    
                update.message.reply_text('Game has been stopped. Use /start to start a new game.')

def alive(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    doc = chat_ref.document(str(chat_id)).get()
    if chat_id == user_id :
        update.message.reply_text('Invalid command.')
    elif not doc.exists :
        update.message.reply_text('There is no ongoing game now.')
    else :
        chat = Chat()
        chat.from_dict(doc.to_dict())
        if chat.game_state == 0 or chat.game_state == 1 :
            update.message.reply_text('There is no ongoing game now.')
        else :
            count = 1
            msg = 'People who are still alive are:'
            for x in chat.alive :
                player = Player(0, 0, "")
                doc = player_ref.document(str(x)).get()
                player.from_dict(doc.to_dict())
                name = player.name
                msg += f'\n{count}. {name}'
                count += 1
            update.message.reply_text(msg)

def graveyard(update: Update, _: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    doc = chat_ref.document(str(chat_id)).get()
    if chat_id == user_id :
        update.message.reply_text('Invalid command.')
    elif not doc.exists :
        update.message.reply_text('There is no ongoing game now.')
    else :
        chat = Chat()
        chat.from_dict(doc.to_dict())
        if chat.game_state == 0 or chat.game_state == 1:
            update.message.reply_text('There is no ongoing game now.')
        else :
            if len(chat.graveyard) == 0 :
                update.message.reply_text("There's no one in the graveyard...yet")
            else :
                count = 1
                msg = 'People in the graveyard are:'
                for x in chat.graveyard :
                    player = Player(0, 0, "")
                    doc = player_ref.document(str(x)).get()
                    player.from_dict(doc.to_dict())
                    name = player.name
                    role = roles_dict.get(chat.players[str(x)])
                    msg += f'\n{count}. {name} Role: {role}'
                    count += 1      
                update.message.reply_text(msg)  

def roles_mayor(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Mayor.info())

def roles_escort(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Escort.info())

def roles_transporter(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Transporter.info())

def roles_retributionist(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Retributionist.info())

def roles_vigilante(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Vigilante.info())

def roles_veteran(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Veteran.info())

def roles_bodyguard(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Bodyguard.info())

def roles_doctor(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Doctor.info())

def roles_investigator(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Investigator.info())

def roles_sheriff(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Sheriff.info())

def roles_lookout(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Lookout.info())

def roles_godfather(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Godfather.info())

def roles_mafioso(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Mafioso.info())

def roles_consort(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Consort.info())

def roles_consigliere(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Consigliere.info())

def roles_janitor(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Janitor.info())

def roles_framer(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(Framer.info())


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler(command="start", callback=start, run_async=True))
    dispatcher.add_handler(CommandHandler(command="join", callback=join, run_async=True))
    dispatcher.add_handler(CommandHandler(command="stop", callback=stop, run_async=True))
    dispatcher.add_handler(CommandHandler(command="help", callback=help, run_async=True))
    dispatcher.add_handler(CommandHandler(command="rules", callback=rules, run_async=True))

    dispatcher.add_handler(CommandHandler(command="settings", callback=settings, run_async=True))
    dispatcher.add_handler(CommandHandler(command="settings_discussion", callback=settings_discussion, run_async=True))
    dispatcher.add_handler(CommandHandler(command="settings_voting", callback=settings_voting, run_async=True))
    dispatcher.add_handler(CommandHandler(command="settings_defence", callback=settings_defence, run_async=True))
    dispatcher.add_handler(CommandHandler(command="settings_judgement", callback=settings_judgement, run_async=True))
    dispatcher.add_handler(CommandHandler(command="settings_night", callback=settings_night, run_async=True))
    dispatcher.add_handler(CommandHandler(command="reset_settings", callback=reset_settings, run_async=True))
    
    dispatcher.add_handler(CommandHandler(command="alive", callback=alive, run_async=True))
    dispatcher.add_handler(CommandHandler(command="graveyard", callback=graveyard, run_async=True))

    dispatcher.add_handler(CommandHandler(command="stats", callback=stats, run_async=True))
    dispatcher.add_handler(CommandHandler(command="global_stats", callback=global_stats, run_async=True))

    dispatcher.add_handler(CommandHandler(command="roles", callback=roles, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_mayor", callback=roles_mayor, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_escort", callback=roles_escort, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_transporter", callback=roles_transporter, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_retributionist", callback=roles_retributionist, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_vigilante", callback=roles_vigilante, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_veteran", callback=roles_veteran, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_bodyguard", callback=roles_bodyguard, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_doctor", callback=roles_doctor, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_investigator", callback=roles_investigator, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_sheriff", callback=roles_sheriff, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_lookout", callback=roles_lookout, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_godfather", callback=roles_godfather, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_mafioso", callback=roles_mafioso, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_consort", callback=roles_consort, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_consigliere", callback=roles_consigliere, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_janitor", callback=roles_janitor, run_async=True))
    dispatcher.add_handler(CommandHandler(command="roles_framer", callback=roles_framer, run_async=True))

    dispatcher.add_handler(CallbackQueryHandler(callback=judge_callback, pattern='Judgement', run_async=True))
    dispatcher.add_handler(CallbackQueryHandler(callback=ability_callback, pattern='Ability', run_async=True))
    dispatcher.add_handler(CallbackQueryHandler(callback=do_nothing, pattern='nothing', run_async=True))

    dispatcher.add_handler(PollAnswerHandler(callback=vote_handling, run_async=True))

    # on non command i.e message - echo the message on Telegram
    
    # Start the Bot
    #updater.start_webhook(listen="0.0.0.0",
                          #port=PORT,
                          #url_path=token,
                          #webhook_url="https://secure-anchorage-25754.herokuapp.com/" + token)
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
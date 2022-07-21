from chat import Chat
from player import Player
import copy
import json

def json_to_dict(x) -> dict:
    x = x.replace("\'", "\"")
    x = x.replace('"is_bot": False', '"is_bot": "False"') # replace boolean in json with string
    x = x.replace('"is_bot": True', '"is_bot": "True"')
    return json.loads(x)

# 1 for start of day check, 2 for end of day check
def check_win_condition(number: int, player_ref, chat_ref, chat: Chat, role_instance_dict: dict, chat_id: int) -> bool :
    win_condition = False
    if len(chat.town) == 0 or len(chat.mafia) == 0 :
        win_condition = True
    # check auto-win conditions when there are only 2 players from different factions alive
    elif len(chat.town) == 1 and len(chat.mafia) == 1 :
        town_id = chat.town[0]
        mafia_id = chat.mafia[0]
        town_role_no = chat.players[str(town_id)]["role"]
        mafia_role_no = chat.players[str(mafia_id)]["role"]
        # mafia and other town roles
        if town_role_no > 6 :
            win_condition = True # mafia wins
        # day check: mafia and mayor
        elif town_role_no == 1 :
            if number == 2 :
                win_condition = True
        # escort
        elif town_role_no == 2 :
            # game ends up in a draw
            chat.deathless_phases = 6
            win_condition = True
        # transporter and godfather
        elif town_role_no == 3 :
            if mafia_role_no == 12 :
                chat.deathless_phases = 6
                win_condition = True
        else :
            dummy_instance = role_instance_dict.get(town_role_no)
            town_player_role_instance = copy.deepcopy(dummy_instance)
            town_player_role_instance.from_dict(json_to_dict(chat.players[str(town_id)]["instance"]))
            # mafia and vigilante 
            if town_role_no == 5 :
                # if last mafia standing is godfather
                if mafia_role_no == 12 :
                    win_condition = True
                # if last mafia standing is mafioso
                else :
                    if town_player_role_instance.bullets == 0 :
                        win_condition = True
            # mafia and retributionist
            elif town_role_no == 4 :
                if town_player_role_instance.revive == 0 :
                    win_condition = True
            # mafia and veteran
            elif town_role_no == 6 :
                if town_player_role_instance.alerts == 0 :
                    win_condition = True
    if win_condition :
        chat.game_state = 0
        chat_ref.document(str(chat_id)).set(chat.to_dict())
        return True
    return False
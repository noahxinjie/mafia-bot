from chat import Chat
from player import Player
import investigative_results
import copy
import json

def json_to_dict(json_input) -> dict:
    json_input = json_input.replace("\'", "\"")
    json_input = json_input.replace('"is_bot": False', '"is_bot": "False"') # replace boolean in json with string
    json_input = json_input.replace('"is_bot": True', '"is_bot": "True"')
    return json.loads(json_input)

roles_dict = {1:'Mayor', 2:'Escort', 3:'Transporter', 4:'Retributionist', 5:'Vigilante', 6:'Veteran', 7:'Bodyguard', 8:'Doctor',
    9:'Investigator', 10:'Sheriff', 11:'Lookout', 12:'Godfather', 13:'Mafioso', 14:'Consort', 15:'Consigliere', 
        16:'Janitor', 17:'Framer'}


def result_handling(chat_ref, chat_id, chat: Chat, player_ref, bot) -> str :
    # computing combined results of ability usage and updating database...
    # Priority One
    # transporter
    transporter_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 3}
    if len(transporter_dict) != 0 :
        for transporter, translist in transporter_dict.items() :
            if len(translist) == 2 :
                first_target = translist[0]
                second_target = translist[1]
                if first_target in chat.ability_targets.values() or second_target in chat.ability_targets.values():
                    for k, v in chat.ability_targets.items() :
                        if v == first_target :
                            chat.ability_targets[k] = "placeholder one"
                        if v == second_target :
                            chat.ability_targets[k] = "placeholder two"
                    # carrying out swapping
                    for k, v in chat.ability_targets.items() :
                        if v == "placeholder one" :
                            chat.ability_targets[k] = second_target
                        if v == "placeholder two" :
                            chat.ability_targets[k] = first_target
                bot.send_message(chat_id=first_target, text="You have been transported to another location!")
                bot.send_message(chat_id=second_target, text="You have been transported to another location!")
            
    # escort consort
    escort_consort_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 2 or chat.players[k]["role"] == 14}
    if len(escort_consort_dict) != 0 :
        for k, v in escort_consort_dict.items() :
            if chat.players[str(v)]["role"] == 2 or chat.players[str(v)]["role"] == 3 or chat.players[str(v)]["role"] == 14 :
                bot.send_message(chat_id=v, text='Someone tried to roleblock you but you are immune!')
            else :
                bot.send_message(chat_id=v, text='You are roleblocked!')
                del chat.ability_targets[str(v)]

    # Priority Two                    
    # framer
    framer_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 17}
    chat.framed = []
    if len(framer_dict) != 0 :
        for k, v in framer_dict.items() :
            chat.framed.append(v)                        
    
    # Priority Three
    # investigative roles
    investigative_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 9 or chat.players[k]["role"] == 10 or chat.players[k]["role"] == 15}
    if len(investigative_dict) != 0 :
        for k, v in investigative_dict.items() :
            investigative_id = [int(s) for s in k.split() if s.isdigit()][0]
            # investigator
            if chat.players[k]["role"] == 9:
                if v in chat.framed :
                    bot.send_message(chat_id=a[0], text="Your target deals with evidence. They must be a Sheriff or a Framer.")
                else :
                    number = chat.players[str(v)]["role"]
                    for k, v in investigative_results.invest_results.items() :
                        if number in v :
                            bot.send_message(chat_id=investigative_id, text=k)
            # sheriff
            elif chat.players[k]["role"] == 10:
                if v in chat.framed :
                    bot.send_message(chat_id=investigative_id, text="Your target seems suspicious!")
                else :
                    number = chat.players[str(v)]["role"]
                    bot.send_message(chat_id=investigative_id, text=investigative_results.sheriff_results[number])
            # consigliere    
            else :
                if v in chat.framed :
                    bot.send_message(chat_id=investigative_id, text="Your target tampers with evidence. They must be a Framer.")
                else :
                    number = chat.players[str(v)]["role"]
                    bot.send_message(chat_id=investigative_id, text=investigative_results.consig_results[number])
    
    # Priority Four
    # killing
    chat.killing_dict = {}
    chat.killing_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 12 or chat.players[k]["role"] == 13}
    # Godfather's decision displaces Mafioso's decision if both exist
    gf_kills = False
    mafioso_kills = False
    godfather = ""
    mafioso = ""
    
    for x in chat.players.keys() :
        if chat.players[x]["role"] == 12 :
            if x in chat.killing_dict.keys() :
                gf_kills = True 
                godfather = x
        if chat.players[x]["role"] == 13 :
            if x in chat.killing_dict.keys() :
                mafioso_kills = True
                mafioso = x
    
    if gf_kills and mafioso_kills :
        target = chat.killing_dict[godfather]
        del chat.killing_dict[godfather]
        gf_kills = False
        chat.killing_dict[mafioso] = target
        mafioso_id = [int(s) for s in mafioso.split() if s.isdigit()][0]
        bot.send_message(chat_id=mafioso_id, text="You have attacked the target the Godfather ordered you to!")
    
    dummy_killing = copy.deepcopy(chat.killing_dict)
    for attacker, attacked in dummy_killing.items() :
        role_instance = chat.players[str(attacked)]["instance"]
        instance1 = json_to_dict(role_instance)
        if instance1["immunity"] > 0 :
            del chat.killing_dict[attacker]
            bot.send_message(chat_id=attacked, text="Someone tried to attack you but you are immune!")  
            attacker_id = [int(s) for s in attacker.split() if s.isdigit()][0]                
            bot.send_message(chat_id=attacker_id, text="You tried to attack your target but it failed!")   

    # vigilante 
    for k in chat.ability_targets.keys() :
        if chat.players[k]["role"] == 5 :
            vig_id = [int(s) for s in k.split() if s.isdigit()][0]
            target_id = chat.ability_targets[k]
            role_instance = chat.players[str(target_id)]["instance"]
            instance1 = json_to_dict(role_instance)
            if instance1["immunity"] > 0 :
                bot.send_message(chat_id=vig_id, text="You tried to attack your target but it failed!")
                bot.send_message(chat_id=target_id, text="Someone tried to attack you but you are immune!")  
            else :
                chat.killing_dict[str(vig_id)] = target_id # target is shot
                    
    # Priority Five
    # janitor
    chat.cleaned = []
    janitor_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 16}
    if len(janitor_dict) != 0 :
        for janitor, target in janitor_dict.items() :
            if gf_kills :
                if target == chat.killing_dict[godfather] :
                    chat.cleaned.append(target)
                    break
            elif mafioso_kills :
                if target == chat.killing_dict[mafioso] :
                    chat.cleaned.append(target)
                    break

    # Priority Six
    # lookout
    lookout_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 11}
    if len(lookout_dict) != 0 :
        for k, v in lookout_dict.items() :
            visited_list = []
            k_id = [int(s) for s in k.split() if s.isdigit()][0]
            targeted = {a:b for (a, b) in chat.ability_targets.items() if v == b}
            for x, y in targeted.items() :
                if x != k : 
                    name = chat.players[x]["name"]
                    visited_list.append(name)
            msg = 'People who visited your target last night are:'
            count = 1
            for a in visited_list :
                msg += f'\n{count}. {a}'
                count += 1

            if len(visited_list) != 0 :
                bot.send_message(chat_id=k_id, text=msg)
            else :
                bot.send_message(chat_id=k_id, text="No one visited your target last night.")
    
    # Priority Seven
    # veteran v = 1 means alert v = 2 means no alert
    veteran_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 6}
    if len(veteran_dict) != 0 :
        for k, v in veteran_dict.items() :
            if v == 1 :
                k_id = [int(s) for s in k.split() if s.isdigit()][0]
                targeted = {a:b for (a, b) in chat.ability_targets.items() if b == k_id[0]}
                vet_killcount = 0
                for x in targeted.keys() :
                    x_id = [int(s) for s in x.split() if s.isdigit()][0]
                    vet_killcount += 1
                    chat.killing_dict[k] = x_id
            if vet_killcount == 1 :
                bot.send_message(chat_id=k_id, text=f'You shot a person who visited you tonight!')
            elif vet_killcount > 1 :
                bot.send_message(chat_id=k_id, text=f"You shot {vet_killcount} people who visited you tonight!")

    # Priority Eight
    # protective
    protective_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 7 or chat.players[k]["role"] == 8}
    if len(protective_dict) != 0 :
        number_of_bodyguards = 0
        # bodyguard goes first
        dummy_protective = copy.deepcopy(protective_dict)
        for bodyguard, defended in dummy_protective.items() :
            if chat.players[bodyguard]["role"] == 7 :
                number_of_bodyguards += 1
                bodyguard_id = [int(s) for s in bodyguard.split() if s.isdigit()][0]
                count = 0
                if defended in chat.killing_dict.values() : # checking how many times defended was attacked
                    for target in chat.killing_dict.values() :
                        if defended == target :
                            count += 1
                if count > 0 : # defended was attacked
                    if bodyguard_id == defended : # bodyguard self-vested
                        bot.send_message(chat_id=defended, text="Someone tried to attack you but your bulletproof vest protected you!")
                        dummy_killing = copy.deepcopy(chat.killing_dict)
                        for attacker, attacked in dummy_killing.items() :
                            if bodyguard_id == attacked :
                                attacker_id = [int(s) for s in attacker.split() if s.isdigit()][0]
                                bot.send_message(chat_id=attacker_id, text="You tried to attack your target but it failed!")
                                del chat.killing_dict[attacker]
                        del protective_dict[bodyguard]
                    else : # bodyguard managed to protect someone else from dying
                        dummy_killing = copy.deepcopy(chat.killing_dict)
                        for attacker, target in dummy_killing.items() :
                            if defended == target :
                                attacker_id = [int(s) for s in attacker.split() if s.isdigit()][0]
                                if chat.players[str(attacker_id)]["role"] != 6 : # if defended did not die by visiting a vet
                                    chat.killing_dict["B" + str(number_of_bodyguards)] = bodyguard_id # bodyguard dies
                                    chat.killing_dict[bodyguard] = attacker_id # attacker dies
                                    bot.send_message(chat_id=defended, text="Someone tried to attack you but a Bodyguard fought off your attacker!")
                                    del chat.killing_dict[str(attacker_id)] # target is saved once
                                    break # stop immediately after selecting a random attacker to die
                        del protective_dict[bodyguard]   

                else :
                    del protective_dict[bodyguard]   # defended was not attacked
        # doctor goes second
        dummy_protective = copy.deepcopy(protective_dict)
        for doctor, defended in dummy_protective.items() :
            if chat.players[doctor]["role"] == 8 :
                doctor_id = [int(s) for s in doctor.split() if s.isdigit()][0]
                count = 0
                if defended in chat.killing_dict.values() : # checking how many times defended was attacked
                    for target in chat.killing_dict.values() :
                        if defended == target :
                            count += 1
                if count > 0 : # defended was attacked
                    if doctor_id == defended : # doctor self healed
                        bot.send_message(chat_id=defended, text="Someone tried to attack you but you nursed yourself back to health!")
                        dummy_killing = copy.deepcopy(chat.killing_dict)
                        for attacker, defended in dummy_killing.items() :
                            if doctor_id == defended :
                                attacker_id = [int(s) for s in attacker.split() if s.isdigit()][0]
                                bot.send_message(chat_id=attacker_id, text="You tried to attack your target but it failed!")
                                del chat.killing_dict[attacker]
                        del protective_dict[doctor]
                    else : # doctor managed to save someone else from dying
                        dummy_killing = copy.deepcopy(chat.killing_dict)
                        for attacker, target in dummy_killing.items() :
                            if defended == target :
                                bot.send_message(chat_id=doctor_id, text="Someone tried to attack your target but you nursed them back to health!")
                                del chat.killing_dict[attacker] # target is saved

                                # if doctor nurses someone shot by veteran back to health
                                if chat.players[attacker]["role"] == 6 :
                                    bot.send_message(chat_id=target, text="You were shot by the Veteran you visited" +
                                    "but a Doctor nursed you back to health!")
                                # if doctor nurses someone attacked by bodyguard
                                elif chat.players[attacker]["role"] == 7 :
                                    bot.send_message(chat_id=target, text="You were gravely injured by the Bodyguard protecting your target" + 
                                    "but a Doctor nursed you back to health!")
                                # if doctor nurses a dying bodyguard
                                elif attacker[0] == "B" :
                                    bot.send_message(chat_id=target, text="You were gravely injured protecting your target" +
                                    "but a Doctor nursed you back to health!")
                                # if doctor nurses someone attacked by mafia or vigilante
                                else :
                                    attacker_id = [int(s) for s in attacker.split() if s.isdigit()][0]
                                    bot.send_message(chat_id=attacker_id, text="You tried to attack your target but it failed!")
                                    bot.send_message(chat_id=target, text="Someone tried to attack you but a Doctor nursed you back to health!")
                        del protective_dict[doctor]

                else :
                    del protective_dict[doctor]   # defended was not attacked

    # Priority Nine
    # retributionist
    retributionist_dict = {k:v for (k, v) in chat.ability_targets.items() if chat.players[k]["role"] == 4}
    if len(retributionist_dict) != 0 :
        for k, v in retributionist_dict.items() :
            if v in chat.graveyard :
                chat.graveyard.remove(v)
                chat.alive.append(v)
                chat.town.append(v)
                bot.send_message(chat_id=v, text='You have been revived by a Retributionist!')

    # final results handling
    day_msg = "It was a quiet night last night...?"
    msg_count = 1
    if len(chat.killing_dict) != 0 :
        day_msg = "Summary of what happened last night:\n"
        attacked_list = [*chat.killing_dict.values()]
        attacked_list_no_dups = [*dict.fromkeys(attacked_list).keys()]
        for x in attacked_list_no_dups :
            chat.alive.remove(x)
            chat.graveyard.append(x)
            if chat.players[str(x)]["role"] < 12 :
                chat.town.remove(x)
            else :
                chat.mafia.remove(x)

            if attacked_list.count(x) >= 2 :
                day_msg += f"{msg_count}. {attacked_name} was slaughtered last night."
                msg_count += 1
            
            for attacker, attacked in chat.killing_dict.items() :
                if attacked == x :
                    attacked_name = chat.players[str(attacked)]["name"]
                    attacked_role_number = chat.players[str(attacked)]["role"]
                    attacked_role = roles_dict.get(attacked_role_number)
                    if attacker[0] != "B" :
                        # mafia kills
                        if chat.players[attacker]["role"] == 12 or chat.players[attacker]["role"] == 13:
                            # if the most recently cleaned target is the one attacked by mafia last night
                            if len(chat.cleaned) > 0 and chat.cleaned[-1] == attacked :
                                bot.send_message(chat_id=attacked, text="You are killed by a member of the Mafia!")
                                day_msg += f"{msg_count}. {attacked_name} was killed by a member of the Mafia last night. We could not determine his role.\n"
                            else :
                                bot.send_message(chat_id=attacked, text="You are killed by a member of the Mafia!")
                                day_msg += f"{msg_count}. {attacked_name} was killed by a member of the Mafia last night. His role was {attacked_role}.\n"                                
                        
                        # bodyguard kills
                        elif chat.players[attacker]["role"] == 7:
                            bot.send_message(chat_id=attacked, text="You are killed by the Bodyguard protecting your target!")
                            day_msg += f"{msg_count}. {attacked_name} was killed by a Bodyguard last night. His role was {attacked_role}.\n"

                        # vigilante kills
                        elif chat.players[attacker]["role"] == 5 :
                            bot.send_message(chat_id=attacked, text="You are shot by a Vigilante!")    
                            day_msg += f"{msg_count}. {attacked_name} was shot by a Vigilante last night. His role was {attacked_role}.\n"
                            if chat.players[str(attacked)]["role"] < 12 :
                                role_instance = chat.players[attacker]["instance"]
                                role_instance_dict = json_to_dict(role_instance)
                                role_instance_dict["guilt"] += 1
                                chat.players[attacker]["instance"] = json.dumps(role_instance_dict)                  
                        
                        # veteran kills
                        else :
                            bot.send_message(chat_id=attacked, text="You are shot by the Veteran you visited!")
                            day_msg += f"{msg_count}. {attacked_name} was shot by a Veteran last night. His role was {attacked_role}.\n"                        
        
                    # bodyguard killed
                    else :
                        bot.send_message(chat_id=attacked, text="You have died protecting your target!")
                        day_msg += f"{msg_count}. {attacked_name} was killed. He died guarding someone last night. His role was {attacked_role}.\n" 
    
                    msg_count += 1
    
    if msg_count == 1 :
        chat.deathless_phases += 1
    else :
        chat.deathless_phases = 0                        

    chat.ability_targets = {}
    chat.killing_dict = {}                    
    chat_ref.document(str(chat_id)).set(chat.to_dict())
    return day_msg                
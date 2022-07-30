from chat import Chat
from player import Player

# update players' stats
# 1 if town wins 2 if mafia wins 3 if draw
def update_stats(number: int, player_ref, chat_ref, chat, global_doc1, global_doc2) -> None :
    # update player stats
    for current_player in chat.players.keys() :
        current_player_id = [int(s) for s in current_player.split() if s.isdigit()][0]
        player = Player.get_player(id=current_player_id, player_db=player_ref)
        stats = player.stats
        stats["number_of_games_played"] += 1
        roles_percentage_dict = stats["roles_percentage"]
        role_percentage_list = roles_percentage_dict[str(chat.players[current_player]["role"])]
        if chat.players[current_player]["role"] < 12 :
            stats["number_of_games_as_town"] += 1
            # Town wins
            if number == 1 :
                stats["number_of_wins"] += 1
                role_percentage_list[0] += 1
            # Mafia wins
            elif number == 2 :
                stats["number_of_losses"] += 1
            # Draws
            else :
                stats["number_of_draws"] += 1
        else :
            stats["number_of_games_as_mafia"] += 1
            # Mafia wins
            if number == 2 :
                stats["number_of_wins"] += 1
                role_percentage_list[0] += 1
            # Town wins
            elif number == 1 :
                stats["number_of_losses"] += 1
            # Draws
            else :
                stats["number_of_draws"] += 1

        role_percentage_list[1] += 1
        role_percentage_list[2] = (role_percentage_list[0] / role_percentage_list[1]) * 100
                        
        if player.stats["number_of_games_played"] != 0 :
            player.stats["win_percentage"] = (player.stats["number_of_wins"] / player.stats["number_of_games_played"]) * 100
            player.stats["loss_percentage"] = (player.stats["number_of_losses"] / player.stats["number_of_games_played"]) * 100
            player.stats["draw_percentage"] = (player.stats["number_of_draws"] / player.stats["number_of_games_played"]) * 100
                        
        if current_player_id in chat.alive :
            player.stats["survived"] += 1
                        
        player_ref.document(current_player).set(player.to_dict())
                    
    # update global stats
    number_of_players = len(chat.players)
    if number_of_players < 8 :
        global_stats_dict = global_doc1.get().to_dict()
        global_stats_dict["total number of games"] += 1
        # Town wins
        if number == 1 :
            global_stats_dict["number of town wins"] += 1
        # Mafia wins 
        elif number == 2 :
            global_stats_dict["number of mafia wins"] += 1
        # Draws
        else :
            global_stats_dict["number of draws"] += 1

        global_stats_dict["town win rate"] = global_stats_dict["number of town wins"] / global_stats_dict["total number of games"]
        global_stats_dict["mafia win rate"] = global_stats_dict["number of mafia wins"] / global_stats_dict["total number of games"]
        global_stats_dict["draw rate"] = global_stats_dict["number of draws"] / global_stats_dict["total number of games"]
        global_doc1.set(global_stats_dict)

    else :
        global_stats_dict = global_doc2.get().to_dict()
        global_stats_dict["total number of games"] += 1
        # Town wins
        if number == 1 :
            global_stats_dict["number of town wins"] += 1
        # Mafia wins 
        elif number == 2 :
            global_stats_dict["number of mafia wins"] += 1
        # Draws
        else :
            global_stats_dict["number of draws"] += 1

        global_stats_dict["town win rate"] = global_stats_dict["number of town wins"] / global_stats_dict["total number of games"]
        global_stats_dict["mafia win rate"] = global_stats_dict["number of mafia wins"] / global_stats_dict["total number of games"]
        global_stats_dict["draw rate"] = global_stats_dict["number of draws"] / global_stats_dict["total number of games"]
        global_doc2.set(global_stats_dict)      
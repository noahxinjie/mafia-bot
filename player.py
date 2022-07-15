import random

class Player:
    @staticmethod
    def make_roles_percentage_dict() -> dict :
      list1 = [0, 0, 0] # list1[0] wins list1[1] games list1[2] win percentage
      dict1 = {}
      for x in range(17) :
        dict1[str(x+1)] = list1
      return dict1

    def __init__(self, user_id: int, chat_id: int, name: str) -> None:
        self.user_id = user_id
        self.chat_id = chat_id
        self.name = name
        self.role_instance = ""
        self.last_vote_count = 0
        # player stats attributes
        self.stats = dict({
          "number_of_games_played": 0,
          "number_of_games_as_town": 0,
          "number_of_games_as_mafia": 0,
          "number_of_wins": 0,
          "number_of_losses": 0,
          "number_of_draws": 0,
          "win_percentage": 0.00,
          "loss_percentage": 0.00,
          "draw_percentage": 0.00,
          "survived": 0,
          "roles_percentage": Player.make_roles_percentage_dict()
        })

    def from_dict(self, source):
      self.user_id = source["user id"]
      self.chat_id = source["chat id"]
      self.name = source["name"]
      self.role_instance = source["role instance"]
      self.last_vote_count = source["last vote count"]
      # insert player stats  
      self.stats = source["stats"]
    
    def to_dict(self) -> dict:
      return dict(
        {"user id": self.user_id,
        "chat id": self.chat_id,
        "name": self.name,
        "role instance": self.role_instance,
        "last vote count": self.last_vote_count,
        # insert player stats
        "stats": self.stats
        }
      )

    @staticmethod
    def get_player(id: int, player_db) :
        player = Player(0, 0, "")
        doc = player_db.document(str(id)).get()
        player.from_dict(doc.to_dict())
        return player

    #number == 1 for finding highest and 2 for finding lowest
    def find_lowest_or_highest_winrate(self, number: int) -> int :
      dict1 = self.stats["roles_percentage"]
      list1 = []
      for k, v in dict1.items() :
        list1.append(v[2])
      if number == 1 :
        value = max(list1)
      else :
        value = min(list1)
      items = [*dict1.items()]
      random.shuffle(items)
      for k, v in items :
        if v[2] == value :
          a = [int(s) for s in k.split() if s.isdigit()]
          return a[0]

    roles_dict = {1:'Mayor', 2:'Escort', 3:'Transporter', 4:'Retributionist', 5:'Vigilante', 6:'Veteran', 7:'Bodyguard', 8:'Doctor',
    9:'Investigator', 10:'Sheriff', 11:'Lookout', 12:'Godfather', 13:'Mafioso', 14:'Consort', 15:'Consigliere', 
        16:'Janitor', 17:'Framer'}

    def show_stats(self) -> str:
      stats_msg = ""
      if self.stats["number_of_games_played"] == 0 :
        stats_msg = "You haven't played any games yet! Play one to start seeing your player stats."
      else :
        stats_msg += f'Number of games played: {self.stats["number_of_games_played"]} \n'
        if self.stats["number_of_games_as_town"] == 0 :
          stats_msg += "You have not played any games as a Town member yet.\n"
        else :
          stats_msg += f'Number of games as Town: {self.stats["number_of_games_as_town"]} \n'
        if self.stats["number_of_games_as_mafia"] == 0 :
          stats_msg += "You have not played any games as a Mafia member yet.\n"
        else :
          stats_msg += f'Number of games as Mafia: {self.stats["number_of_games_as_mafia"]} \n'

        stats_msg += f'Number of wins: {self.stats["number_of_wins"]} \n'
        stats_msg += f'Number of losses: {self.stats["number_of_losses"]} \n'
        stats_msg += f'Number of draws: {self.stats["number_of_draws"]} \n'

        win_percentage = round(self.stats["win_percentage"], 2)
        stats_msg += f'Win percentage: {win_percentage}% \n'
        loss_percentage = round(self.stats["loss_percentage"], 2)
        stats_msg += f'Loss percentage: {loss_percentage}% \n'
        draw_percentage = round(self.stats["draw_percentage"], 2)
        stats_msg += f'Draw percentage: {draw_percentage}% \n'

        highest_winrate = self.find_lowest_or_highest_winrate(1)
        highest_winrate_role = Player.roles_dict.get(highest_winrate)
        highest_winrate_list = self.stats["roles_percentage"][str(highest_winrate)]
        winrate = round(highest_winrate_list[2], 2)
        stats_msg += f'Role with highest win percentage: {highest_winrate_role} with {winrate}% \n'

        lowest_winrate = self.find_lowest_or_highest_winrate(2)
        lowest_winrate_role = Player.roles_dict.get(lowest_winrate)
        lowest_winrate_list = self.stats["roles_percentage"][str(lowest_winrate)]
        winrate = round(lowest_winrate_list[2], 2)
        stats_msg += f'Role with lowest win percentage: {lowest_winrate_role} with {winrate}% \n'


        if self.stats["survived"] == 0 :
          stats_msg += "You have not survived all the way to the end of a game before. Better luck next time! \n"
        else :
          stats_msg += f'You have survived to the end of a game {self.stats["survived"]} times. \n'

      return stats_msg

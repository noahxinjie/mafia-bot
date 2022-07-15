class Chat:

  def __init__(self) -> None:
    self.players = {}
    self.ability_targets = {}
    self.killing_dict = {}
    self.voting = {}
    self.innocent = []
    self.guilty = []
    self.alive = []
    self.graveyard = []
    self.town =  []
    self.mafia = []
    self.framed = []
    self.cleaned = []
    self.game_state = 0
    self.stop_state = 0
    self.defendant = -1
    self.deathless_phases = 0

  def from_dict(self, source):
    self.players = source["players"]
    self.ability_targets = source["ability_targets"]
    self.killing_dict = source["killing dict"]
    self.voting = source["voting"]
    self.innocent = source["innocent"]
    self.guilty = source["guilty"]
    self.alive = source["alive"]
    self.graveyard = source["graveyard"]
    self.town = source["town"]
    self.mafia = source["mafia"]
    self.framed = source["framed"]
    self.cleaned = source["cleaned"]
    self.game_state = source["game state"]
    self.stop_state = source["stop state"]
    self.defendant = source["defendant"]
    self.deathless_phases = source["deathless phases"]

  def to_dict(self) -> dict:
    return dict(
      {"players": self.players,
      "ability_targets": self.ability_targets,
      "killing dict": self.killing_dict,
      "voting": self.voting,
      "innocent": self.innocent,
      "guilty": self.guilty,
      "alive": self.alive,
      "graveyard": self.graveyard,
      "town": self.town,
      "mafia": self.mafia,
      "framed": self.framed,
      "cleaned": self.cleaned,
      "game state": self.game_state,
      "stop state": self.stop_state,
      "defendant": self.defendant,
      "deathless phases": self.deathless_phases
    })

  @staticmethod
  def get_chat(id: int, chat_db) :
      chat = Chat()
      doc = chat_db.document(str(id)).get()
      chat.from_dict(doc.to_dict())
      return chat

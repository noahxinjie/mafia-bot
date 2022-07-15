class Settings :

    def __init__(self) -> None:
        self.discussion = 70
        self.voting = 30
        self.defence = 20
        self.judgement = 20
        self.night = 70

    def from_dict(self, source):
        self.discussion = source["discussion"]
        self.voting = source["voting"]
        self.defence = source["defence"]
        self.judgement = source["judgement"]
        self.night = source["night"]

    def to_dict(self) -> dict:
      return dict(
        {"discussion": self.discussion,
        "voting": self.voting,
        "defence": self.defence,
        "judgement": self.judgement,
        "night": self.night
        }
      )

    def check_default(self) -> bool:
        return self.discussion == 70 and self.voting == 30 and self.defence == 20 and self.judgement == 20 and self.night == 70

consig_results = dict({
    1: "Your target is the leader of the town. They must be the Mayor.",
    2: "Your target is a beautiful person working for the town. They must be an Escort.",
    3: "Your target has a space-manipualting device. They must be a Transporter.",
    4: "Your target wields mystical powers that can revive the dead. They must be a Retributionist.",
    5: "Your target will bend the law to enact justice. They must be a Vigilante.",
    6: "Your target is a paranoid war hero. They must be a Veteran.",
    7: "Your target is a trained protector. They must be a Bodyguard.",
    8: "Your target is a professional surgeon. They must be a Doctor.",
    9: "Your target gathers information about people. They must be an Investigator.",
    10: "Your target is a member of the town's police task force. They must be a Sheriff.",
    11: "Your target watches who visits people at night. They must be a Lookout.",
    12: "Your target is the leader of the Mafia. They must be the Godfather.",
    13: "Your target does the Godfather's dirty work. They must be the Mafioso.",
    14: "Your target is a beautiful person working for the Mafia. They must be a Consort.",
    15: "Your target gathers information for the Mafia. They must be the Consigliere. Wait, what just happened?",
    16: "Your target cleans up dead bodies. They must be a Janitor.",
    17: "Your target tampers with evidence. They must be a Framer."
})

sheriff_results = dict({
    1: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    2: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    3: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    4: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    5: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    6: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    7: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    8: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    9: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    10: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    11: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    12: "You cannot find any evidence of wrongdoing. Your target seems innocent.",
    13: "Your target seems suspicious!",
    14: "Your target seems suspicious!",
    15: "Your target seems suspicious!",
    16: "Your target seems suspicious!",
    17: "Your target seems suspicious!"
})

invest_results = dict({
    "Your target is a righteous member of the Town. They must be a Transporter or the Mayor.": [1, 3],
    "Your target is a beautiful person. They must be a Escort or a Consort.": [2, 14],
    "Your target deals with bodies. They must be a Retributionist, a Doctor, or a Janitor.": [4, 8, 16],
    "Your target isn't afraid to resort to violence to settle things. They must be a Vigilante, a Veteran, or the Mafioso.": [5, 6, 13],
    "Your target seems to command respect among townsfolk. He must be a Bodyguard or the Godfather.": [7, 12],
    "Your target likes to gather information about others. He must be a Investigator, a Lookout, or the Consigiliere.": [9, 11, 15],
    "Your target deals with evidence. They must be a Sheriff or a Framer.": [10, 17]
})
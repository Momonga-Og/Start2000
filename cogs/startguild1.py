# startguild1.py
import random

# Configuration
GUILD_ID = 1217700740949348443  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1247706162317758597  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1247728738326679583  # Replace with your alert channel ID

GUILD_EMOJIS_ROLES = {
    "Darkness": {"emoji": "🌑", "role_id": 1244077334668116050},
    "GTO": {"emoji": "🔥", "role_id": 1244077334668116050},
    "Aversion": {"emoji": "💀", "role_id": 1244077334668116050},
    "Bonnebuche": {"emoji": "🍞", "role_id": 1244077334668116050},
    "LMDF": {"emoji": "💪", "role_id": 1244077334668116050},
    "Notorious": {"emoji": "⚡", "role_id": 1244077334668116050},
    "Percophile": {"emoji": "🎶", "role_id": 1244077334668116050},
    "Tilisquad": {"emoji": "👑", "role_id": 1244077334668116050},
}

ALERT_MESSAGES = [
    "🚨 {role} Alerte DEF ! Connectez-vous maintenant !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
]

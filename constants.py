"""
Game constants and configuration
"""

# Offensive systems
OFFENSIVE_SYSTEMS = [
    "Motion Offense",
    "Princeton Offense",
    "Fast Break",
    "Pick and Roll",
    "Isolation",
    "Triangle Offense"
]

# Defensive systems
DEFENSIVE_SYSTEMS = [
    "Man-to-Man",
    "2-3 Zone",
    "1-3-1 Zone",
    "Full Court Press",
    "Pack Line",
    "Match-Up Zone"
]

# Player positions
POSITIONS = ["PG", "SG", "SF", "PF", "C"]

# Attribute names
ATTRIBUTES = ["Shooting", "Defense", "Athleticism", "Basketball IQ", "Rebounding"]

# Season configuration
REGULAR_SEASON_GAMES = 30
CONFERENCE_TOURNAMENT_TEAMS = 8
NCAA_TOURNAMENT_TEAMS = 68
NIT_TOURNAMENT_TEAMS = 32

# Game configuration
GAME_LENGTH_MINUTES = 40
POSSESSIONS_PER_GAME = 70

# Player development
MIN_ATTRIBUTE = 1
MAX_ATTRIBUTE = 10
DEVELOPMENT_RATE = 0.3  # Average improvement per season

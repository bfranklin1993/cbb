"""
Core game models: Player, Team, etc.
"""

import random
from typing import Dict, List
from constants import POSITIONS, ATTRIBUTES, MIN_ATTRIBUTE, MAX_ATTRIBUTE


class Player:
    """Represents a college basketball player"""

    def __init__(self, name: str, position: str, year: int = 1):
        self.name = name
        self.position = position  # PG, SG, SF, PF, C
        self.year = year  # 1=Freshman, 2=Sophomore, 3=Junior, 4=Senior

        # Attributes (1-10 scale)
        self.shooting = random.randint(3, 8)
        self.defense = random.randint(3, 8)
        self.athleticism = random.randint(3, 8)
        self.basketball_iq = random.randint(3, 8)
        self.rebounding = random.randint(3, 8)

        # Season stats
        self.games_played = 0
        self.points = 0
        self.rebounds = 0
        self.assists = 0
        self.steals = 0
        self.blocks = 0

    def overall_rating(self) -> float:
        """Calculate overall player rating"""
        return (self.shooting + self.defense + self.athleticism +
                self.basketball_iq + self.rebounding) / 5

    def get_stats_per_game(self) -> Dict[str, float]:
        """Get per-game statistics"""
        if self.games_played == 0:
            return {"PPG": 0, "RPG": 0, "APG": 0, "SPG": 0, "BPG": 0}

        return {
            "PPG": round(self.points / self.games_played, 1),
            "RPG": round(self.rebounds / self.games_played, 1),
            "APG": round(self.assists / self.games_played, 1),
            "SPG": round(self.steals / self.games_played, 1),
            "BPG": round(self.blocks / self.games_played, 1)
        }

    def develop(self, amount: float = 0.3):
        """Improve player attributes over time"""
        # Younger players develop more
        development_multiplier = (5 - self.year) / 4
        actual_amount = amount * development_multiplier

        # Randomly improve 2-3 attributes
        num_improvements = random.randint(2, 3)
        attributes = ['shooting', 'defense', 'athleticism', 'basketball_iq', 'rebounding']

        for attr in random.sample(attributes, num_improvements):
            current = getattr(self, attr)
            improvement = random.uniform(0, actual_amount)
            new_value = min(MAX_ATTRIBUTE, current + improvement)
            setattr(self, attr, round(new_value, 1))

    def __str__(self):
        return f"{self.name} ({self.position}) - OVR: {self.overall_rating():.1f}"


class Team:
    """Represents a college basketball team"""

    def __init__(self, name: str, conference: str):
        self.name = name
        self.conference = conference
        self.roster: List[Player] = []

        # Systems
        self.offensive_system = "Motion Offense"
        self.defensive_system = "Man-to-Man"

        # Season record
        self.wins = 0
        self.losses = 0
        self.conference_wins = 0
        self.conference_losses = 0

        # Generate initial roster
        self._generate_roster()

    def _generate_roster(self):
        """Generate a random roster of 12 players"""
        first_names = ["James", "Michael", "John", "David", "Chris", "Matt", "Ryan",
                      "Kevin", "Tyler", "Brandon", "Jason", "Josh", "Andrew", "Nick"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                     "Miller", "Davis", "Martinez", "Wilson", "Anderson", "Taylor"]

        positions_needed = ["PG", "PG", "SG", "SG", "SF", "SF", "PF", "PF", "C", "C", "SG", "SF"]

        for i, pos in enumerate(positions_needed):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            year = random.randint(1, 4)
            player = Player(name, pos, year)

            # Make some players better (starters)
            if i < 5:  # Starting 5
                player.shooting += random.randint(0, 2)
                player.defense += random.randint(0, 2)
                player.athleticism += random.randint(0, 2)
                player.basketball_iq += random.randint(0, 2)
                player.rebounding += random.randint(0, 2)

                # Cap at 10
                player.shooting = min(10, player.shooting)
                player.defense = min(10, player.defense)
                player.athleticism = min(10, player.athleticism)
                player.basketball_iq = min(10, player.basketball_iq)
                player.rebounding = min(10, player.rebounding)

            self.roster.append(player)

    def get_team_rating(self) -> float:
        """Get overall team rating based on top 8 players"""
        sorted_players = sorted(self.roster, key=lambda p: p.overall_rating(), reverse=True)
        top_8 = sorted_players[:8]
        return sum(p.overall_rating() for p in top_8) / 8

    def get_starting_five(self) -> List[Player]:
        """Get the 5 best players"""
        return sorted(self.roster, key=lambda p: p.overall_rating(), reverse=True)[:5]

    def win_percentage(self) -> float:
        """Calculate win percentage"""
        total_games = self.wins + self.losses
        if total_games == 0:
            return 0.0
        return self.wins / total_games

    def __str__(self):
        return f"{self.name} ({self.wins}-{self.losses})"

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
        self.games_played = 0

        # Schedule and results
        self.schedule = []  # List of upcoming games
        self.results = []   # List of completed games with box scores

        # Rotation management
        self.rotation_starters = []  # List of 5 player indices
        self.rotation_backups = []   # List of 5 player indices
        self.rotation_bench = []     # List of 2 player indices
        self.rotation_style = "BALANCED"  # SHORT, BALANCED, or DEEP

        # Generate initial roster
        self._generate_roster()
        self._set_default_rotation()

    def _generate_roster(self):
        """Generate a balanced roster of 12 players (3 per class)"""
        first_names = ["James", "Michael", "John", "David", "Chris", "Matt", "Ryan",
                      "Kevin", "Tyler", "Brandon", "Jason", "Josh", "Andrew", "Nick"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                     "Miller", "Davis", "Martinez", "Wilson", "Anderson", "Taylor"]

        # Positions: need variety across all positions
        positions_needed = ["PG", "PG", "SG", "SG", "SF", "SF", "PF", "PF", "C", "C", "SG", "SF"]

        # Years: 3 per class (Fr, So, Jr, Sr)
        years_needed = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]

        # Shuffle to mix positions with years
        import random as rand
        rand.shuffle(positions_needed)
        rand.shuffle(years_needed)

        for i in range(12):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            pos = positions_needed[i]
            year = years_needed[i]
            player = Player(name, pos, year)

            # Older players are generally better
            year_bonus = (year - 1) * 0.5  # +0.5 per year

            # Some randomness in quality
            if random.random() < 0.3:  # 30% chance to be notably better
                player.shooting += random.uniform(1, 2) + year_bonus
                player.defense += random.uniform(1, 2) + year_bonus
                player.athleticism += random.uniform(1, 2) + year_bonus
                player.basketball_iq += random.uniform(1, 2) + year_bonus
                player.rebounding += random.uniform(1, 2) + year_bonus
            else:
                player.shooting += year_bonus
                player.defense += year_bonus
                player.athleticism += year_bonus
                player.basketball_iq += year_bonus
                player.rebounding += year_bonus

            # Cap at 10
            player.shooting = min(10, player.shooting)
            player.defense = min(10, player.defense)
            player.athleticism = min(10, player.athleticism)
            player.basketball_iq = min(10, player.basketball_iq)
            player.rebounding = min(10, player.rebounding)

            self.roster.append(player)

    def _set_default_rotation(self):
        """Set default rotation based on player ratings"""
        if len(self.roster) < 12:
            return

        # Sort players by rating
        sorted_indices = sorted(range(len(self.roster)),
                              key=lambda i: self.roster[i].overall_rating(),
                              reverse=True)

        self.rotation_starters = sorted_indices[:5]
        self.rotation_backups = sorted_indices[5:10]
        self.rotation_bench = sorted_indices[10:12]

    def get_rotation_distribution(self) -> tuple:
        """Get stat distribution percentages based on rotation style"""
        if self.rotation_style == "SHORT":
            return (0.70, 0.25, 0.05)  # Starters, Backups, Bench
        elif self.rotation_style == "DEEP":
            return (0.50, 0.40, 0.10)
        else:  # BALANCED
            return (0.60, 0.33, 0.07)

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

"""
Recruiting system for college basketball
"""

import random
from typing import List
from models import Player, Team


class Recruit:
    """Represents a potential recruit"""

    def __init__(self, name: str, position: str, potential: int):
        self.name = name
        self.position = position
        self.potential = potential  # 1-10 scale (recruiting ranking)
        self.interest = random.randint(40, 100)  # Interest in your program
        self.committed = False
        self.committed_to = None

        # Generate base attributes based on potential
        base = potential - 2
        variance = 1.5

        self.shooting = max(1, min(10, base + random.uniform(-variance, variance)))
        self.defense = max(1, min(10, base + random.uniform(-variance, variance)))
        self.athleticism = max(1, min(10, base + random.uniform(-variance, variance)))
        self.basketball_iq = max(1, min(10, base + random.uniform(-variance, variance)))
        self.rebounding = max(1, min(10, base + random.uniform(-variance, variance)))

    def overall_rating(self) -> float:
        """Calculate overall rating"""
        return (self.shooting + self.defense + self.athleticism +
                self.basketball_iq + self.rebounding) / 5

    def to_player(self) -> Player:
        """Convert recruit to player"""
        player = Player(self.name, self.position, year=1)
        player.shooting = round(self.shooting, 1)
        player.defense = round(self.defense, 1)
        player.athleticism = round(self.athleticism, 1)
        player.basketball_iq = round(self.basketball_iq, 1)
        player.rebounding = round(self.rebounding, 1)
        return player

    def __str__(self):
        return f"{self.name} ({self.position}) - Potential: {self.potential}/10, Interest: {self.interest}%"


class RecruitingClass:
    """Manages the recruiting process"""

    def __init__(self, year: int):
        self.year = year
        self.recruits = self._generate_recruits()

    def _generate_recruits(self) -> List[Recruit]:
        """Generate a pool of recruits"""
        recruits = []

        first_names = ["Marcus", "Tyler", "Jordan", "Chris", "Kevin", "Brandon", "Justin",
                      "Anthony", "Cameron", "Darius", "Isaiah", "Jamal", "Malik", "Trey",
                      "Xavier", "Zion", "RJ", "Cole", "Duke", "Jalen"]
        last_names = ["Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore",
                     "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
                     "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez"]

        positions = ["PG", "SG", "SF", "PF", "C"]

        # Generate 50 recruits with varying potential
        for _ in range(50):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            position = random.choice(positions)

            # Potential distribution: mostly 4-7, few elite (8-10), few low (1-3)
            rand = random.random()
            if rand < 0.05:  # 5% elite
                potential = random.randint(9, 10)
            elif rand < 0.15:  # 10% very good
                potential = 8
            elif rand < 0.40:  # 25% good
                potential = random.randint(6, 7)
            elif rand < 0.75:  # 35% average
                potential = random.randint(4, 5)
            else:  # 25% below average
                potential = random.randint(2, 3)

            recruit = Recruit(name, position, potential)
            recruits.append(recruit)

        # Sort by potential
        recruits.sort(key=lambda r: r.potential, reverse=True)
        return recruits

    def get_available_recruits(self, position: str = None) -> List[Recruit]:
        """Get recruits that haven't committed yet"""
        available = [r for r in self.recruits if not r.committed]

        if position:
            available = [r for r in available if r.position == position]

        return available

    def recruit_player(self, recruit: Recruit, team: Team) -> bool:
        """
        Attempt to recruit a player
        Returns True if successful
        """
        if recruit.committed:
            return False

        # Calculate success chance based on:
        # - Team success (wins)
        # - Recruit's interest
        # - Team rating

        team_factor = (team.wins / max(1, team.wins + team.losses)) * 30  # 0-30
        interest_factor = recruit.interest * 0.5  # 0-50
        rating_factor = team.get_team_rating() * 2  # 0-20

        success_chance = team_factor + interest_factor + rating_factor

        # Add randomness
        roll = random.uniform(0, 100)

        if roll < success_chance:
            recruit.committed = True
            recruit.committed_to = team.name
            return True
        else:
            # Decrease interest slightly on failed attempt
            recruit.interest = max(0, recruit.interest - random.randint(5, 15))
            return False


def recruit_players_auto(team: Team, recruiting_class: RecruitingClass, slots: int):
    """Auto-recruit players for CPU teams"""
    recruited = []

    available = recruiting_class.get_available_recruits()

    # Prefer recruits based on team rating
    team_rating = team.get_team_rating()

    for recruit in available:
        if len(recruited) >= slots:
            break

        # Better teams get better recruits
        if team_rating >= 7.5 and recruit.potential >= 7:
            if random.random() < 0.6:
                recruit.committed = True
                recruit.committed_to = team.name
                recruited.append(recruit)
        elif team_rating >= 6.0 and recruit.potential >= 5:
            if random.random() < 0.5:
                recruit.committed = True
                recruit.committed_to = team.name
                recruited.append(recruit)
        elif recruit.potential >= 3:
            if random.random() < 0.4:
                recruit.committed = True
                recruit.committed_to = team.name
                recruited.append(recruit)

    # Add recruited players to roster
    for recruit in recruited:
        player = recruit.to_player()
        team.roster.append(player)

    return recruited

"""
Recruiting system for college basketball
"""

import random
from typing import List
from models import Player, Team


class Recruit:
    """Represents a potential recruit"""

    def __init__(self, name: str, position: str, potential: int, ranking: int = 0):
        self.name = name
        self.position = position
        self.potential = potential  # 1-10 scale (scouting consensus)
        self.ranking = ranking  # National ranking (1-1080)
        self.stars = self._calculate_stars()  # Star rating (2-5)
        self.interest = random.randint(40, 100)  # Interest in your program
        self.committed = False
        self.committed_to = None

        # Generate ACTUAL attributes with hidden potential variance
        # Stars show what scouts THINK, but actual talent varies!
        # This creates busts and hidden gems

        # Determine outcome: will player live up to hype, bust, or exceed?
        outcome_roll = random.random()

        if self.stars == 5:  # Elite recruits (potential 9-10)
            # 70% live up to hype, 20% decent, 10% bust
            if outcome_roll < 0.70:  # Lives up to hype
                base = self.potential - 1.5
                variance = 1.0
            elif outcome_roll < 0.90:  # Decent but not elite
                base = self.potential - 2.5
                variance = 1.0
            else:  # Major bust
                base = self.potential - 4.0
                variance = 1.5

        elif self.stars == 4:  # Very good recruits (potential 8)
            # 65% good, 25% okay, 10% exceed
            if outcome_roll < 0.65:  # Good as expected
                base = self.potential - 1.5
                variance = 1.2
            elif outcome_roll < 0.90:  # Okay, not great
                base = self.potential - 2.5
                variance = 1.0
            else:  # Exceeds expectations!
                base = self.potential - 0.5
                variance = 1.0

        elif self.stars == 3:  # Solid recruits (potential 6-7)
            # 60% average, 25% below, 15% exceed
            if outcome_roll < 0.60:  # Average
                base = self.potential - 2.0
                variance = 1.5
            elif outcome_roll < 0.85:  # Below average
                base = self.potential - 3.0
                variance = 1.2
            else:  # Hidden gem!
                base = self.potential
                variance = 1.5

        else:  # 2-star recruits (potential 3-5)
            # 60% stay mediocre, 30% solid, 10% hidden gem
            if outcome_roll < 0.60:  # Stays mediocre
                base = self.potential - 2.0
                variance = 1.3
            elif outcome_roll < 0.90:  # Solid contributor
                base = self.potential - 0.5
                variance = 1.5
            else:  # Hidden gem! (Steph Curry scenario)
                base = self.potential + 2.0
                variance = 1.5

        # Generate attributes with variance
        self.shooting = max(1, min(10, base + random.uniform(-variance, variance)))
        self.defense = max(1, min(10, base + random.uniform(-variance, variance)))
        self.athleticism = max(1, min(10, base + random.uniform(-variance, variance)))
        self.basketball_iq = max(1, min(10, base + random.uniform(-variance, variance)))
        self.rebounding = max(1, min(10, base + random.uniform(-variance, variance)))

    def _calculate_stars(self) -> int:
        """Calculate star rating based on potential"""
        if self.potential >= 9:
            return 5
        elif self.potential >= 8:
            return 4
        elif self.potential >= 6:
            return 3
        else:
            return 2

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

    def get_star_display(self) -> str:
        """Get star rating as string"""
        return "★" * self.stars

    def __str__(self):
        return f"#{self.ranking} {self.name} ({self.position}) - {self.get_star_display()}"


class RecruitingClass:
    """Manages the recruiting process"""

    def __init__(self, year: int, num_teams: int = 100):
        self.year = year
        self.num_teams = num_teams
        self.class_quality = self._determine_class_quality()
        self.recruits = self._generate_recruits()

    def _determine_class_quality(self) -> str:
        """Randomly determine if this is a strong, average, or weak recruiting class"""
        rand = random.random()
        if rand < 0.15:  # 15% chance
            return "ELITE"  # Loaded class
        elif rand < 0.30:  # 15% chance
            return "WEAK"   # Weak class
        else:  # 70% chance
            return "AVERAGE"

    def _generate_recruits(self) -> List[Recruit]:
        """Generate a pool of recruits (3 per team = 300 total)"""
        recruits = []

        first_names = ["Marcus", "Tyler", "Jordan", "Chris", "Kevin", "Brandon", "Justin",
                      "Anthony", "Cameron", "Darius", "Isaiah", "Jamal", "Malik", "Trey",
                      "Xavier", "Zion", "RJ", "Cole", "Duke", "Jalen", "Devon", "Trevor",
                      "Austin", "Mason", "Logan", "Dylan", "Jayden", "Caleb", "Nathan",
                      "Ethan", "Aiden", "Jackson", "Carter", "Wyatt", "Grayson"]
        last_names = ["Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson", "Moore",
                     "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
                     "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez",
                     "Lewis", "Walker", "Hall", "Allen", "Young", "King", "Wright", "Lopez",
                     "Hill", "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell"]

        positions = ["PG", "SG", "SF", "PF", "C"]

        # Generate 300 recruits (100 teams × 3 seniors)
        num_recruits = self.num_teams * 3

        for i in range(num_recruits):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            position = random.choice(positions)

            # Adjust potential distribution based on class quality
            if self.class_quality == "ELITE":
                # More elite players in loaded class
                rand = random.random()
                if rand < 0.08:  # 8% elite (24 players)
                    potential = random.randint(9, 10)
                elif rand < 0.20:  # 12% very good
                    potential = 8
                elif rand < 0.50:  # 30% good
                    potential = random.randint(6, 7)
                elif rand < 0.80:  # 30% average
                    potential = random.randint(4, 5)
                else:  # 20% below average
                    potential = random.randint(2, 3)

            elif self.class_quality == "WEAK":
                # Fewer elite players in weak class
                rand = random.random()
                if rand < 0.02:  # 2% elite (6 players)
                    potential = random.randint(9, 10)
                elif rand < 0.08:  # 6% very good
                    potential = 8
                elif rand < 0.30:  # 22% good
                    potential = random.randint(6, 7)
                elif rand < 0.70:  # 40% average
                    potential = random.randint(4, 5)
                else:  # 30% below average
                    potential = random.randint(2, 3)

            else:  # AVERAGE
                # Normal distribution
                rand = random.random()
                if rand < 0.05:  # 5% elite (15 players)
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

        # Sort by potential and assign rankings
        recruits.sort(key=lambda r: r.overall_rating(), reverse=True)
        for i, recruit in enumerate(recruits, 1):
            recruit.ranking = i
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

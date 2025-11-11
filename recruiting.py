"""
Recruiting system for college basketball
"""

import random
from typing import List, Dict
from models import Player, Team


# US States for recruit locations
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
          "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
          "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
          "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


class Recruit:
    """Represents a potential recruit"""

    def __init__(self, name: str, position: str, potential: int, ranking: int = 0):
        self.name = name
        self.position = position
        self.potential = potential  # 1-10 scale (scouting consensus)
        self.ranking = ranking  # National ranking (1-1080)
        self.stars = self._calculate_stars()  # Star rating (2-5)
        self.state = random.choice(STATES)  # Home state

        # Base interest starts at 50
        self.interest = 50
        self.committed = False
        self.committed_to = None

        # Recruiting actions tracking
        self.times_scouted = 0
        self.times_visited = 0
        self.scholarship_offered = False

        # Track which teams are recruiting this player
        self.team_interests = {}  # {team_name: interest_level}
        self.scouted_by = set()  # Teams that have scouted this player
        self.visited_by = set()  # Teams that have visited this player
        self.offers_from = set()  # Teams that have offered scholarship

        # Recruit preferences (what they value most) - each recruit has 2-3 priorities
        self.preferences = self._generate_preferences()

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

    def _generate_preferences(self) -> Dict[str, int]:
        """Generate recruit's preferences (what they value)
        Each preference has a weight 1-5 (5 = most important)
        """
        prefs = {}

        # Randomly select 2-3 top priorities
        all_factors = ["prestige", "playing_time", "location", "conference", "system_fit"]
        num_priorities = random.randint(2, 3)
        priorities = random.sample(all_factors, num_priorities)

        # Assign weights (top priorities get higher weight)
        for factor in all_factors:
            if factor in priorities[:1]:  # Top priority
                prefs[factor] = random.randint(4, 5)
            elif factor in priorities:  # Secondary priority
                prefs[factor] = random.randint(3, 4)
            else:  # Low priority
                prefs[factor] = random.randint(1, 2)

        return prefs

    def get_offense_rating(self) -> str:
        """Get visible offense rating (Bad/Poor/Average/Good/Elite)"""
        avg = (self.shooting + self.basketball_iq) / 2
        return self._rating_to_label(avg)

    def get_defense_rating(self) -> str:
        """Get visible defense rating (Bad/Poor/Average/Good/Elite)"""
        avg = (self.defense + self.athleticism) / 2
        return self._rating_to_label(avg)

    def get_fundamentals_rating(self) -> str:
        """Get visible fundamentals rating (Bad/Poor/Average/Good/Elite)"""
        avg = (self.basketball_iq + self.rebounding) / 2
        return self._rating_to_label(avg)

    def _rating_to_label(self, rating: float) -> str:
        """Convert numeric rating to label"""
        if rating >= 8.5:
            return "Elite"
        elif rating >= 7.0:
            return "Good"
        elif rating >= 5.0:
            return "Average"
        elif rating >= 3.5:
            return "Poor"
        else:
            return "Bad"

    def overall_rating(self) -> float:
        """Calculate overall rating"""
        return (self.shooting + self.defense + self.athleticism +
                self.basketball_iq + self.rebounding) / 5

    def _calculate_realistic_initial_interest(self, team: Team) -> float:
        """Calculate realistic initial interest for a team

        This is used when a team first contacts a recruit who wasn't previously aware of them.
        Uses same logic as initialize_team_interests to ensure consistency.
        """
        team_fit = self.calculate_team_fit(team)

        # Base interest varies by prestige
        if team.prestige == "ELITE":
            base = random.uniform(40, 60)
        elif team.prestige == "HIGH":
            base = random.uniform(30, 50)
        elif team.prestige == "UPPER_MID":
            base = random.uniform(25, 45)
        elif team.prestige == "MID":
            base = random.uniform(20, 40)
        elif team.prestige == "LOW_MID":
            base = random.uniform(15, 35)
        else:  # LOW
            base = random.uniform(10, 30)

        # Adjust for team fit (can add or subtract up to 15)
        fit_adjustment = (team_fit - 60) / 3  # -20 to +13

        # Add some randomness
        random_factor = random.uniform(-8, 8)

        # Calculate final interest
        initial_interest = base + fit_adjustment + random_factor

        # Bound between 10 and 70 (no one starts super high)
        initial_interest = max(10, min(70, initial_interest))

        return initial_interest

    def calculate_team_fit(self, team: Team) -> float:
        """
        Calculate how well this recruit fits with the team (0-100)
        Based on recruit's preferences and team attributes
        """
        fit_score = 0
        max_score = 0

        # Map team prestige to score
        prestige_scores = {
            "ELITE": 100,
            "HIGH": 85,
            "UPPER_MID": 70,
            "MID": 55,
            "LOW_MID": 40,
            "LOW": 25
        }

        # Prestige factor
        weight = self.preferences.get("prestige", 1)
        max_score += weight * 100
        fit_score += weight * prestige_scores.get(team.prestige, 50)

        # Playing time factor (based on roster strength at position)
        weight = self.preferences.get("playing_time", 1)
        max_score += weight * 100
        position_players = [p for p in team.roster if p.position == self.position]
        avg_position_rating = sum(p.overall_rating() for p in position_players) / max(len(position_players), 1)
        # Lower avg rating = more playing time available
        playing_time_score = max(0, 100 - (avg_position_rating * 10))
        fit_score += weight * playing_time_score

        # Location factor (same state or nearby)
        weight = self.preferences.get("location", 1)
        max_score += weight * 100
        # For now, random location fit (could map teams to states later)
        location_score = random.randint(40, 80)
        fit_score += weight * location_score

        # Conference factor (prestige of conference)
        weight = self.preferences.get("conference", 1)
        max_score += weight * 100
        # Power conferences score higher
        power_conferences = ["ACC", "Big Ten", "Big 12", "SEC", "Big East", "Pac-12"]
        conf_score = 90 if team.conference in power_conferences else 60
        fit_score += weight * conf_score

        # System fit (always moderate since systems can be learned)
        weight = self.preferences.get("system_fit", 1)
        max_score += weight * 100
        system_score = random.randint(60, 85)
        fit_score += weight * system_score

        # Normalize to 0-100
        return min(100, (fit_score / max_score) * 100) if max_score > 0 else 50

    def scout_action(self, team: Team):
        """Scout a player - increases interest slightly, reveals more info
        Can only scout a player once per team"""
        if team.name in self.scouted_by:
            return False  # Already scouted by this team

        self.times_scouted += 1
        self.scouted_by.add(team.name)

        # Initialize team interest if not exists (recruit wasn't aware of this team)
        if team.name not in self.team_interests:
            # Use realistic calculation based on prestige, not hardcoded high value
            self.team_interests[team.name] = self._calculate_realistic_initial_interest(team)

        # Minimal interest boost - scouting is mainly for info gathering
        team_fit = self.calculate_team_fit(team)
        base_boost = random.uniform(0.3, 0.5)  # 0.3-0.5 base (reduced from 0.5-1.0)
        fit_bonus = team_fit / 300  # 0-0.33 based on fit (reduced from /200)
        interest_boost = base_boost + fit_bonus  # Total: 0.3-0.8 points (was 0.5-1.5)

        self.team_interests[team.name] = min(100, self.team_interests[team.name] + interest_boost)
        self.interest = self.team_interests[team.name]  # Update current interest
        return True

    def visit_action(self, team: Team):
        """Visit a player - significant interest boost"""
        self.times_visited += 1
        self.visited_by.add(team.name)

        # Initialize team interest if not exists (recruit wasn't aware of this team)
        if team.name not in self.team_interests:
            # Use realistic calculation based on prestige, not hardcoded high value
            self.team_interests[team.name] = self._calculate_realistic_initial_interest(team)

        # Small interest boost - visiting helps but isn't magical
        team_fit = self.calculate_team_fit(team)
        base_boost = random.uniform(1.0, 2.0)  # 1-2 base (reduced from 2-4)
        fit_bonus = team_fit / 100  # 0-1.0 based on fit (reduced from /30)
        interest_boost = base_boost + fit_bonus  # Total: 1-3 points (was 2-7.3)

        self.team_interests[team.name] = min(100, self.team_interests[team.name] + interest_boost)
        self.interest = self.team_interests[team.name]  # Update current interest
        return True

    def offer_scholarship(self, team: Team):
        """Offer scholarship - required before player can commit"""
        self.scholarship_offered = True
        self.offers_from.add(team.name)

        # Initialize team interest if not exists (recruit wasn't aware of this team)
        if team.name not in self.team_interests:
            # Use realistic calculation based on prestige, not hardcoded high value
            self.team_interests[team.name] = self._calculate_realistic_initial_interest(team)

        # Minimal interest boost for being offered - offer is expected, not special
        team_fit = self.calculate_team_fit(team)
        base_boost = random.uniform(0.5, 1.5)  # 0.5-1.5 base (reduced from 1-3)
        fit_bonus = team_fit / 200  # 0-0.5 based on fit (reduced from /40)
        interest_boost = base_boost + fit_bonus  # Total: 0.5-2 points (was 1-5.5)

        self.team_interests[team.name] = min(100, self.team_interests[team.name] + interest_boost)
        self.interest = self.team_interests[team.name]  # Update current interest
        return True

    def get_top_schools(self, limit: int = 5) -> List[tuple]:
        """Get the recruit's top schools by interest level
        Returns list of (team_name, interest_level) tuples"""
        sorted_interests = sorted(
            self.team_interests.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_interests[:limit]

    def can_commit(self, team: Team, current_week: int = 0) -> bool:
        """Check if recruit can commit (needs scholarship offer + high enough interest + right time period)"""
        if not self.scholarship_offered:
            return False

        if self.committed:
            return False

        # Time-based recruiting periods
        # Early signing period: Weeks 4-6 (mid-November)
        # Regular signing period: Weeks 16+ (March-April)
        is_early_period = 4 <= current_week <= 6
        is_regular_period = current_week >= 16

        if not (is_early_period or is_regular_period):
            return False  # Can't commit outside signing periods

        # Elite recruits (5-star, top 100) have MUCH higher standards
        team_fit = self.calculate_team_fit(team)

        # Get team interest (not general interest)
        team_interest = self.team_interests.get(team.name, 50)

        # Base required interest varies by recruit quality - MUCH HIGHER NOW
        if self.stars == 5 or self.ranking <= 20:  # Top 20 recruits
            base_required = 95  # Need near-perfect interest
            # Must be top 2 in their list
            top_schools = self.get_top_schools(2)
            if not any(school[0] == team.name for school in top_schools):
                return False
        elif self.stars == 4 or self.ranking <= 100:  # Top 100 recruits
            base_required = 92  # Very high interest needed
            # Must be top 3 in their list
            top_schools = self.get_top_schools(3)
            if not any(school[0] == team.name for school in top_schools):
                return False
        elif self.stars == 3 or self.ranking <= 300:  # Top 300 recruits
            base_required = 85
        else:
            base_required = 75

        # Reduce required interest based on team fit (max -10, reduced from -20)
        required_interest = max(85, base_required - (team_fit / 10))

        return team_interest >= required_interest

    def attempt_commit(self, team: Team) -> bool:
        """Attempt to get recruit to commit - MUCH HARDER NOW"""
        if not self.can_commit(team):
            return False

        # Success chance - not guaranteed even at high interest
        # Elite recruits are VERY picky
        team_fit = self.calculate_team_fit(team)
        team_interest = self.team_interests.get(team.name, 50)

        # Check if team is #1 choice
        top_schools = self.get_top_schools(5)
        team_rank = next((i for i, (name, _) in enumerate(top_schools, 1) if name == team.name), 999)

        if self.stars == 5 or self.ranking <= 20:  # Top tier - EXTREMELY HARD
            # Need ELITE prestige AND be #1 choice for decent chance
            if team.prestige in ["ELITE"] and team_rank == 1:
                base_chance = 45  # Even #1 elite school only 45% (down from 60)
            elif team.prestige in ["ELITE"] and team_rank <= 2:
                base_chance = 25  # #2 elite school 25% (down from 40)
            elif team.prestige in ["HIGH"] and team_rank == 1:
                base_chance = 30  # High prestige #1 is 30% (down from 50)
            else:
                base_chance = 5  # Almost impossible otherwise (down from 15)
        elif self.stars == 4 or self.ranking <= 100:  # 4-stars - VERY HARD
            if team.prestige in ["ELITE", "HIGH"] and team_rank <= 2:
                base_chance = 50  # Down from 65
            elif team.prestige in ["ELITE", "HIGH", "UPPER_MID"] and team_rank <= 3:
                base_chance = 35  # Down from 50
            else:
                base_chance = 15  # Down from 30
        elif self.stars == 3 or self.ranking <= 300:  # 3-stars - HARD
            if team_rank <= 3:
                base_chance = 55  # Down from 70
            else:
                base_chance = 30  # Down from 45
        else:  # 2-stars - MODERATE
            if team_rank <= 3:
                base_chance = 60  # Down from 75
            else:
                base_chance = 40

        # Add tiny interest bonus (max +5, significantly reduced)
        interest_bonus = (team_interest - 90) / 4  # 0-2.5 bonus max
        success_chance = min(75, base_chance + interest_bonus + (team_fit / 25))  # Cap at 75% (down from 90%)

        if random.uniform(0, 100) < success_chance:
            self.committed = True
            self.committed_to = team.name
            return True

        # Failed - interest decrease
        if team.name in self.team_interests:
            self.team_interests[team.name] = max(30, self.team_interests[team.name] - random.randint(8, 15))
            self.interest = self.team_interests[team.name]
        return False

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

    def update_weekly_interest(self):
        """Update recruit interest levels each week

        Interest naturally fluctuates as recruits consider their options,
        learn more about schools, and are influenced by the season.
        """
        for recruit in self.recruits:
            if recruit.committed:
                continue

            # Update all team interests
            for team_name in list(recruit.team_interests.keys()):
                interest = recruit.team_interests[team_name]

                # Small random fluctuation (-2 to +2)
                base_change = random.uniform(-2, 2)

                # Slight decay if interest is very high (keeps things realistic)
                # Players at 90+ interest will slowly drift down unless actively recruited
                if interest > 90:
                    decay = random.uniform(-1, -0.5)
                elif interest > 80:
                    decay = random.uniform(-0.5, 0)
                else:
                    decay = 0

                # Apply changes
                interest_change = base_change + decay

                # Update interest with bounds (keep between 15 and 100)
                recruit.team_interests[team_name] = max(15, min(100, interest + interest_change))

            # Update general interest to current team's interest if it exists
            if recruit.team_interests:
                recruit.interest = max(recruit.team_interests.values())

    def initialize_team_interests(self, all_teams: List[Team]):
        """Initialize realistic interest levels for all teams

        Creates varied, realistic interest distributions based on:
        - Team prestige (better teams get higher baseline)
        - Team fit with recruit
        - Randomness to create variety
        """
        for recruit in self.recruits:
            # Reset team interests
            recruit.team_interests = {}

            # Determine how many teams this recruit is initially aware of
            # Top recruits know more teams, lower recruits know fewer
            if recruit.stars == 5:
                num_aware = random.randint(15, 25)  # Top recruits know lots of schools
            elif recruit.stars == 4:
                num_aware = random.randint(10, 20)
            elif recruit.stars == 3:
                num_aware = random.randint(8, 15)
            else:
                num_aware = random.randint(5, 10)

            # Select random teams to be aware of, weighted by prestige
            prestige_weights = {
                "ELITE": 10,
                "HIGH": 7,
                "UPPER_MID": 5,
                "MID": 3,
                "LOW_MID": 2,
                "LOW": 1
            }

            # Create weighted list
            weighted_teams = []
            for team in all_teams:
                weight = prestige_weights.get(team.prestige, 1)
                weighted_teams.extend([team] * weight)

            # Select teams
            aware_teams = random.sample(weighted_teams, min(num_aware, len(weighted_teams)))

            # Remove duplicates while preserving some
            aware_teams = list({team.name: team for team in aware_teams}.values())

            # Set initial interest for each team the recruit is aware of
            for team in aware_teams:
                team_fit = recruit.calculate_team_fit(team)

                # Base interest varies by prestige
                if team.prestige == "ELITE":
                    base = random.uniform(40, 60)  # Elite teams start higher
                elif team.prestige == "HIGH":
                    base = random.uniform(30, 50)
                elif team.prestige == "UPPER_MID":
                    base = random.uniform(25, 45)
                elif team.prestige == "MID":
                    base = random.uniform(20, 40)
                elif team.prestige == "LOW_MID":
                    base = random.uniform(15, 35)
                else:  # LOW
                    base = random.uniform(10, 30)

                # Adjust for team fit (can add or subtract up to 15)
                fit_adjustment = (team_fit - 60) / 3  # -20 to +13

                # Add some randomness
                random_factor = random.uniform(-8, 8)

                # Calculate final interest
                initial_interest = base + fit_adjustment + random_factor

                # Bound between 10 and 70 (no one starts super high)
                initial_interest = max(10, min(70, initial_interest))

                recruit.team_interests[team.name] = initial_interest

            # Set general interest to the highest team interest
            if recruit.team_interests:
                recruit.interest = max(recruit.team_interests.values())
            else:
                recruit.interest = 50

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
    """Auto-recruit players for CPU teams - smarter about scholarship limits"""
    recruited = []

    if slots <= 0:
        return recruited

    available = recruiting_class.get_available_recruits()
    team_rating = team.get_team_rating()

    # Determine realistic recruiting targets based on prestige
    # Top teams can be pickier, lower teams need to cast wider net
    prestige_multipliers = {
        "ELITE": 2.5,      # Duke/UNC pursue 2.5x their spots
        "HIGH": 3.0,       # Good teams pursue 3x
        "UPPER_MID": 3.5,  # Mid-major powers pursue 3.5x
        "MID": 4.0,        # Average teams pursue 4x
        "LOW_MID": 4.5,    # Worse teams need more targets
        "LOW": 5.0         # Bottom teams need many targets
    }

    max_targets = int(slots * prestige_multipliers.get(team.prestige, 3.5))
    targets_found = 0

    # Build interest in realistic recruits (don't offer to everyone)
    for recruit in available:
        if targets_found >= max_targets:
            break

        team_fit = recruit.calculate_team_fit(team)

        # Determine if this recruit is a realistic target
        realistic_target = False

        if recruit.stars == 5 or recruit.ranking <= 20:
            # Top recruits - only elite/high prestige teams pursue
            if team.prestige in ["ELITE", "HIGH"] and team_fit > 70:
                realistic_target = random.random() < 0.4
        elif recruit.stars == 4 or recruit.ranking <= 100:
            # 4-star recruits - elite/high/upper-mid pursue
            if team.prestige in ["ELITE", "HIGH"]:
                realistic_target = random.random() < 0.6 if team_fit > 60 else random.random() < 0.3
            elif team.prestige in ["UPPER_MID"] and team_fit > 65:
                realistic_target = random.random() < 0.5
        elif recruit.stars == 3 or recruit.ranking <= 300:
            # 3-star recruits - all teams can pursue
            if team.prestige in ["ELITE", "HIGH"]:
                realistic_target = random.random() < 0.3  # Less focus on 3-stars
            elif team.prestige in ["UPPER_MID", "MID"]:
                realistic_target = random.random() < 0.6 if team_fit > 50 else random.random() < 0.4
            else:
                realistic_target = random.random() < 0.7 if team_fit > 50 else random.random() < 0.5
        else:
            # 2-star recruits - mainly lower tier teams
            if team.prestige in ["MID", "LOW_MID", "LOW"]:
                realistic_target = random.random() < 0.8 if team_fit > 40 else random.random() < 0.6

        if realistic_target:
            targets_found += 1
            # Build interest through simulated recruiting actions
            recruit.interest = max(recruit.interest, 50 + (team_fit / 4))

    # Actually commit recruits based on interest and fit
    for recruit in available:
        if len(recruited) >= slots:
            break

        team_fit = recruit.calculate_team_fit(team)

        # Check if recruit is interested enough and team has good fit
        if recruit.interest >= 65 and team_fit > 60:
            # Success chance based on prestige, fit, and recruit quality
            base_chance = 0.3

            if recruit.stars == 5 or recruit.ranking <= 20:
                if team.prestige in ["ELITE"]:
                    base_chance = 0.6
                elif team.prestige in ["HIGH"]:
                    base_chance = 0.4
                else:
                    base_chance = 0.1
            elif recruit.stars == 4 or recruit.ranking <= 100:
                if team.prestige in ["ELITE", "HIGH"]:
                    base_chance = 0.6
                elif team.prestige in ["UPPER_MID"]:
                    base_chance = 0.5
                else:
                    base_chance = 0.3
            else:
                if team.prestige in ["ELITE", "HIGH"]:
                    base_chance = 0.8
                else:
                    base_chance = 0.6

            # Add fit bonus
            fit_bonus = (team_fit - 60) / 100  # 0-0.4 bonus
            success_chance = base_chance + fit_bonus

            if random.random() < success_chance:
                recruit.committed = True
                recruit.committed_to = team.name
                recruited.append(recruit)

    # Add recruited players to roster
    for recruit in recruited:
        player = recruit.to_player()
        team.roster.append(player)

    return recruited

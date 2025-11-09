"""
Game simulation engine
"""

import random
from typing import Tuple, Dict
from models import Team, Player
from constants import POSSESSIONS_PER_GAME


class GameEngine:
    """Simulates basketball games based on team attributes and systems"""

    def __init__(self):
        # System matchup modifiers
        self.offensive_bonuses = {
            "Motion Offense": {"shooting": 0.1, "basketball_iq": 0.15},
            "Princeton Offense": {"basketball_iq": 0.2, "shooting": 0.1},
            "Fast Break": {"athleticism": 0.2, "shooting": 0.05},
            "Pick and Roll": {"basketball_iq": 0.15, "athleticism": 0.1},
            "Isolation": {"shooting": 0.15, "athleticism": 0.1},
            "Triangle Offense": {"basketball_iq": 0.15, "shooting": 0.1}
        }

        self.defensive_bonuses = {
            "Man-to-Man": {"defense": 0.15, "athleticism": 0.1},
            "2-3 Zone": {"defense": 0.1, "rebounding": 0.15},
            "1-3-1 Zone": {"defense": 0.1, "basketball_iq": 0.1},
            "Full Court Press": {"athleticism": 0.2, "defense": 0.1},
            "Pack Line": {"defense": 0.2, "basketball_iq": 0.05},
            "Match-Up Zone": {"defense": 0.1, "basketball_iq": 0.15}
        }

    def simulate_game(self, home_team: Team, away_team: Team, is_conference: bool = False) -> Tuple[int, int]:
        """
        Simulate a game between two teams
        Returns (home_score, away_score)
        """
        home_score = self._calculate_team_score(home_team, away_team, is_home=True)
        away_score = self._calculate_team_score(away_team, home_team, is_home=False)

        # Update team games played
        home_team.games_played += 1
        away_team.games_played += 1

        # Update records
        if home_score > away_score:
            home_team.wins += 1
            away_team.losses += 1
            if is_conference:
                home_team.conference_wins += 1
                away_team.conference_losses += 1
        else:
            away_team.wins += 1
            home_team.losses += 1
            if is_conference:
                away_team.conference_wins += 1
                home_team.conference_losses += 1

        # Update player stats
        self._update_player_stats(home_team, home_score)
        self._update_player_stats(away_team, away_score)

        return home_score, away_score

    def _calculate_team_score(self, team: Team, opponent: Team, is_home: bool = True) -> int:
        """Calculate a team's score based on attributes and systems"""
        starters = team.get_starting_five()

        # Base offensive rating
        offensive_rating = sum(p.overall_rating() for p in starters) / 5

        # Apply offensive system bonuses
        offensive_bonuses = self.offensive_bonuses.get(team.offensive_system, {})
        for attr, bonus in offensive_bonuses.items():
            avg_attr = sum(getattr(p, attr) for p in starters) / 5
            offensive_rating += avg_attr * bonus

        # Opponent defensive rating
        opponent_starters = opponent.get_starting_five()
        defensive_rating = sum(p.defense for p in opponent_starters) / 5

        # Apply opponent defensive system
        defensive_bonuses = self.defensive_bonuses.get(opponent.defensive_system, {})
        for attr, bonus in defensive_bonuses.items():
            avg_attr = sum(getattr(p, attr) for p in opponent_starters) / 5
            defensive_rating += avg_attr * bonus

        # Home court advantage
        if is_home:
            offensive_rating += 0.5

        # Calculate efficiency (points per possession)
        efficiency = 0.95 + (offensive_rating - defensive_rating) * 0.02
        efficiency = max(0.7, min(1.3, efficiency))  # Clamp between 0.7 and 1.3

        # Calculate score
        possessions = random.randint(65, 75)
        base_score = possessions * efficiency

        # Add some randomness (clutch plays, hot/cold shooting)
        variance = random.uniform(-5, 5)
        final_score = int(base_score + variance)

        return max(50, final_score)  # Minimum 50 points

    def _update_player_stats(self, team: Team, team_score: int):
        """Update player statistics after a game"""
        starters = team.get_starting_five()

        # Distribute points among starters (with some randomness)
        for player in starters:
            player.games_played += 1

            # Points based on shooting ability and some randomness
            shooting_factor = player.shooting / 10
            points = int(team_score * shooting_factor * random.uniform(0.08, 0.18))
            player.points += points

            # Rebounds based on rebounding attribute
            rebounding_factor = player.rebounding / 10
            rebounds = int(random.uniform(2, 10) * rebounding_factor)
            player.rebounds += rebounds

            # Assists based on basketball IQ (guards get more)
            if player.position in ["PG", "SG"]:
                iq_factor = player.basketball_iq / 10
                assists = int(random.uniform(1, 6) * iq_factor)
                player.assists += assists
            else:
                player.assists += random.randint(0, 2)

            # Steals based on defense
            defense_factor = player.defense / 10
            steals = int(random.uniform(0, 3) * defense_factor)
            player.steals += steals

            # Blocks based on rebounding and position (big men get more)
            if player.position in ["PF", "C"]:
                rebounding_factor = player.rebounding / 10
                blocks = int(random.uniform(0, 3) * rebounding_factor)
                player.blocks += blocks
            else:
                player.blocks += random.randint(0, 1)

        # Bench players get minimal stats
        for player in team.roster[5:]:
            if random.random() < 0.6:  # 60% chance bench player sees action
                player.games_played += 1
                player.points += random.randint(0, 5)
                player.rebounds += random.randint(0, 3)
                player.assists += random.randint(0, 2)

    def simulate_game_with_details(self, home_team: Team, away_team: Team, is_conference: bool = False) -> Dict:
        """
        Simulate a game and return detailed results with box score
        """
        home_score, away_score = self.simulate_game(home_team, away_team, is_conference)

        result = {
            "home_team": home_team.name,
            "away_team": away_team.name,
            "home_score": home_score,
            "away_score": away_score,
            "winner": home_team.name if home_score > away_score else away_team.name,
            "margin": abs(home_score - away_score),
            "is_conference": is_conference,
            "home_team_obj": home_team,
            "away_team_obj": away_team
        }

        # Store result in both teams' history
        home_team.results.append(result)
        away_team.results.append(result)

        return result

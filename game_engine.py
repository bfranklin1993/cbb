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

        # Handle overtime - keep playing until there's a winner
        overtime_count = 0
        while home_score == away_score:
            overtime_count += 1
            # Each overtime is 5 minutes (about 1/8 of regulation)
            ot_home = self._calculate_overtime_score(home_team, away_team, is_home=True)
            ot_away = self._calculate_overtime_score(away_team, home_team, is_home=False)
            home_score += ot_home
            away_score += ot_away

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

    def _calculate_overtime_score(self, team: Team, opponent: Team, is_home: bool = True) -> int:
        """Calculate score for a 5-minute overtime period"""
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

        # Calculate efficiency
        efficiency = 0.95 + (offensive_rating - defensive_rating) * 0.02
        efficiency = max(0.7, min(1.3, efficiency))

        # OT is about 1/8 of regulation (5 min vs 40 min)
        possessions = random.randint(8, 12)
        base_score = possessions * efficiency

        # Add some randomness
        variance = random.uniform(-1, 1)
        final_score = int(base_score + variance)

        return max(5, final_score)  # Minimum 5 points in OT

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
        # Increased multiplier to make rating differences matter more
        efficiency = 0.95 + (offensive_rating - defensive_rating) * 0.04
        efficiency = max(0.65, min(1.35, efficiency))  # Wider range: 0.65-1.35

        # Calculate score - possessions vary more
        possessions = random.randint(60, 80)  # More variance in pace
        base_score = possessions * efficiency

        # Add significant randomness (hot/cold shooting, clutch plays, luck)
        variance = random.uniform(-10, 10)  # Doubled variance
        final_score = int(base_score + variance)

        return max(45, final_score)  # Lower minimum for blowouts

    def _update_player_stats(self, team: Team, team_score: int):
        """Update player statistics after a game using rotation system"""
        # Get rotation distribution percentages
        starter_pct, backup_pct, bench_pct = team.get_rotation_distribution()

        # Calculate stats pool for each group
        starter_stats = team_score * starter_pct
        backup_stats = team_score * backup_pct
        bench_stats = team_score * bench_pct

        # Distribute stats to starters
        for idx in team.rotation_starters:
            if idx < len(team.roster):
                player = team.roster[idx]
                player.games_played += 1
                self._assign_player_stats(player, starter_stats / 5)

        # Distribute stats to backups
        for idx in team.rotation_backups:
            if idx < len(team.roster):
                player = team.roster[idx]
                player.games_played += 1
                self._assign_player_stats(player, backup_stats / 5)

        # Distribute stats to bench (may not play every game)
        for idx in team.rotation_bench:
            if idx < len(team.roster):
                player = team.roster[idx]
                if random.random() < 0.7:  # 70% chance bench player sees action
                    player.games_played += 1
                    self._assign_player_stats(player, bench_stats / 2)

    def _assign_player_stats(self, player: Player, points_pool: float):
        """Assign stats to a player based on their attributes"""
        # Points based on shooting ability and some randomness
        shooting_factor = player.shooting / 10
        points = int(points_pool * shooting_factor * random.uniform(0.8, 1.2))
        player.points += points

        # Rebounds based on rebounding attribute
        rebounding_factor = player.rebounding / 10
        rebounds = int(random.uniform(1, 6) * rebounding_factor * (points_pool / 10))
        player.rebounds += rebounds

        # Assists based on basketball IQ (guards get more)
        if player.position in ["PG", "SG"]:
            iq_factor = player.basketball_iq / 10
            assists = int(random.uniform(1, 4) * iq_factor * (points_pool / 10))
            player.assists += assists
        else:
            assists = int(random.uniform(0, 2) * (points_pool / 15))
            player.assists += assists

        # Steals based on defense
        defense_factor = player.defense / 10
        steals = int(random.uniform(0, 2) * defense_factor * (points_pool / 15))
        player.steals += steals

        # Blocks based on rebounding and position (big men get more)
        if player.position in ["PF", "C"]:
            rebounding_factor = player.rebounding / 10
            blocks = int(random.uniform(0, 2) * rebounding_factor * (points_pool / 15))
            player.blocks += blocks
        else:
            if random.random() < 0.3:
                player.blocks += 1

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

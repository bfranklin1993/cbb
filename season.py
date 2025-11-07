"""
Season management and scheduling
"""

import random
from typing import List, Tuple
from models import Team
from game_engine import GameEngine
from teams_data import get_conference_teams, CONFERENCES


class Season:
    """Manages a college basketball season"""

    def __init__(self, all_teams: List[Team], year: int = 2024):
        self.all_teams = all_teams
        self.year = year
        self.game_engine = GameEngine()
        self.schedule = []
        self.current_week = 0
        self.total_weeks = 15  # ~15 weeks of regular season

    def generate_schedule(self):
        """Generate the season schedule"""
        self.schedule = []

        for team in self.all_teams:
            conference_teams = [t for t in self.all_teams if t.conference == team.conference and t != team]
            other_teams = [t for t in self.all_teams if t.conference != team.conference]

            # Play each conference team twice (home and away)
            conference_games = []
            for opponent in conference_teams:
                # Home game
                conference_games.append((team, opponent, True))

            # Play ~10 non-conference games
            non_conf_opponents = random.sample(other_teams, min(10, len(other_teams)))
            non_conf_games = [(team, opp, False) for opp in non_conf_opponents]

            team_schedule = conference_games + non_conf_games
            random.shuffle(team_schedule)

            # Only add if this team is "home" to avoid duplicates
            for game in team_schedule[:30]:  # Limit to 30 games
                if game not in self.schedule:
                    # Check reverse (away game) isn't already scheduled
                    reverse = (game[1], game[0], game[2])
                    if reverse not in self.schedule:
                        self.schedule.append(game)

    def simulate_week(self) -> List[dict]:
        """Simulate one week of games"""
        if self.current_week >= self.total_weeks:
            return []

        # Calculate games per week
        games_per_week = len(self.schedule) // self.total_weeks
        start_idx = self.current_week * games_per_week
        end_idx = start_idx + games_per_week

        week_games = self.schedule[start_idx:end_idx]
        results = []

        for home_team, away_team, is_conference in week_games:
            result = self.game_engine.simulate_game_with_details(
                home_team, away_team, is_conference
            )
            results.append(result)

        self.current_week += 1
        return results

    def simulate_full_season(self):
        """Simulate the entire regular season"""
        while self.current_week < self.total_weeks:
            self.simulate_week()

    def get_conference_standings(self, conference: str) -> List[Team]:
        """Get conference standings sorted by conference record"""
        conf_teams = [t for t in self.all_teams if t.conference == conference]
        conf_teams.sort(key=lambda t: (t.conference_wins, -t.conference_losses, t.wins), reverse=True)
        return conf_teams

    def get_top_teams(self, count: int = 68) -> List[Team]:
        """Get top teams for tournament selection"""
        # Sort by overall record and strength
        sorted_teams = sorted(self.all_teams,
                            key=lambda t: (t.wins - t.losses, t.get_team_rating()),
                            reverse=True)
        return sorted_teams[:count]

    def get_standings(self) -> List[Team]:
        """Get overall standings"""
        return sorted(self.all_teams,
                     key=lambda t: (t.wins, -t.losses),
                     reverse=True)

    def display_scoreboard(self, results: List[dict]):
        """Display game results"""
        print("\n" + "="*60)
        print(f"WEEK {self.current_week} RESULTS")
        print("="*60)

        for result in results:
            winner_marker_home = "**" if result["home_score"] > result["away_score"] else "  "
            winner_marker_away = "**" if result["away_score"] > result["home_score"] else "  "

            print(f"{winner_marker_home}{result['home_team']:25} {result['home_score']:3}")
            print(f"{winner_marker_away}{result['away_team']:25} {result['away_score']:3}")
            print("-" * 60)

    def display_standings(self, limit: int = 25):
        """Display top teams standings"""
        print("\n" + "="*70)
        print(f"TOP {limit} TEAMS - {self.year} SEASON")
        print("="*70)
        print(f"{'Rank':<6}{'Team':<25}{'Record':<12}{'Conf':<8}{'Rating':<8}")
        print("-" * 70)

        standings = self.get_standings()
        for i, team in enumerate(standings[:limit], 1):
            record = f"{team.wins}-{team.losses}"
            conf_record = f"{team.conference_wins}-{team.conference_losses}"
            rating = f"{team.get_team_rating():.1f}"
            print(f"{i:<6}{team.name:<25}{record:<12}{conf_record:<8}{rating:<8}")

    def advance_players(self):
        """Advance players to next year and develop them"""
        for team in self.all_teams:
            for player in team.roster[:]:
                # Develop player
                player.develop()

                # Advance year
                player.year += 1

                # Seniors graduate
                if player.year > 4:
                    team.roster.remove(player)

            # Recruit new players to fill roster
            while len(team.roster) < 12:
                team._generate_roster()
                # Keep only the new player(s)
                team.roster = team.roster[:12]

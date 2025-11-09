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
        """Generate the season schedule organized by weeks"""
        # Schedule is now a list of weeks, where each week is a list of games
        self.schedule = [[] for _ in range(self.total_weeks)]
        scheduled_matchups = set()
        all_games = []

        # Generate conference games - each pair plays once
        for conference in CONFERENCES.keys():
            conf_teams = [t for t in self.all_teams if t.conference == conference]

            # Round robin - each team plays each other once
            for i, team1 in enumerate(conf_teams):
                for team2 in conf_teams[i+1:]:
                    matchup = tuple(sorted([team1.name, team2.name]))

                    if matchup not in scheduled_matchups:
                        # Randomly assign home team
                        if random.random() < 0.5:
                            all_games.append((team1, team2, True))
                        else:
                            all_games.append((team2, team1, True))
                        scheduled_matchups.add(matchup)

        # Generate non-conference games (fewer for balance)
        for team in self.all_teams:
            other_conf_teams = [t for t in self.all_teams if t.conference != team.conference]

            # Each team plays 5-8 non-conference games
            num_non_conf = min(random.randint(5, 8), len(other_conf_teams))
            opponents = random.sample(other_conf_teams, num_non_conf)

            for opponent in opponents:
                matchup = tuple(sorted([team.name, opponent.name]))

                if matchup not in scheduled_matchups:
                    if random.random() < 0.5:
                        all_games.append((team, opponent, False))
                    else:
                        all_games.append((opponent, team, False))
                    scheduled_matchups.add(matchup)

        # Distribute games across weeks, ensuring no team plays multiple times per week
        random.shuffle(all_games)

        for game in all_games:
            home_team, away_team, is_conf = game

            # Find the earliest week where both teams can play
            for week_idx in range(self.total_weeks):
                week_teams = set()
                for g in self.schedule[week_idx]:
                    week_teams.add(g[0].name)
                    week_teams.add(g[1].name)

                # Check if both teams are available this week
                if home_team.name not in week_teams and away_team.name not in week_teams:
                    self.schedule[week_idx].append(game)
                    break

    def simulate_week(self) -> List[dict]:
        """Simulate one week of games"""
        if self.current_week >= self.total_weeks:
            return []

        # Get this week's games
        week_games = self.schedule[self.current_week]
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

    def get_team_schedule(self, team: Team) -> List[dict]:
        """Get full season schedule for a specific team"""
        team_schedule = []

        for week_idx, week_games in enumerate(self.schedule):
            for home_team, away_team, is_conference in week_games:
                if home_team.name == team.name or away_team.name == team.name:
                    is_home = home_team.name == team.name
                    opponent = away_team if is_home else home_team

                    # Check if game has been played (week is in the past)
                    played = week_idx < self.current_week

                    game_info = {
                        'week': week_idx + 1,
                        'opponent': opponent.name,
                        'is_home': is_home,
                        'is_conference': is_conference,
                        'played': played
                    }

                    # If played, get the result
                    if played:
                        for result in team.results:
                            home_match = result['home_team'] == team.name or result['home_team'] == opponent.name
                            away_match = result['away_team'] == team.name or result['away_team'] == opponent.name

                            if home_match and away_match:
                                if is_home:
                                    game_info['team_score'] = result['home_score']
                                    game_info['opp_score'] = result['away_score']
                                else:
                                    game_info['team_score'] = result['away_score']
                                    game_info['opp_score'] = result['home_score']
                                game_info['won'] = game_info['team_score'] > game_info['opp_score']
                                break

                    team_schedule.append(game_info)

        return team_schedule

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

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
        self.total_weeks = 18  # 18 weeks of regular season (Nov-Feb)

    def generate_schedule(self):
        """Generate realistic 30-33 game schedule per team"""
        # Schedule is now a list of weeks, where each week is a list of games
        self.schedule = [[] for _ in range(self.total_weeks)]
        scheduled_matchups = set()
        all_games = []

        # Generate conference games - realistic counts based on conference size
        for conference in CONFERENCES.keys():
            conf_teams = [t for t in self.all_teams if t.conference == conference]
            conf_size = len(conf_teams)

            # Determine number of conference games based on conference size
            if conf_size >= 16:
                # Large conferences: 18-20 games (like SEC, ACC, Big Ten)
                target_conf_games = 20 if conf_size >= 17 else 19
            elif conf_size >= 10:
                # Medium conferences: 18-20 games
                target_conf_games = 19
            else:
                # Small conferences: Play everyone home and away
                target_conf_games = (conf_size - 1) * 2

            # Play each conference opponent at least once
            for i, team1 in enumerate(conf_teams):
                for team2 in conf_teams[i+1:]:
                    matchup = tuple(sorted([team1.name, team2.name]))

                    if matchup not in scheduled_matchups:
                        # Home game for one team
                        if random.random() < 0.5:
                            all_games.append((team1, team2, True))
                        else:
                            all_games.append((team2, team1, True))
                        scheduled_matchups.add(matchup)

            # Add return games to reach target conference games
            games_per_team_so_far = conf_size - 1
            if games_per_team_so_far < target_conf_games:
                # Calculate how many return games needed
                return_games_needed = (target_conf_games - games_per_team_so_far) // 2

                # Add return games for random matchups
                for i, team1 in enumerate(conf_teams):
                    if return_games_needed > 0:
                        # Select random opponents for return games
                        num_return = min(return_games_needed, len(conf_teams) - 1)
                        opponents = random.sample([t for t in conf_teams if t != team1], num_return)

                        for team2 in opponents:
                            # Add return game (opposite venue from first game)
                            all_games.append((team2, team1, True))

        # Generate non-conference games - 5-7 games per team
        # (Since each matchup creates games for 2 teams, we request fewer)
        for team in self.all_teams:
            other_conf_teams = [t for t in self.all_teams if t.conference != team.conference]

            # Each team plays 5-7 non-conference games
            # This results in ~10-14 total non-conf games per team when counting both sides
            num_non_conf = min(random.randint(5, 7), len(other_conf_teams))
            opponents = random.sample(other_conf_teams, num_non_conf)

            for opponent in opponents:
                matchup = tuple(sorted([team.name, opponent.name]))

                if matchup not in scheduled_matchups:
                    if random.random() < 0.5:
                        all_games.append((team, opponent, False))
                    else:
                        all_games.append((opponent, team, False))
                    scheduled_matchups.add(matchup)

        # Distribute games across weeks - teams can play 2 games per week (realistic)
        random.shuffle(all_games)

        for game in all_games:
            home_team, away_team, is_conf = game

            # Find the earliest week where both teams haven't played too much
            for week_idx in range(self.total_weeks):
                week_teams = {}
                for g in self.schedule[week_idx]:
                    week_teams[g[0].name] = week_teams.get(g[0].name, 0) + 1
                    week_teams[g[1].name] = week_teams.get(g[1].name, 0) + 1

                # Each team can play up to 2 games per week
                if week_teams.get(home_team.name, 0) < 2 and week_teams.get(away_team.name, 0) < 2:
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

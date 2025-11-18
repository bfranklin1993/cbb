"""
Tournament system for NCAA and NIT
"""

import random
from typing import List, Optional, Tuple
from models import Team
from game_engine import GameEngine


class Tournament:
    """Base tournament class"""

    def __init__(self, name: str, teams: List[Team], game_engine: GameEngine):
        self.name = name
        self.teams = teams
        self.game_engine = game_engine
        self.champion: Optional[Team] = None
        self.rounds = []

    def seed_teams(self):
        """Seed teams based on their records"""
        # Sort by wins, then rating
        self.teams.sort(key=lambda t: (t.wins, t.get_team_rating()), reverse=True)

    def simulate_round(self, matchups: List[Tuple[Team, Team]], round_name: str) -> List[Team]:
        """Simulate a tournament round"""
        print(f"\n{'='*60}")
        print(f"{self.name} - {round_name}")
        print(f"{'='*60}")

        winners = []
        for i, (team1, team2) in enumerate(matchups, 1):
            result = self.game_engine.simulate_game_with_details(team1, team2)

            winner = team1 if result["home_score"] > result["away_score"] else team2
            winners.append(winner)

            winner_marker_1 = "**" if winner == team1 else "  "
            winner_marker_2 = "**" if winner == team2 else "  "

            print(f"\nGame {i}:")
            print(f"{winner_marker_1}{result['home_team']:30} {result['home_score']:3}")
            print(f"{winner_marker_2}{result['away_team']:30} {result['away_score']:3}")

        self.rounds.append({
            "name": round_name,
            "matchups": matchups,
            "winners": winners
        })

        return winners

    def create_matchups(self, teams: List[Team]) -> List[Tuple[Team, Team]]:
        """Create matchups from a list of teams"""
        matchups = []
        for i in range(0, len(teams), 2):
            if i + 1 < len(teams):
                matchups.append((teams[i], teams[i + 1]))
        return matchups


class ConferenceTournament(Tournament):
    """Conference Tournament - varies by conference size"""

    def __init__(self, conference_name: str, teams: List[Team], game_engine: GameEngine):
        super().__init__(f"{conference_name} Tournament", teams, game_engine)
        self.conference_name = conference_name

    def simulate(self) -> Team:
        """Simulate conference tournament based on number of teams"""
        # Seed by conference record, then overall record
        self.teams.sort(key=lambda t: (t.conference_wins, t.wins, t.get_team_rating()), reverse=True)

        num_teams = len(self.teams)

        # Determine tournament format based on conference size
        if num_teams <= 8:
            # Small conference: All teams play, quarterfinals start
            return self._simulate_8_team_bracket()
        elif num_teams <= 12:
            # Medium conference: Top 8-12 teams
            tournament_teams = self.teams[:min(12, num_teams)]
            return self._simulate_12_team_bracket(tournament_teams)
        else:
            # Large conference: Top 12-14 teams
            tournament_teams = self.teams[:min(14, num_teams)]
            return self._simulate_14_team_bracket(tournament_teams)

    def _simulate_8_team_bracket(self) -> Team:
        """8 team bracket: Quarterfinals -> Semifinals -> Final"""
        # Quarterfinals
        qf_matchups = [
            (self.teams[0], self.teams[7]),
            (self.teams[1], self.teams[6]),
            (self.teams[2], self.teams[5]),
            (self.teams[3], self.teams[4])
        ]
        sf_teams = self.simulate_round(qf_matchups, "QUARTERFINALS")

        # Semifinals
        sf_matchups = self.create_matchups(sf_teams)
        final_teams = self.simulate_round(sf_matchups, "SEMIFINALS")

        # Championship
        championship = [(final_teams[0], final_teams[1])]
        champions = self.simulate_round(championship, "CHAMPIONSHIP")

        self.champion = champions[0]
        return self.champion

    def _simulate_12_team_bracket(self, teams: List[Team]) -> Team:
        """12 team bracket: Top 4 get byes, Round of 12 -> QF -> SF -> Final"""
        # Top 4 get first round byes
        bye_teams = teams[:4]
        first_round_teams = teams[4:12]

        # First Round (8 teams play, 4 advance)
        fr_matchups = [
            (first_round_teams[0], first_round_teams[7]),  # 5 vs 12
            (first_round_teams[1], first_round_teams[6]),  # 6 vs 11
            (first_round_teams[2], first_round_teams[5]),  # 7 vs 10
            (first_round_teams[3], first_round_teams[4])   # 8 vs 9
        ]
        fr_winners = self.simulate_round(fr_matchups, "FIRST ROUND")

        # Quarterfinals (byes + first round winners)
        qf_matchups = [
            (bye_teams[0], fr_winners[3]),  # 1 vs 8/9 winner
            (bye_teams[1], fr_winners[2]),  # 2 vs 7/10 winner
            (bye_teams[2], fr_winners[1]),  # 3 vs 6/11 winner
            (bye_teams[3], fr_winners[0])   # 4 vs 5/12 winner
        ]
        sf_teams = self.simulate_round(qf_matchups, "QUARTERFINALS")

        # Semifinals
        sf_matchups = self.create_matchups(sf_teams)
        final_teams = self.simulate_round(sf_matchups, "SEMIFINALS")

        # Championship
        championship = [(final_teams[0], final_teams[1])]
        champions = self.simulate_round(championship, "CHAMPIONSHIP")

        self.champion = champions[0]
        return self.champion

    def _simulate_14_team_bracket(self, teams: List[Team]) -> Team:
        """14 team bracket: Top 2 get double byes"""
        # Top 2 get second round byes
        double_bye_teams = teams[:2]
        single_bye_teams = teams[2:6]
        first_round_teams = teams[6:14]

        # First Round
        fr_matchups = [
            (first_round_teams[0], first_round_teams[7]),  # 7 vs 14
            (first_round_teams[1], first_round_teams[6]),  # 8 vs 13
            (first_round_teams[2], first_round_teams[5]),  # 9 vs 12
            (first_round_teams[3], first_round_teams[4])   # 10 vs 11
        ]
        fr_winners = self.simulate_round(fr_matchups, "FIRST ROUND")

        # Second Round (single byes + first round winners)
        r2_matchups = [
            (single_bye_teams[0], fr_winners[3]),  # 3 vs 10/11
            (single_bye_teams[1], fr_winners[2]),  # 4 vs 9/12
            (single_bye_teams[2], fr_winners[1]),  # 5 vs 8/13
            (single_bye_teams[3], fr_winners[0])   # 6 vs 7/14
        ]
        r2_winners = self.simulate_round(r2_matchups, "SECOND ROUND")

        # Quarterfinals (double byes + second round winners)
        qf_matchups = [
            (double_bye_teams[0], r2_winners[3]),  # 1 vs lowest seed
            (double_bye_teams[1], r2_winners[2])   # 2 vs next lowest
        ] + self.create_matchups(r2_winners[:2])
        sf_teams = self.simulate_round(qf_matchups, "QUARTERFINALS")

        # Semifinals
        sf_matchups = self.create_matchups(sf_teams)
        final_teams = self.simulate_round(sf_matchups, "SEMIFINALS")

        # Championship
        championship = [(final_teams[0], final_teams[1])]
        champions = self.simulate_round(championship, "CHAMPIONSHIP")

        self.champion = champions[0]
        return self.champion


class NCAABracket(Tournament):
    """NCAA Tournament (March Madness) - 68 teams"""

    def __init__(self, teams: List[Team], game_engine: GameEngine):
        super().__init__("NCAA TOURNAMENT", teams[:68], game_engine)

    def simulate(self) -> Team:
        """Simulate the entire NCAA tournament"""
        self.seed_teams()

        print(f"\n{'='*60}")
        print(f"NCAA TOURNAMENT BRACKET - {len(self.teams)} TEAMS")
        print(f"{'='*60}")

        # First Four (68 -> 64)
        first_four_teams = self.teams[64:68]
        remaining_64 = self.teams[:64]

        if len(first_four_teams) == 4:
            first_four_matchups = self.create_matchups(first_four_teams)
            first_four_winners = self.simulate_round(first_four_matchups, "FIRST FOUR")
            round_of_64_teams = remaining_64 + first_four_winners
        else:
            round_of_64_teams = self.teams[:64]

        # Round of 64
        round_of_64_matchups = self.create_matchups(round_of_64_teams)
        round_of_32_teams = self.simulate_round(round_of_64_matchups, "ROUND OF 64")

        # Round of 32
        round_of_32_matchups = self.create_matchups(round_of_32_teams)
        sweet_16_teams = self.simulate_round(round_of_32_matchups, "ROUND OF 32")

        # Sweet 16
        sweet_16_matchups = self.create_matchups(sweet_16_teams)
        elite_8_teams = self.simulate_round(sweet_16_matchups, "SWEET SIXTEEN")

        # Elite 8
        elite_8_matchups = self.create_matchups(elite_8_teams)
        final_4_teams = self.simulate_round(elite_8_matchups, "ELITE EIGHT")

        # Final Four
        final_4_matchups = self.create_matchups(final_4_teams)
        championship_teams = self.simulate_round(final_4_matchups, "FINAL FOUR")

        # Championship
        championship_matchup = [(championship_teams[0], championship_teams[1])]
        champions = self.simulate_round(championship_matchup, "NATIONAL CHAMPIONSHIP")

        self.champion = champions[0]

        print(f"\n{'*'*60}")
        print(f"NCAA CHAMPION: {self.champion.name}".center(60))
        print(f"{'*'*60}\n")

        return self.champion


class NITBracket(Tournament):
    """NIT Tournament - 32 teams"""

    def __init__(self, teams: List[Team], game_engine: GameEngine):
        super().__init__("NIT TOURNAMENT", teams[:32], game_engine)

    def simulate(self) -> Team:
        """Simulate the entire NIT tournament"""
        self.seed_teams()

        print(f"\n{'='*60}")
        print(f"NIT TOURNAMENT BRACKET - {len(self.teams)} TEAMS")
        print(f"{'='*60}")

        # Round of 32
        round_of_32_matchups = self.create_matchups(self.teams)
        round_of_16_teams = self.simulate_round(round_of_32_matchups, "ROUND OF 32")

        # Round of 16
        round_of_16_matchups = self.create_matchups(round_of_16_teams)
        quarterfinal_teams = self.simulate_round(round_of_16_matchups, "ROUND OF 16")

        # Quarterfinals
        quarterfinal_matchups = self.create_matchups(quarterfinal_teams)
        semifinal_teams = self.simulate_round(quarterfinal_matchups, "QUARTERFINALS")

        # Semifinals
        semifinal_matchups = self.create_matchups(semifinal_teams)
        championship_teams = self.simulate_round(semifinal_matchups, "SEMIFINALS")

        # Championship
        championship_matchup = [(championship_teams[0], championship_teams[1])]
        champions = self.simulate_round(championship_matchup, "NIT CHAMPIONSHIP")

        self.champion = champions[0]

        print(f"\n{'*'*60}")
        print(f"NIT CHAMPION: {self.champion.name}".center(60))
        print(f"{'*'*60}\n")

        return self.champion


def run_postseason(all_teams: List[Team], game_engine: GameEngine):
    """Run both NCAA and NIT tournaments"""

    # Sort teams by record
    sorted_teams = sorted(all_teams,
                         key=lambda t: (t.wins - t.losses, t.get_team_rating()),
                         reverse=True)

    # Top 68 go to NCAA
    ncaa_teams = sorted_teams[:68]
    # Next 32 go to NIT
    nit_teams = sorted_teams[68:100]

    print("\n" + "="*60)
    print("POSTSEASON TOURNAMENT SELECTION")
    print("="*60)
    print(f"\nNCAA Tournament: {len(ncaa_teams)} teams")
    print(f"NIT Tournament: {len(nit_teams)} teams")

    input("\nPress Enter to start NCAA Tournament...")

    # Run NCAA Tournament
    ncaa = NCAABracket(ncaa_teams, game_engine)
    ncaa_champion = ncaa.simulate()

    input("\nPress Enter to start NIT Tournament...")

    # Run NIT Tournament
    nit = NITBracket(nit_teams, game_engine)
    nit_champion = nit.simulate()

    return {
        'ncaa_champion': ncaa_champion,
        'nit_champion': nit_champion
    }


def run_conference_tournaments(all_teams: List[Team], game_engine: GameEngine) -> dict:
    """Run all conference tournaments and return champions"""
    from teams_data import CONFERENCES

    conference_champions = {}

    # Group teams by conference
    conferences_teams = {}
    for team in all_teams:
        if team.conference not in conferences_teams:
            conferences_teams[team.conference] = []
        conferences_teams[team.conference].append(team)

    # Run tournament for each conference
    for conference_name in sorted(CONFERENCES.keys()):
        if conference_name not in conferences_teams:
            continue

        conf_teams = conferences_teams[conference_name]
        if len(conf_teams) < 4:  # Need at least 4 teams for a tournament
            # Just take the regular season champion
            conf_teams.sort(key=lambda t: (t.conference_wins, t.wins), reverse=True)
            conference_champions[conference_name] = conf_teams[0]
            continue

        # Run conference tournament
        tournament = ConferenceTournament(conference_name, conf_teams, game_engine)
        champion = tournament.simulate()
        conference_champions[conference_name] = champion

        print(f"\n{conference_name} Champion: {champion.name} ({champion.conference_wins}-{champion.conference_losses} conf, {champion.wins}-{champion.losses} overall)")

    return conference_champions

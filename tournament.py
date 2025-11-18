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

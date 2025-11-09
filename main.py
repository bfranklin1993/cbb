"""
College Basketball Manager - Main Game
"""

import os
from typing import Optional
from models import Team
from teams_data import create_all_teams, get_team_by_name, CONFERENCES
from season import Season
from tournament import run_postseason
from game_engine import GameEngine
from constants import OFFENSIVE_SYSTEMS, DEFENSIVE_SYSTEMS
from recruiting import RecruitingClass, recruit_players_auto


class Game:
    """Main game controller"""

    def __init__(self):
        self.all_teams = create_all_teams()
        self.player_team: Optional[Team] = None
        self.current_season: Optional[Season] = None
        self.current_year = 2024
        self.game_engine = GameEngine()

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def display_title(self):
        """Display game title"""
        print("\n" + "="*60)
        print("COLLEGE BASKETBALL MANAGER".center(60))
        print("="*60)

    def select_team(self):
        """Let player select their team"""
        print("\n" + "="*60)
        print("SELECT YOUR TEAM")
        print("="*60)

        print("\nAvailable Conferences:")
        for i, conf in enumerate(CONFERENCES.keys(), 1):
            print(f"{i}. {conf}")

        while True:
            try:
                conf_choice = int(input("\nSelect conference (number): ")) - 1
                conference_name = list(CONFERENCES.keys())[conf_choice]
                break
            except (ValueError, IndexError):
                print("Invalid selection. Try again.")

        print(f"\n{conference_name} Teams:")
        teams_in_conf = CONFERENCES[conference_name]
        for i, team_name in enumerate(teams_in_conf, 1):
            print(f"{i}. {team_name}")

        while True:
            try:
                team_choice = int(input("\nSelect team (number): ")) - 1
                team_name = teams_in_conf[team_choice]
                self.player_team = get_team_by_name(self.all_teams, team_name)
                break
            except (ValueError, IndexError):
                print("Invalid selection. Try again.")

        print(f"\nYou selected: {self.player_team.name}")
        print(f"Conference: {self.player_team.conference}")
        print(f"Team Rating: {self.player_team.get_team_rating():.1f}")

        input("\nPress Enter to continue...")

    def view_roster(self):
        """View and manage team roster"""
        print("\n" + "="*60)
        print(f"{self.player_team.name} ROSTER")
        print("="*60)

        print(f"\n{'Name':<20}{'Pos':<5}{'Yr':<5}{'OVR':<6}{'SHT':<5}{'DEF':<5}{'ATH':<5}{'IQ':<5}{'REB':<5}")
        print("-" * 60)

        for player in sorted(self.player_team.roster, key=lambda p: p.overall_rating(), reverse=True):
            year_str = ["Fr", "So", "Jr", "Sr"][player.year - 1]
            print(f"{player.name:<20}{player.position:<5}{year_str:<5}"
                  f"{player.overall_rating():<6.1f}"
                  f"{player.shooting:<5.1f}{player.defense:<5.1f}"
                  f"{player.athleticism:<5.1f}{player.basketball_iq:<5.1f}"
                  f"{player.rebounding:<5.1f}")

        input("\nPress Enter to continue...")

    def view_player_stats(self):
        """View detailed player statistics"""
        print("\n" + "="*60)
        print(f"{self.player_team.name} PLAYER STATISTICS")
        print("="*60)

        print(f"\n{'Name':<20}{'GP':<5}{'PPG':<6}{'RPG':<6}{'APG':<6}{'SPG':<6}{'BPG':<6}")
        print("-" * 60)

        for player in sorted(self.player_team.roster, key=lambda p: p.points, reverse=True):
            stats = player.get_stats_per_game()
            if player.games_played > 0:
                print(f"{player.name:<20}{player.games_played:<5}"
                      f"{stats['PPG']:<6.1f}{stats['RPG']:<6.1f}"
                      f"{stats['APG']:<6.1f}{stats['SPG']:<6.1f}{stats['BPG']:<6.1f}")

        input("\nPress Enter to continue...")

    def view_team_schedule(self):
        """View team's game results and schedule"""
        print("\n" + "="*60)
        print(f"{self.player_team.name} - SEASON RESULTS")
        print("="*60)
        print(f"\nRecord: {self.player_team.wins}-{self.player_team.losses}")
        print(f"Games Played: {self.player_team.games_played}")

        if len(self.player_team.results) > 0:
            print("\n" + "-"*60)
            print("GAME RESULTS:")
            print("-"*60)

            for i, result in enumerate(self.player_team.results, 1):
                is_home = result["home_team"] == self.player_team.name
                opponent = result["away_team"] if is_home else result["home_team"]
                team_score = result["home_score"] if is_home else result["away_score"]
                opp_score = result["away_score"] if is_home else result["home_score"]
                location = "vs" if is_home else "@"

                # Determine result
                if team_score > opp_score:
                    outcome = "W"
                else:
                    outcome = "L"

                conf_marker = "*" if result["is_conference"] else " "

                print(f"Game {i:2}: {outcome} {team_score:3}-{opp_score:3} {location} {opponent:25} {conf_marker}")
        else:
            print("\nNo games played yet.")

        input("\nPress Enter to continue...")

    def set_game_plan(self):
        """Set offensive and defensive systems"""
        print("\n" + "="*60)
        print("SET GAME PLAN")
        print("="*60)

        print(f"\nCurrent Offensive System: {self.player_team.offensive_system}")
        print(f"Current Defensive System: {self.player_team.defensive_system}")

        # Offensive system
        print("\nOffensive Systems:")
        for i, system in enumerate(OFFENSIVE_SYSTEMS, 1):
            print(f"{i}. {system}")

        while True:
            try:
                choice = int(input("\nSelect offensive system (0 to keep current): "))
                if choice == 0:
                    break
                self.player_team.offensive_system = OFFENSIVE_SYSTEMS[choice - 1]
                print(f"Offensive system set to: {self.player_team.offensive_system}")
                break
            except (ValueError, IndexError):
                print("Invalid selection. Try again.")

        # Defensive system
        print("\nDefensive Systems:")
        for i, system in enumerate(DEFENSIVE_SYSTEMS, 1):
            print(f"{i}. {system}")

        while True:
            try:
                choice = int(input("\nSelect defensive system (0 to keep current): "))
                if choice == 0:
                    break
                self.player_team.defensive_system = DEFENSIVE_SYSTEMS[choice - 1]
                print(f"Defensive system set to: {self.player_team.defensive_system}")
                break
            except (ValueError, IndexError):
                print("Invalid selection. Try again.")

        input("\nPress Enter to continue...")

    def start_season(self):
        """Start a new season"""
        self.current_season = Season(self.all_teams, self.current_year)
        self.current_season.generate_schedule()

        print("\n" + "="*60)
        print(f"{self.current_year} SEASON STARTED")
        print("="*60)
        print(f"\nYour Team: {self.player_team.name}")
        print(f"Conference: {self.player_team.conference}")
        print(f"Games Scheduled: ~30")

        input("\nPress Enter to continue...")

    def season_menu(self):
        """Season management menu"""
        while self.current_season.current_week < self.current_season.total_weeks:
            print("\n" + "="*60)
            print(f"{self.current_year} SEASON - WEEK {self.current_season.current_week + 1}")
            print("="*60)
            print(f"\nYour Record: {self.player_team.wins}-{self.player_team.losses}")
            print(f"Conference: {self.player_team.conference_wins}-{self.player_team.conference_losses}")

            print("\n1. Simulate Week")
            print("2. View Roster")
            print("3. View Player Stats")
            print("4. View Team Schedule/Results")
            print("5. Adjust Game Plan")
            print("6. View Standings")
            print("7. View Conference Standings")
            print("8. Simulate Rest of Season")

            choice = input("\nSelect option: ")

            if choice == "1":
                results = self.current_season.simulate_week()
                self.current_season.display_scoreboard(results)
                input("\nPress Enter to continue...")

            elif choice == "2":
                self.view_roster()

            elif choice == "3":
                self.view_player_stats()

            elif choice == "4":
                self.view_team_schedule()

            elif choice == "5":
                self.set_game_plan()

            elif choice == "6":
                self.current_season.display_standings(50)
                input("\nPress Enter to continue...")

            elif choice == "7":
                standings = self.current_season.get_conference_standings(self.player_team.conference)
                print("\n" + "="*60)
                print(f"{self.player_team.conference} STANDINGS")
                print("="*60)
                print(f"\n{'Team':<25}{'Overall':<12}{'Conference':<12}")
                print("-" * 60)
                for team in standings:
                    overall = f"{team.wins}-{team.losses}"
                    conf = f"{team.conference_wins}-{team.conference_losses}"
                    print(f"{team.name:<25}{overall:<12}{conf:<12}")
                input("\nPress Enter to continue...")

            elif choice == "8":
                print("\nSimulating rest of season...")
                self.current_season.simulate_full_season()
                print("Regular season complete!")
                input("\nPress Enter to continue...")
                break

        # Season complete
        print("\n" + "="*60)
        print("REGULAR SEASON COMPLETE")
        print("="*60)
        print(f"\nFinal Record: {self.player_team.wins}-{self.player_team.losses}")
        print(f"Conference: {self.player_team.conference_wins}-{self.player_team.conference_losses}")

        self.current_season.display_standings(25)

        input("\nPress Enter to continue to postseason...")

        # Run tournaments
        ncaa_champ, nit_champ = run_postseason(self.all_teams, self.game_engine)

        # End of season
        print("\n" + "="*60)
        print(f"{self.current_year} SEASON COMPLETE")
        print("="*60)
        print(f"\nYour Final Record: {self.player_team.wins}-{self.player_team.losses}")
        print(f"NCAA Champion: {ncaa_champ.name}")
        print(f"NIT Champion: {nit_champ.name}")

        input("\nPress Enter to continue to off-season...")

        # Advance to next season
        self.current_year += 1
        print("\n" + "="*60)
        print("OFF-SEASON")
        print("="*60)
        print("\nPlayer Development and Graduation...")

        # Check graduating seniors
        graduating_count = sum(1 for p in self.player_team.roster if p.year >= 4)

        self.current_season.advance_players()

        print(f"\n{graduating_count} seniors graduated from your team.")
        print("Players developed and improved their skills!")

        input("\nPress Enter to start recruiting...")

        # Recruiting phase
        self.recruiting_phase()

        # Reset records for all teams
        for team in self.all_teams:
            team.wins = 0
            team.losses = 0
            team.conference_wins = 0
            team.conference_losses = 0
            team.games_played = 0
            team.results = []

        print("\nOff-season complete!")
        input("\nPress Enter to continue...")

    def recruiting_phase(self):
        """Handle recruiting for the off-season"""
        print("\n" + "="*60)
        print("RECRUITING")
        print("="*60)

        # Calculate open scholarships
        open_spots = 12 - len(self.player_team.roster)
        print(f"\nOpen Scholarships: {open_spots}")

        if open_spots == 0:
            print("Your roster is full!")
            input("\nPress Enter to continue...")
            return

        # Create recruiting class
        recruiting_class = RecruitingClass(self.current_year)

        recruited_count = 0

        while recruited_count < open_spots:
            print("\n" + "="*60)
            print(f"RECRUITING - {open_spots - recruited_count} spots remaining")
            print("="*60)

            print("\n1. View Available Recruits (All)")
            print("2. View Available Recruits (by Position)")
            print("3. View Your Commits")
            print("4. Finish Recruiting (Auto-fill remaining spots)")

            choice = input("\nSelect option: ")

            if choice == "1":
                self.view_recruits(recruiting_class, None)

            elif choice == "2":
                print("\nSelect position:")
                print("1. PG  2. SG  3. SF  4. PF  5. C")
                pos_choice = input("Select: ")
                positions = {" 1": "PG", "2": "SG", "3": "SF", "4": "PF", "5": "C"}
                position = positions.get(pos_choice, None)

                if position:
                    self.view_recruits(recruiting_class, position)

            elif choice == "3":
                self.view_commits(recruiting_class)

            elif choice == "4":
                # Auto-fill remaining spots
                remaining = open_spots - recruited_count
                print(f"\nAuto-recruiting {remaining} players...")

                recruited = recruit_players_auto(self.player_team, recruiting_class, remaining)
                recruited_count += len(recruited)

                for recruit in recruited:
                    print(f"Recruited: {recruit.name} ({recruit.position}) - Potential: {recruit.potential}/10")

                input("\nPress Enter to continue...")
                break

            # Check if we filled all spots through manual recruiting
            current_recruited = sum(1 for r in recruiting_class.recruits
                                  if r.committed and r.committed_to == self.player_team.name)
            recruited_count = current_recruited

        # Add all committed recruits to roster
        for recruit in recruiting_class.recruits:
            if recruit.committed and recruit.committed_to == self.player_team.name:
                player = recruit.to_player()
                if player not in self.player_team.roster:
                    self.player_team.roster.append(player)

        # Other teams auto-recruit
        print("\nOther teams are recruiting...")
        for team in self.all_teams:
            if team != self.player_team:
                open_spots_team = 12 - len(team.roster)
                if open_spots_team > 0:
                    recruit_players_auto(team, recruiting_class, open_spots_team)

        print("Recruiting complete!")

    def view_recruits(self, recruiting_class: RecruitingClass, position: str = None):
        """View available recruits"""
        recruits = recruiting_class.get_available_recruits(position)

        print("\n" + "="*60)
        title = f"AVAILABLE RECRUITS" + (f" - {position}" if position else "")
        print(title)
        print("="*60)
        print(f"\n{'#':<4}{'Name':<20}{'Pos':<5}{'Pot':<5}{'Int':<5}{'OVR':<6}{'SHT':<5}{'DEF':<5}{'ATH':<5}")
        print("-" * 60)

        for i, recruit in enumerate(recruits[:30], 1):  # Show top 30
            print(f"{i:<4}{recruit.name:<20}{recruit.position:<5}"
                  f"{recruit.potential:<5}{recruit.interest:<5}"
                  f"{recruit.overall_rating():<6.1f}"
                  f"{recruit.shooting:<5.1f}{recruit.defense:<5.1f}{recruit.athleticism:<5.1f}")

        # Option to recruit
        choice = input("\nEnter recruit # to attempt recruitment (0 to go back): ")

        try:
            choice_num = int(choice)
            if choice_num > 0 and choice_num <= len(recruits[:30]):
                recruit = recruits[choice_num - 1]
                self.attempt_recruit(recruit, recruiting_class)
        except ValueError:
            pass

    def attempt_recruit(self, recruit, recruiting_class: RecruitingClass):
        """Attempt to recruit a player"""
        print(f"\n Attempting to recruit {recruit.name}...")
        print(f"Position: {recruit.position}, Potential: {recruit.potential}/10")
        print(f"Interest Level: {recruit.interest}%")

        confirm = input("\nCommit a scholarship? (y/n): ")

        if confirm.lower() == 'y':
            success = recruiting_class.recruit_player(recruit, self.player_team)

            if success:
                print(f"\n*** SUCCESS! {recruit.name} commits to {self.player_team.name}! ***")
                player = recruit.to_player()
                self.player_team.roster.append(player)
            else:
                print(f"\n{recruit.name} declined your offer.")
                print(f"Interest decreased to {recruit.interest}%")

            input("\nPress Enter to continue...")

    def view_commits(self, recruiting_class: RecruitingClass):
        """View current recruiting commits"""
        commits = [r for r in recruiting_class.recruits
                  if r.committed and r.committed_to == self.player_team.name]

        print("\n" + "="*60)
        print(f"YOUR COMMITS ({len(commits)})")
        print("="*60)

        if len(commits) == 0:
            print("\nNo commits yet.")
        else:
            print(f"\n{'Name':<20}{'Pos':<5}{'Pot':<5}{'OVR':<6}")
            print("-" * 40)
            for recruit in commits:
                print(f"{recruit.name:<20}{recruit.position:<5}"
                      f"{recruit.potential:<5}{recruit.overall_rating():<6.1f}")

        input("\nPress Enter to continue...")

    def main_menu(self):
        """Main game menu"""
        while True:
            self.display_title()
            print(f"\nCurrent Season: {self.current_year}")
            if self.player_team:
                print(f"Your Team: {self.player_team.name}")

            print("\n1. Start New Career")
            print("2. Continue Season")
            print("3. View Team")
            print("4. Quit")

            choice = input("\nSelect option: ")

            if choice == "1":
                self.select_team()
                self.set_game_plan()
                self.start_season()
                self.season_menu()

            elif choice == "2":
                if self.current_season:
                    self.season_menu()
                else:
                    print("\nNo active season. Start a new career first.")
                    input("Press Enter to continue...")

            elif choice == "3":
                if self.player_team:
                    self.view_roster()
                else:
                    print("\nNo team selected. Start a new career first.")
                    input("Press Enter to continue...")

            elif choice == "4":
                print("\nThanks for playing!")
                break


def main():
    """Entry point"""
    game = Game()
    game.main_menu()


if __name__ == "__main__":
    main()

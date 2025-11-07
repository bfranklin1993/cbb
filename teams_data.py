"""
Real college basketball teams organized by conference
"""

from models import Team

# Major conferences and their teams
CONFERENCES = {
    "ACC": [
        "Duke", "North Carolina", "Virginia", "Miami", "Clemson",
        "Florida State", "NC State", "Syracuse", "Pittsburgh", "Louisville",
        "Virginia Tech", "Georgia Tech", "Wake Forest", "Boston College", "Notre Dame"
    ],
    "Big Ten": [
        "Michigan State", "Michigan", "Illinois", "Purdue", "Wisconsin",
        "Ohio State", "Indiana", "Iowa", "Maryland", "Penn State",
        "Rutgers", "Minnesota", "Northwestern", "Nebraska"
    ],
    "Big 12": [
        "Kansas", "Baylor", "Texas Tech", "Texas", "Oklahoma State",
        "West Virginia", "TCU", "Kansas State", "Iowa State", "Oklahoma"
    ],
    "SEC": [
        "Kentucky", "Tennessee", "Auburn", "Alabama", "Arkansas",
        "Florida", "LSU", "Mississippi State", "Ole Miss", "Texas A&M",
        "Missouri", "South Carolina", "Georgia", "Vanderbilt"
    ],
    "Pac-12": [
        "Arizona", "UCLA", "USC", "Oregon", "Colorado",
        "Washington", "Stanford", "Utah", "Arizona State", "Oregon State",
        "California", "Washington State"
    ],
    "Big East": [
        "Villanova", "UConn", "Creighton", "Xavier", "Marquette",
        "Providence", "Butler", "Seton Hall", "St. John's", "Georgetown", "DePaul"
    ],
    "American": [
        "Houston", "Memphis", "Cincinnati", "SMU", "UCF",
        "Temple", "Wichita State", "Tulsa", "ECU", "Tulane", "USF", "South Florida"
    ],
    "Mountain West": [
        "San Diego State", "Nevada", "New Mexico", "Utah State", "Boise State",
        "Colorado State", "Wyoming", "UNLV", "Fresno State", "Air Force"
    ],
    "Atlantic 10": [
        "VCU", "Dayton", "Richmond", "St. Louis", "Davidson",
        "Rhode Island", "Saint Joseph's", "George Mason", "UMass", "Fordham"
    ],
    "WCC": [
        "Gonzaga", "Saint Mary's", "BYU", "San Francisco", "Santa Clara",
        "Loyola Marymount", "Pepperdine", "Pacific", "Portland"
    ]
}


def create_all_teams():
    """Create all college basketball teams"""
    all_teams = []

    for conference, team_names in CONFERENCES.items():
        for team_name in team_names:
            team = Team(team_name, conference)
            all_teams.append(team)

    return all_teams


def get_team_by_name(teams, name: str):
    """Find a team by name"""
    for team in teams:
        if team.name.lower() == name.lower():
            return team
    return None


def get_conference_teams(teams, conference: str):
    """Get all teams in a conference"""
    return [t for t in teams if t.conference == conference]

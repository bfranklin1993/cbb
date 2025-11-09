"""
Real college basketball teams organized by conference
"""

from models import Team

# All D1 conferences and their teams (~360 teams total)
CONFERENCES = {
    # Power Conferences
    "ACC": [
        "Duke", "North Carolina", "Virginia", "Miami", "Clemson",
        "Florida State", "NC State", "Syracuse", "Pittsburgh", "Louisville",
        "Virginia Tech", "Georgia Tech", "Wake Forest", "Boston College", "Notre Dame",
        "California", "Stanford", "SMU"
    ],
    "Big Ten": [
        "Michigan State", "Michigan", "Illinois", "Purdue", "Wisconsin",
        "Ohio State", "Indiana", "Iowa", "Maryland", "Penn State",
        "Rutgers", "Minnesota", "Northwestern", "Nebraska", "USC",
        "UCLA", "Oregon", "Washington"
    ],
    "Big 12": [
        "Kansas", "Baylor", "Texas Tech", "Texas", "Oklahoma State",
        "West Virginia", "TCU", "Kansas State", "Iowa State", "Cincinnati",
        "Houston", "UCF", "BYU", "Arizona", "Arizona State", "Colorado", "Utah"
    ],
    "SEC": [
        "Kentucky", "Tennessee", "Auburn", "Alabama", "Arkansas",
        "Florida", "LSU", "Mississippi State", "Ole Miss", "Texas A&M",
        "Missouri", "South Carolina", "Georgia", "Vanderbilt", "Oklahoma", "Texas"
    ],
    "Big East": [
        "Villanova", "UConn", "Creighton", "Xavier", "Marquette",
        "Providence", "Butler", "Seton Hall", "St. John's", "Georgetown", "DePaul"
    ],

    # High Mid-Major Conferences
    "American": [
        "Memphis", "Temple", "Wichita State", "Tulsa", "Tulane",
        "East Carolina", "USF", "UAB", "North Texas", "UTSA",
        "Rice", "Charlotte", "Florida Atlantic", "Army"
    ],
    "Mountain West": [
        "San Diego State", "Nevada", "New Mexico", "Utah State", "Boise State",
        "Colorado State", "Wyoming", "UNLV", "Fresno State", "Air Force",
        "San Jose State", "Hawaii"
    ],
    "Atlantic 10": [
        "VCU", "Dayton", "Richmond", "St. Louis", "Davidson",
        "Rhode Island", "Saint Joseph's", "George Mason", "UMass", "Fordham",
        "La Salle", "Duquesne", "Saint Louis", "Loyola Chicago", "George Washington"
    ],
    "WCC": [
        "Gonzaga", "Saint Mary's", "San Francisco", "Santa Clara",
        "Loyola Marymount", "Pepperdine", "Pacific", "Portland", "San Diego"
    ],

    # Mid-Major Conferences
    "Conference USA": [
        "Louisiana Tech", "UTEP", "Middle Tennessee", "Western Kentucky",
        "Jacksonville State", "Liberty", "New Mexico State", "Sam Houston State",
        "FIU", "Kennesaw State"
    ],
    "MAC": [
        "Toledo", "Akron", "Kent State", "Ohio", "Buffalo",
        "Bowling Green", "Miami (OH)", "Ball State", "Central Michigan",
        "Eastern Michigan", "Western Michigan", "Northern Illinois"
    ],
    "Sun Belt": [
        "Louisiana", "Texas State", "Arkansas State", "Troy",
        "South Alabama", "Georgia State", "Georgia Southern", "Coastal Carolina",
        "App State", "UL Monroe", "Old Dominion", "James Madison", "Marshall", "Southern Miss"
    ],
    "Missouri Valley": [
        "Drake", "Bradley", "Northern Iowa", "Missouri State",
        "Indiana State", "Southern Illinois", "Illinois State", "Belmont",
        "UIC", "Valparaiso", "Murray State"
    ],
    "Ivy League": [
        "Princeton", "Yale", "Harvard", "Penn",
        "Cornell", "Columbia", "Brown", "Dartmouth"
    ],
    "Colonial": [
        "Charleston", "Hofstra", "Delaware", "Drexel",
        "Towson", "UNC Wilmington", "Northeastern", "William & Mary",
        "Elon", "Hampton", "Monmouth", "Stony Brook", "Campbell"
    ],

    # Low-Mid Major Conferences
    "Horizon": [
        "Wright State", "Northern Kentucky", "Cleveland State", "Milwaukee",
        "Oakland", "Youngstown State", "Green Bay", "Robert Morris",
        "Detroit Mercy", "IUPUI", "Purdue Fort Wayne"
    ],
    "WAC": [
        "Grand Canyon", "Seattle U", "UT Arlington", "Utah Tech",
        "Abilene Christian", "California Baptist", "Tarleton State",
        "Southern Utah", "UT Rio Grande Valley"
    ],
    "Big Sky": [
        "Montana", "Montana State", "Weber State", "Northern Colorado",
        "Idaho State", "Eastern Washington", "Portland State",
        "Sacramento State", "Northern Arizona", "Idaho"
    ],
    "Big South": [
        "High Point", "Winthrop", "Radford", "Gardner-Webb",
        "Longwood", "Charleston Southern", "UNC Asheville", "Presbyterian"
    ],
    "MAAC": [
        "Iona", "Quinnipiac", "Siena", "Rider",
        "Marist", "Fairfield", "Manhattan", "Niagara",
        "Canisius", "St. Peter's", "Mount St. Mary's", "Sacred Heart"
    ],
    "MEAC": [
        "Norfolk State", "North Carolina Central", "Howard",
        "Coppin State", "Morgan State", "Delaware State",
        "Maryland Eastern Shore", "South Carolina State"
    ],
    "NEC": [
        "Merrimack", "Fairleigh Dickinson", "Wagner", "Central Connecticut",
        "LIU", "St. Francis Brooklyn", "Sacred Heart", "Mount St. Mary's"
    ],
    "OVC": [
        "Morehead State", "Eastern Illinois", "Tennessee Tech",
        "SIU Edwardsville", "UT Martin", "Southeast Missouri",
        "Tennessee State", "Eastern Kentucky", "Lindenwood", "Little Rock"
    ],
    "Patriot": [
        "Colgate", "Bucknell", "Lehigh", "Boston University",
        "American", "Navy", "Holy Cross", "Lafayette", "Army",
        "Loyola Maryland"
    ],
    "Southern": [
        "Furman", "Samford", "UNC Greensboro", "Wofford",
        "Chattanooga", "ETSU", "Mercer", "Western Carolina",
        "The Citadel", "VMI"
    ],
    "Southland": [
        "McNeese", "Nicholls", "Northwestern State", "Lamar",
        "Incarnate Word", "Houston Christian", "Texas A&M Commerce",
        "New Orleans", "SE Louisiana"
    ],
    "SWAC": [
        "Texas Southern", "Prairie View A&M", "Southern", "Grambling",
        "Jackson State", "Alcorn State", "Alabama State", "Alabama A&M",
        "Arkansas Pine Bluff", "Mississippi Valley State", "Florida A&M", "Bethune-Cookman"
    ],
    "Summit": [
        "South Dakota State", "North Dakota State", "Oral Roberts",
        "South Dakota", "North Dakota", "Denver", "Omaha",
        "Kansas City", "Western Illinois", "St. Thomas"
    ],
    "America East": [
        "Vermont", "UMBC", "UMass Lowell", "Albany",
        "Binghamton", "Maine", "New Hampshire", "UNH",
        "Bryant", "NJIT"
    ],
    "Atlantic Sun": [
        "Liberty", "Lipscomb", "Jacksonville", "North Florida",
        "FGCU", "Stetson", "Kennesaw State", "Bellarmine",
        "Eastern Kentucky", "Queens", "Central Arkansas", "Austin Peay"
    ],
    "Big West": [
        "UC Irvine", "UC Santa Barbara", "UC Davis", "UC San Diego",
        "UC Riverside", "Long Beach State", "Cal State Fullerton",
        "Cal State Northridge", "Cal Poly", "Hawaii", "Cal State Bakersfield"
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

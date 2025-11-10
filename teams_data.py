"""
Real college basketball teams organized by conference
"""

from models import Team

# Team nicknames mapping
TEAM_NICKNAMES = {
    # ACC
    "Duke": "Blue Devils", "North Carolina": "Tar Heels", "Virginia": "Cavaliers",
    "Miami": "Hurricanes", "Clemson": "Tigers", "Florida State": "Seminoles",
    "NC State": "Wolfpack", "Syracuse": "Orange", "Pittsburgh": "Panthers",
    "Louisville": "Cardinals", "Virginia Tech": "Hokies", "Georgia Tech": "Yellow Jackets",
    "Wake Forest": "Demon Deacons", "Boston College": "Eagles", "Notre Dame": "Fighting Irish",
    "California": "Golden Bears", "Stanford": "Cardinal", "SMU": "Mustangs",

    # Big Ten
    "Michigan State": "Spartans", "Michigan": "Wolverines", "Illinois": "Fighting Illini",
    "Purdue": "Boilermakers", "Wisconsin": "Badgers", "Ohio State": "Buckeyes",
    "Indiana": "Hoosiers", "Iowa": "Hawkeyes", "Maryland": "Terrapins",
    "Penn State": "Nittany Lions", "Rutgers": "Scarlet Knights", "Minnesota": "Golden Gophers",
    "Northwestern": "Wildcats", "Nebraska": "Cornhuskers", "USC": "Trojans",
    "UCLA": "Bruins", "Oregon": "Ducks", "Washington": "Huskies",

    # Big 12
    "Kansas": "Jayhawks", "Baylor": "Bears", "Texas Tech": "Red Raiders",
    "Texas": "Longhorns", "Oklahoma State": "Cowboys", "West Virginia": "Mountaineers",
    "TCU": "Horned Frogs", "Kansas State": "Wildcats", "Iowa State": "Cyclones",
    "Cincinnati": "Bearcats", "Houston": "Cougars", "UCF": "Knights",
    "BYU": "Cougars", "Arizona": "Wildcats", "Arizona State": "Sun Devils",
    "Colorado": "Buffaloes", "Utah": "Utes",

    # SEC
    "Kentucky": "Wildcats", "Tennessee": "Volunteers", "Auburn": "Tigers",
    "Alabama": "Crimson Tide", "Arkansas": "Razorbacks", "Florida": "Gators",
    "LSU": "Tigers", "Mississippi State": "Bulldogs", "Ole Miss": "Rebels",
    "Texas A&M": "Aggies", "Missouri": "Tigers", "South Carolina": "Gamecocks",
    "Georgia": "Bulldogs", "Vanderbilt": "Commodores", "Oklahoma": "Sooners",

    # Big East
    "Villanova": "Wildcats", "UConn": "Huskies", "Creighton": "Bluejays",
    "Xavier": "Musketeers", "Marquette": "Golden Eagles", "Providence": "Friars",
    "Butler": "Bulldogs", "Seton Hall": "Pirates", "St. John's": "Red Storm",
    "Georgetown": "Hoyas", "DePaul": "Blue Demons",

    # American
    "Memphis": "Tigers", "Temple": "Owls", "Wichita State": "Shockers",
    "Tulsa": "Golden Hurricane", "Tulane": "Green Wave", "East Carolina": "Pirates",
    "USF": "Bulls", "UAB": "Blazers", "North Texas": "Mean Green",
    "UTSA": "Roadrunners", "Rice": "Owls", "Charlotte": "49ers",
    "Florida Atlantic": "Owls", "Army": "Black Knights",

    # Mountain West
    "San Diego State": "Aztecs", "Nevada": "Wolf Pack", "New Mexico": "Lobos",
    "Utah State": "Aggies", "Boise State": "Broncos", "Colorado State": "Rams",
    "Wyoming": "Cowboys", "UNLV": "Rebels", "Fresno State": "Bulldogs",
    "Air Force": "Falcons", "San Jose State": "Spartans", "Hawaii": "Rainbow Warriors",

    # Atlantic 10
    "VCU": "Rams", "Dayton": "Flyers", "Richmond": "Spiders",
    "St. Louis": "Billikens", "Davidson": "Wildcats", "Rhode Island": "Rams",
    "Saint Joseph's": "Hawks", "George Mason": "Patriots", "UMass": "Minutemen",
    "Fordham": "Rams", "La Salle": "Explorers", "Duquesne": "Dukes",
    "Saint Louis": "Billikens", "Loyola Chicago": "Ramblers", "George Washington": "Colonials",

    # WCC
    "Gonzaga": "Bulldogs", "Saint Mary's": "Gaels", "San Francisco": "Dons",
    "Santa Clara": "Broncos", "Loyola Marymount": "Lions", "Pepperdine": "Waves",
    "Pacific": "Tigers", "Portland": "Pilots", "San Diego": "Toreros",

    # Conference USA
    "Louisiana Tech": "Bulldogs", "UTEP": "Miners", "Middle Tennessee": "Blue Raiders",
    "Western Kentucky": "Hilltoppers", "Jacksonville State": "Gamecocks", "Liberty": "Flames",
    "New Mexico State": "Aggies", "Sam Houston State": "Bearkats", "FIU": "Panthers",
    "Kennesaw State": "Owls",

    # MAC
    "Toledo": "Rockets", "Akron": "Zips", "Kent State": "Golden Flashes",
    "Ohio": "Bobcats", "Buffalo": "Bulls", "Bowling Green": "Falcons",
    "Miami (OH)": "RedHawks", "Ball State": "Cardinals", "Central Michigan": "Chippewas",
    "Eastern Michigan": "Eagles", "Western Michigan": "Broncos", "Northern Illinois": "Huskies",

    # Sun Belt
    "Louisiana": "Ragin' Cajuns", "Texas State": "Bobcats", "Arkansas State": "Red Wolves",
    "Troy": "Trojans", "South Alabama": "Jaguars", "Georgia State": "Panthers",
    "Georgia Southern": "Eagles", "Coastal Carolina": "Chanticleers", "App State": "Mountaineers",
    "UL Monroe": "Warhawks", "Old Dominion": "Monarchs", "James Madison": "Dukes",
    "Marshall": "Thundering Herd", "Southern Miss": "Golden Eagles",

    # Missouri Valley
    "Drake": "Bulldogs", "Bradley": "Braves", "Northern Iowa": "Panthers",
    "Missouri State": "Bears", "Indiana State": "Sycamores", "Southern Illinois": "Salukis",
    "Illinois State": "Redbirds", "Belmont": "Bruins", "UIC": "Flames",
    "Valparaiso": "Beacons", "Murray State": "Racers",

    # Ivy League
    "Princeton": "Tigers", "Yale": "Bulldogs", "Harvard": "Crimson",
    "Penn": "Quakers", "Cornell": "Big Red", "Columbia": "Lions",
    "Brown": "Bears", "Dartmouth": "Big Green",

    # Colonial
    "Charleston": "Cougars", "Hofstra": "Pride", "Delaware": "Blue Hens",
    "Drexel": "Dragons", "Towson": "Tigers", "UNC Wilmington": "Seahawks",
    "Northeastern": "Huskies", "William & Mary": "Tribe", "Elon": "Phoenix",
    "Hampton": "Pirates", "Monmouth": "Hawks", "Stony Brook": "Seawolves",
    "Campbell": "Fighting Camels",
}

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

# Team prestige levels - determines base roster quality
# ELITE: 8.0-9.0, HIGH: 7.0-8.0, UPPER_MID: 6.0-7.0, MID: 5.0-6.0, LOW_MID: 4.0-5.0, LOW: 3.0-4.0
TEAM_PRESTIGE = {
    # ELITE Programs (Blue Bloods and Top Programs)
    "Duke": "ELITE", "North Carolina": "ELITE", "Kansas": "ELITE", "Kentucky": "ELITE",
    "UConn": "ELITE", "Villanova": "ELITE", "Gonzaga": "ELITE",

    # HIGH Programs (Perennial contenders)
    "Michigan State": "HIGH", "Purdue": "HIGH", "Arizona": "HIGH", "Houston": "HIGH",
    "UCLA": "HIGH", "Baylor": "HIGH", "Tennessee": "HIGH", "Auburn": "HIGH",
    "Creighton": "HIGH", "Texas": "HIGH", "Alabama": "HIGH", "Illinois": "HIGH",
    "San Diego State": "HIGH", "Marquette": "HIGH", "Xavier": "HIGH", "Wisconsin": "HIGH",
    "Virginia": "HIGH", "Michigan": "HIGH", "Florida": "HIGH",

    # UPPER_MID Programs (Strong programs, occasional contenders)
    "Texas Tech": "UPPER_MID", "Arkansas": "UPPER_MID", "Iowa": "UPPER_MID",
    "USC": "UPPER_MID", "Ohio State": "UPPER_MID", "Indiana": "UPPER_MID",
    "Miami": "UPPER_MID", "Florida State": "UPPER_MID", "NC State": "UPPER_MID",
    "Syracuse": "UPPER_MID", "Maryland": "UPPER_MID", "Iowa State": "UPPER_MID",
    "Oklahoma State": "UPPER_MID", "LSU": "UPPER_MID", "Saint Mary's": "UPPER_MID",
    "Memphis": "UPPER_MID", "Providence": "UPPER_MID", "Seton Hall": "UPPER_MID",
    "VCU": "UPPER_MID", "Dayton": "UPPER_MID", "Ole Miss": "UPPER_MID",
    "Texas A&M": "UPPER_MID", "West Virginia": "UPPER_MID", "TCU": "UPPER_MID",
    "Utah": "UPPER_MID", "Colorado": "UPPER_MID", "BYU": "UPPER_MID",
    "Oregon": "UPPER_MID", "Arizona State": "UPPER_MID", "Clemson": "UPPER_MID",

    # MID Programs (Decent programs, can make noise)
    "Pittsburgh": "MID", "Louisville": "MID", "Virginia Tech": "MID",
    "Wake Forest": "MID", "Georgia Tech": "MID", "Notre Dame": "MID",
    "Stanford": "MID", "California": "MID", "SMU": "MID",
    "Rutgers": "MID", "Penn State": "MID", "Minnesota": "MID",
    "Northwestern": "MID", "Nebraska": "MID", "Washington": "MID",
    "Kansas State": "MID", "Cincinnati": "MID", "UCF": "MID",
    "Mississippi State": "MID", "Missouri": "MID", "South Carolina": "MID",
    "Georgia": "MID", "Vanderbilt": "MID", "Oklahoma": "MID",
    "Butler": "MID", "St. John's": "MID", "Georgetown": "MID",
    "Wichita State": "MID", "Temple": "MID", "Nevada": "MID",
    "New Mexico": "MID", "Utah State": "MID", "Boise State": "MID",
    "Colorado State": "MID", "UNLV": "MID", "San Francisco": "MID",
    "Richmond": "MID", "St. Louis": "MID", "Davidson": "MID",
    "Drake": "MID", "Bradley": "MID", "Princeton": "MID",
    "Charleston": "MID", "Grand Canyon": "MID", "Boston College": "MID",
}

def get_team_prestige(team_name: str) -> str:
    """Get prestige level for a team, default to LOW_MID if not specified"""
    return TEAM_PRESTIGE.get(team_name, "LOW_MID")


def create_all_teams():
    """Create all college basketball teams with prestige levels"""
    all_teams = []

    for conference, team_names in CONFERENCES.items():
        for team_name in team_names:
            prestige = get_team_prestige(team_name)
            team = Team(team_name, conference, prestige=prestige)
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

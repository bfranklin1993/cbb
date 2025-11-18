# CLAUDE.md - AI Assistant Guide

This guide helps AI assistants understand the College Basketball Manager codebase structure, development workflows, and key conventions.

## Project Overview

College Basketball Manager is a text-based college basketball management and simulation game built with Python and Streamlit. Players manage real D1 college basketball teams through recruiting, game strategy, and season progression.

**Tech Stack:**
- Python 3.7+ (CI uses 3.10)
- Streamlit 1.28.0+ (Web UI)
- No database (in-memory state management)

**Interfaces:**
- `app.py` - Streamlit web UI (primary interface)
- `main.py` - CLI version (legacy/alternative)

## Codebase Architecture

### Module Overview

```
/home/user/cbb/
├── app.py              (1091 lines) - Streamlit web UI, session state management
├── main.py             (685 lines)  - CLI interface, career mode
├── models.py           (214 lines)  - Player & Team data models
├── season.py           (452 lines)  - Season management, scheduling, standings
├── game_engine.py      (249 lines)  - Game simulation algorithm
├── recruiting.py       (836 lines)  - Recruiting system (most complex module)
├── tournament.py       (196 lines)  - NCAA/NIT postseason tournaments
├── teams_data.py       (345 lines)  - Real D1 teams, conferences, prestige data
├── constants.py        (45 lines)   - Game configuration constants
└── requirements.txt    - Dependencies (only streamlit>=1.28.0)
```

### Architecture Pattern

```
Data Layer
  ├── models.py (Player, Team classes)
  ├── teams_data.py (360 D1 teams, 30+ conferences)
  └── constants.py (systems, positions, game parameters)
       ↓
Business Logic
  ├── season.py (scheduling, standings, advancement)
  ├── game_engine.py (simulation algorithm)
  ├── tournament.py (postseason)
  └── recruiting.py (recruit generation, AI recruiting)
       ↓
Presentation Layer
  ├── app.py (Streamlit web UI)
  └── main.py (CLI)
```

### Key Data Models

```python
# models.py
class Player:
    attributes: shooting, defense, athleticism, basketball_iq, rebounding (1-10)
    year: int (1=FR, 2=SO, 3=JR, 4=SR)
    stats: games_played, points, rebounds, assists, steals, blocks

class Team:
    roster: List[Player] (12 players)
    offensive_system: str (Motion, Princeton, Fast Break, etc.)
    defensive_system: str (Man-to-Man, Zone, Press, etc.)
    rotation: (starters[5], backups[5], bench[2])
    prestige: str (ELITE/HIGH/UPPER_MID/MID/LOW_MID/LOW)
    results: List[dict] (game outcomes)

# season.py
class Season:
    schedule: List[List[Tuple]] (18 weeks of games)
    played_games: Set[tuple] (week, home_team, away_team)
    current_week: int (0-17)

# recruiting.py
class Recruit (Player-like):
    potential: int (1-10, determines star rating)
    stars: int (2-5)
    team_interests: Dict[str, float] (team_name → interest %)
    preferences: Dict[str, int] (prestige, playing_time, etc.)
    committed: bool
```

## Critical State Management

### Streamlit Session State (app.py)

**IMPORTANT:** Streamlit reruns on every interaction, so state MUST be stored in `st.session_state`.

```python
# Key session state variables
st.session_state.all_teams          # List[Team] - all 360 teams
st.session_state.player_team        # Team - user's selected team
st.session_state.current_season     # Season - active season object
st.session_state.played_games       # Set - CRITICAL for preventing duplicates
st.session_state.recruiting_class   # RecruitingClass
st.session_state.recruiting_actions_remaining  # int (5 per week)
```

### Duplicate Game Simulation Fix (RESOLVED)

**Problem:** Games were being simulated multiple times due to Streamlit reruns.

**Root Cause:** The simulation methods in `season.py` did NOT check if games had been played before simulating them.

**Fix Applied:**
- `season.py:229-232` - `simulate_week()` now checks `played_games` BEFORE simulating
- `season.py:377-380` - `simulate_to_next_game()` now checks `played_games` BEFORE simulating

**Fixed Code:**
```python
# Check BEFORE simulating
game_key = (self.current_week, home_team.name, away_team.name)
if game_key in self.played_games:
    continue  # Skip already played games

self.played_games.add(game_key)
result = self.game_engine.simulate_game_with_details(
    home_team, away_team, is_conference
)
```

**Complete Solution:**
- `played_games` stored in `st.session_state` ✓
- Passed by reference to Season constructor ✓
- Simulation methods check before simulating ✓

**Note:** Previous commits (a61190a, b3d28f8, 1cc82a6) set up the infrastructure but didn't implement the actual check. This is now fixed.

## Development Workflows

### Running the Application

```bash
# Web UI (primary)
streamlit run app.py

# CLI version
python main.py
```

### CI/CD Pipeline

**File:** `.github/workflows/python-app.yml`

**Trigger:** Push/PR to claude branches

**Steps:**
1. Setup Python 3.10 on Ubuntu
2. Install dependencies: `pip install flake8 pytest streamlit`
3. **Linting (fails build on errors):**
   - `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
   - `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`
4. **Import validation:** `python -c "import main"`

**Note:** No test suite exists (pytest installed but no tests written)

### Git Branching

- Main development branch: `main` (inferred)
- Feature branches: `claude/*` pattern for AI-assisted development
- Commit message style: Descriptive with severity prefix (CRITICAL, MAJOR FIX, Fix)

### Code Style

- **Line length:** Max 127 characters (flake8 configured)
- **Complexity:** Max complexity 10 (flake8 configured)
- **No strict formatter:** No black/autopep8 configured
- **Docstrings:** Minimal (add when enhancing code)

## Game Mechanics Reference

### Core Systems

**Offensive Systems** (constants.py:5-10):
- Motion Offense, Princeton Offense, Fast Break, Pick and Roll, Isolation, Post Up

**Defensive Systems** (constants.py:12-17):
- Man-to-Man, 2-3 Zone, 1-3-1 Zone, Full Court Press, Half Court Trap, Pack Line

**Player Positions** (constants.py:19-23):
- PG, SG, SF, PF, C

### Game Simulation (game_engine.py)

```python
# Core algorithm
base_score = (offensive_rating - defensive_rating) * efficiency * possessions

# Modifiers
home_advantage = +0.5 rating
system_matchup_bonus = varies by offensive vs defensive system
overtime = automatic until winner determined

# Stat distribution by rotation
SHORT: starters 70%, backups 25%, bench 5%
BALANCED: starters 60%, backups 35%, bench 5%
DEEP: starters 50%, backups 40%, bench 10%
```

### Scheduling (season.py)

**18-week season:**
- Weeks 1-8: Non-conference (5-7 games per team)
- Weeks 9-18: Conference games (18-20 games)
- Constraints: No back-to-backs, max 2 games/week

**Important:** Schedule uses 0-based week indexing internally (Week 0 = Week 1 in UI)

### Recruiting (recruiting.py)

**Annual Cycle:**
- ~300 recruits generated (3 per team)
- 2-5 star ratings based on hidden potential
- Star rating ≠ actual ability (creates busts and gems)

**Actions (5 per week):**
- Scout: Reveal attributes/potential
- Visit: Build interest (+10-15%)
- Offer: Required for commitment

**Commitment Logic:**
- Time-gated: Early signing (weeks 4-6), Regular signing (week 16+)
- Interest threshold: 85-95+ required
- Success rates vary by team prestige vs recruit stars

**AI Recruiting:**
- CPU teams auto-recruit based on prestige
- Prioritize needs by position/rating

### Prestige Tiers (teams_data.py)

```python
ELITE      # Duke, UNC, Kansas, Kentucky (10 roster avg)
HIGH       # Top 25 programs (8 roster avg)
UPPER_MID  # NCAA regular participants (7 roster avg)
MID        # Bubble teams (6 roster avg)
LOW_MID    # Sub-.500 teams (5 roster avg)
LOW        # Bottom dwellers (4 roster avg)
```

Prestige affects:
- Initial roster quality
- Recruiting interest generation
- AI recruiting success rates

### Player Development (season.py)

**Annual Progression:**
- All players: Small attribute increases (±0-2 across attributes)
- Seniors: Graduate and removed from roster
- Recruits: Fill empty roster spots (12-player max)

## Common Development Tasks

### Adding New Features

1. **Data models:** Modify `models.py` (Player, Team classes)
2. **Game mechanics:** Modify `game_engine.py` (simulation)
3. **Season logic:** Modify `season.py` (scheduling, advancement)
4. **UI (Web):** Modify `app.py` (Streamlit components)
5. **UI (CLI):** Modify `main.py` (menu systems)

### Modifying UI

**Streamlit (app.py):**
- Uses custom dark theme (lines 15-60)
- Font: 'Teko' for sporty feel
- Layout: st.columns, st.tabs, st.expander
- Navigation: page state in session_state

**Key UI sections:**
- Dashboard: Team overview, upcoming games, recruiting summary
- Team: Roster, rotation management, system selection
- League: Standings, schedules, league-wide stats
- Recruiting: Scout/visit/offer actions, interest tracking

### Adding New Teams/Conferences

**File:** `teams_data.py`

1. Add conference to `CONFERENCES` dict
2. Add team to `D1_TEAMS` dict with prestige tier
3. Regenerate all teams: `create_all_teams()` handles automatically

### Modifying Game Balance

**Files:** `constants.py`, `game_engine.py`

- Scoring: Adjust `POSSESSIONS_PER_GAME` (constants.py:29)
- Difficulty: Modify system matchup bonuses (game_engine.py:45-86)
- Recruiting: Adjust commitment thresholds (recruiting.py:450-480)
- Player quality: Modify prestige roster generation (models.py:125-155)

## Testing Strategy

**Current State:** No automated tests

**Manual Testing Checklist:**
1. Run `python -c "import main"` to verify imports
2. Test Streamlit UI: `streamlit run app.py`
3. Test CLI: `python main.py`
4. Check flake8: `flake8 . --count --select=E9,F63,F7,F82`

**If Adding Tests:**
- Use pytest framework (already in requirements)
- Test game simulation determinism
- Test recruiting logic edge cases
- Test season advancement and player development

## Known Issues & Gotchas

### Streamlit State Persistence

**Issue:** Session state lost on browser refresh
**Workaround:** No save/load system implemented
**Future:** Add pickle/JSON serialization for save games

### Duplicate Game Simulation (FIXED)

**Issue:** Games were being simulated multiple times on Streamlit reruns
**Status:** FIXED - Simulation methods now check `played_games` before simulating
**Fix Applied:** Added `if game_key in self.played_games: continue` in both simulate_week() and simulate_to_next_game()
**See:** "Duplicate Game Simulation Fix" section above for details

### Recruiting Commitment Timing

**Issue:** Players can't commit outside signing periods
**Expected Behavior:** Time-gated to weeks 4-6 (early) and 16+ (regular)
**Location:** recruiting.py:460-475

### Conference Scheduling Variance

**Issue:** Conference game counts vary (18-20 games)
**Cause:** Different conference sizes (10-16 teams)
**Expected Behavior:** Working as intended

### Player Development Randomness

**Issue:** Attribute changes seem random
**Cause:** Small random increments each year
**Location:** season.py:380-395

## File Reference Guide

### When to Edit Each File

| File | Edit When... |
|------|-------------|
| `app.py` | Changing web UI, adding Streamlit pages, modifying navigation |
| `main.py` | Changing CLI interface, adding terminal menus |
| `models.py` | Adding player/team attributes, changing data structures |
| `season.py` | Modifying scheduling, standings, season advancement logic |
| `game_engine.py` | Changing simulation algorithm, scoring, stat distribution |
| `recruiting.py` | Modifying recruiting mechanics, AI recruiting, commitment logic |
| `tournament.py` | Changing postseason format, seeding, tournament brackets |
| `teams_data.py` | Adding/removing teams, modifying conferences, adjusting prestige |
| `constants.py` | Adding systems, changing game parameters, global configuration |

### Important Line References

**Streamlit State Management:**
- app.py:122 - Initialize played_games in session_state
- app.py:362-368 - Season object creation with played_games reference
- app.py:424-426 - Persist Season object back to session_state

**Game Simulation:**
- game_engine.py:87-120 - simulate_game() core algorithm
- game_engine.py:45-86 - System matchup bonuses
- season.py:229-232 - simulate_week() checks played_games to prevent duplicates
- season.py:377-380 - simulate_to_next_game() checks played_games to prevent duplicates

**Recruiting Commitment:**
- recruiting.py:450-480 - Commitment logic and timing
- recruiting.py:350-400 - AI recruiting decisions

**Season Scheduling:**
- season.py:50-150 - generate_schedule() algorithm
- season.py:200-250 - Conference standings calculation

**Player Development:**
- season.py:380-395 - advance_year() player progression
- models.py:125-155 - Initial roster generation by prestige

## Naming Conventions

**Variables:**
- `player_team` - User's selected team
- `all_teams` - List of all 360 D1 teams
- `current_season` - Active Season object
- `played_games` - Set of (week, home, away) tuples

**Functions:**
- `simulate_game()` - Returns game result dict
- `advance_week()` - Progress season by one week
- `create_all_teams()` - Factory for all teams
- `generate_schedule()` - Build season schedule

**Classes:**
- PascalCase: `Player`, `Team`, `Season`, `GameEngine`
- No abstract base classes
- Composition over inheritance (except Recruit ≈ Player)

## Performance Considerations

**State Size:**
- 360 teams × 12 players = 4,320 player objects in memory
- Streamlit session state can grow large over multiple seasons
- No optimization needed for current scope

**Simulation Speed:**
- Week simulation: ~20-30 games, runs instantly
- Full season: ~2,000+ games total, takes seconds
- No need for async/threading currently

**Recruiting:**
- 300 recruits × 360 teams = potential 108k interest calculations
- Current implementation is fast enough
- AI recruiting is the bottleneck (could parallelize)

## Extension Points

### Easy Additions

1. **Player Stats Tracking:** Add new stats to Player.stats dict
2. **New Systems:** Add to OFFENSIVE_SYSTEMS/DEFENSIVE_SYSTEMS in constants.py
3. **Custom Conferences:** Add to CONFERENCES dict in teams_data.py
4. **UI Themes:** Modify CSS in app.py:15-60

### Moderate Additions

1. **Transfer Portal:** New recruiting.py module for mid-season transfers
2. **Injuries:** Add injury system to Player class, affect availability
3. **Coaching Staff:** New model for assistant coaches with bonuses
4. **Player Morale:** Add morale attribute affecting performance

### Complex Additions

1. **Save/Load System:** Serialize session_state to JSON/pickle
2. **Historical Stats:** Database layer for multi-season tracking
3. **Play-by-Play:** Detailed game simulation with possession-level events
4. **Online Multiplayer:** Backend API for shared leagues

## Best Practices for AI Assistants

### Before Making Changes

1. **Read related files:** Don't assume - verify with Read tool
2. **Check git history:** Look for recent fixes to avoid regressions
3. **Test imports:** Ensure changes don't break `import main`
4. **Consider state:** Think about Streamlit reruns and session state

### When Implementing Features

1. **Follow existing patterns:** Match coding style in the file
2. **Update both UIs:** app.py (Streamlit) AND main.py (CLI) if applicable
3. **Preserve game balance:** Don't make drastic changes to simulation
4. **Document complex logic:** Add comments for non-obvious algorithms

### When Fixing Bugs

1. **Check session state:** Most bugs relate to Streamlit state management
2. **Look for recent fixes:** Git log shows common bug patterns
3. **Test edge cases:** Recruiting, overtime, tiebreakers are complex
4. **Maintain backwards compatibility:** Don't break existing saves (future)

### Code Review Checklist

- [ ] Follows flake8 rules (max line length 127, complexity 10)
- [ ] No new imports without updating requirements.txt
- [ ] Session state properly managed in app.py
- [ ] Both CLI and web UI updated if applicable
- [ ] No hardcoded magic numbers (use constants.py)
- [ ] Player/team attributes stay in 1-10 range
- [ ] Recruiting timing constraints respected
- [ ] Git commit message is descriptive

## Debugging Tips

### Common Issues

**"KeyError in session_state"**
→ Initialize in app.py initialization block (lines 90-130)

**"Games simulating multiple times"**
→ FIXED: Simulation methods now check played_games before simulating
→ If you still see this issue, check that played_games is properly stored in st.session_state
→ Verify Season object receives the played_games set reference in constructor

**"Recruits won't commit"**
→ Check week number (must be 4-6 or 16+) and interest level (85-95+)

**"Wrong number of conference games"**
→ Expected - varies by conference size (10-16 teams)

**"Player stats don't add up"**
→ Check rotation system - stat distribution varies (SHORT/BALANCED/DEEP)

### Useful Debug Commands

```python
# Check session state
st.write(st.session_state.keys())
st.write(st.session_state.played_games)

# Verify game simulation
print(f"Week {week}: {len(games_this_week)} games scheduled")
print(f"Played: {len(season.played_games)} unique games")

# Check recruiting state
for recruit in recruits:
    if player_team.name in recruit.team_interests:
        print(f"{recruit.name}: {recruit.team_interests[player_team.name]}% interest")
```

## Resources

**Documentation:**
- Streamlit docs: https://docs.streamlit.io/
- Python 3.10 docs: https://docs.python.org/3.10/

**Key Files to Reference:**
- Game balance: `constants.py`, `game_engine.py`
- Data structures: `models.py`
- Real-world data: `teams_data.py`

**Git History:**
- Recent bug fixes show common patterns
- Commit messages describe intent clearly
- Check `git log --oneline -20` before major changes

---

**Last Updated:** 2025-11-18 (Auto-generated by AI)

**Codebase Version:** Based on commit a61190a "FINAL FIX: Store played_games in session_state directly"

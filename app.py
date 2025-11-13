"""
College Basketball Manager - Simple Dashboard UI
Dark mode, minimal navigation, action-focused
"""

import streamlit as st
import pandas as pd
from models import Team
from teams_data import create_all_teams, get_team_by_name, CONFERENCES, TEAM_NICKNAMES
from season import Season
from tournament import run_postseason
from game_engine import GameEngine
from constants import OFFENSIVE_SYSTEMS, DEFENSIVE_SYSTEMS
from recruiting import RecruitingClass, recruit_players_auto


# Page config
st.set_page_config(
    page_title="College Basketball Manager",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode styling with sporty font
st.markdown("""
<style>
    /* Import sporty font */
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@400;500;600;700&display=swap');

    /* Dark theme */
    .stApp {
        background-color: #0e1117;
    }

    /* Sporty headers */
    h1, h2, h3 {
        font-family: 'Teko', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        color: #ffffff;
    }

    /* Main title */
    .main-title {
        font-family: 'Teko', sans-serif;
        font-size: 3.5em;
        font-weight: 700;
        text-align: center;
        letter-spacing: 2px;
        color: #ff6b35;
        margin-bottom: 0;
    }

    /* Nav buttons */
    .nav-button {
        font-family: 'Teko', sans-serif;
        font-size: 1.3em;
        letter-spacing: 1px;
    }

    /* Results boxes */
    .win-box {
        background-color: #1a4d2e;
        border-left: 4px solid #4caf50;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-family: 'Teko', sans-serif;
        font-size: 1.2em;
    }

    .loss-box {
        background-color: #4d1a1a;
        border-left: 4px solid #f44336;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-family: 'Teko', sans-serif;
        font-size: 1.2em;
    }

    .tie-box {
        background-color: #3d3d1a;
        border-left: 4px solid #ffa726;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-family: 'Teko', sans-serif;
        font-size: 1.2em;
    }

    /* Info boxes */
    .info-box {
        background-color: #1a1a2e;
        border-left: 4px solid: #ff6b35;
        padding: 12px;
        border-radius: 4px;
        margin: 12px 0;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Teko', sans-serif;
        font-size: 2em;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if 'game_initialized' not in st.session_state:
        st.session_state.all_teams = create_all_teams()
        st.session_state.player_team = None
        st.session_state.current_season = None
        st.session_state.current_year = 2025
        st.session_state.game_engine = GameEngine()
        st.session_state.game_initialized = True
        st.session_state.page = "dashboard"
        st.session_state.recruiting_class = None


def main():
    init_session_state()

    # Title
    st.markdown('<div class="main-title">🏀 CBB MANAGER</div>', unsafe_allow_html=True)

    # Team selection or navigation
    if not st.session_state.player_team:
        select_team_page()
    else:
        # Navigation
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📊 DASHBOARD", use_container_width=True, type="primary" if st.session_state.page == "dashboard" else "secondary"):
                st.session_state.page = "dashboard"
                st.rerun()
        with col2:
            if st.button("👥 TEAM", use_container_width=True, type="primary" if st.session_state.page == "team" else "secondary"):
                st.session_state.page = "team"
                st.rerun()
        with col3:
            if st.button("🏆 LEAGUE", use_container_width=True, type="primary" if st.session_state.page == "league" else "secondary"):
                st.session_state.page = "league"
                st.rerun()
        with col4:
            if st.button("🎓 RECRUITING", use_container_width=True, type="primary" if st.session_state.page == "recruiting" else "secondary"):
                st.session_state.page = "recruiting"
                st.rerun()

        st.markdown("---")

        # Route to pages
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "team":
            team_page()
        elif st.session_state.page == "league":
            league_page()
        elif st.session_state.page == "recruiting":
            recruiting_page()


def select_team_page():
    """Team selection"""
    st.markdown("## SELECT YOUR TEAM")
    st.caption("Choose a school to begin your coaching career")

    col1, col2 = st.columns(2)
    with col1:
        conferences = ["All"] + sorted(CONFERENCES.keys())
        selected_conf = st.selectbox("Conference:", conferences)
    with col2:
        sort_by = st.selectbox("Sort by:", ["Prestige", "Alphabetical", "Rating"])

    # Search box
    search_term = st.text_input("🔍 Search teams:", "").strip().lower()

    if selected_conf == "All":
        teams = st.session_state.all_teams
    else:
        teams = [t for t in st.session_state.all_teams if t.conference == selected_conf]

    # Apply search filter
    if search_term:
        teams = [t for t in teams if search_term in t.name.lower()]

    # Sort teams
    if sort_by == "Prestige":
        prestige_order = {"ELITE": 0, "HIGH": 1, "UPPER_MID": 2, "MID": 3, "LOW_MID": 4, "LOW": 5}
        teams.sort(key=lambda t: (prestige_order.get(t.prestige, 6), -t.get_team_rating()))
    elif sort_by == "Alphabetical":
        teams.sort(key=lambda t: t.name)
    else:  # Rating
        teams.sort(key=lambda t: t.get_team_rating(), reverse=True)

    # Get preseason rankings
    all_teams_ranked = sorted(st.session_state.all_teams, key=lambda t: t.get_team_rating(), reverse=True)

    team_data = []
    for t in teams:
        rank = next((i+1 for i, rt in enumerate(all_teams_ranked) if rt.name == t.name), None)
        rank_str = f"#{rank}" if rank and rank <= 25 else "-"

        team_data.append({
            "Rank": rank_str,
            "Team": t.name,
            "Conference": t.conference,
            "Prestige": t.prestige,
            "Rating": f"{t.get_team_rating():.1f}"
        })

    df = pd.DataFrame(team_data)
    st.dataframe(df, use_container_width=True, height=450, hide_index=True)
    st.caption(f"Showing {len(teams)} teams")

    team_names = [t.name for t in teams]
    selected = st.selectbox("Choose your team:", [""] + team_names)

    if selected:
        team = get_team_by_name(st.session_state.all_teams, selected)
        if team:
            # Show team preview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Prestige", team.prestige)
            with col2:
                st.metric("Rating", f"{team.get_team_rating():.1f}")
            with col3:
                st.metric("Conference", team.conference)

            if st.button("🏀 START CAREER", type="primary", use_container_width=True):
                st.session_state.player_team = team
                st.rerun()


def dashboard_page():
    """Main dashboard - all key info visible"""
    team = st.session_state.player_team
    season = st.session_state.current_season

    # Get team ranking - only update at week boundaries to prevent mid-week changes
    current_week = season.current_week if season else 0

    # Check if we need to recalculate rankings (week changed or first time)
    if 'rankings_week' not in st.session_state or st.session_state.rankings_week != current_week:
        # Recalculate rankings using power ranking system
        def power_ranking(t):
            if t.games_played == 0:
                # No games yet - pure rating
                return t.get_team_rating()
            else:
                # Blend win% and rating - rating influence decreases as games increase
                win_pct = t.wins / t.games_played
                rating = t.get_team_rating()

                # Weight: early season ratings matter, late season record matters
                # At 1 game: 80% rating, 20% record
                # At 10 games: 50% rating, 50% record
                # At 20+ games: 20% rating, 80% record
                games_factor = min(t.games_played / 25, 1.0)
                record_weight = 0.2 + (games_factor * 0.6)
                rating_weight = 1.0 - record_weight

                # Convert win% to 0-100 scale to match rating scale
                record_score = win_pct * 100

                return (record_score * record_weight) + (rating * rating_weight)

        all_teams_sorted = sorted(st.session_state.all_teams, key=power_ranking, reverse=True)
        team_rank = next((i+1 for i, t in enumerate(all_teams_sorted) if t.name == team.name), None)

        # Cache the ranking for this week
        st.session_state.rankings_week = current_week
        st.session_state.cached_team_rank = team_rank
    else:
        # Use cached ranking from start of week
        team_rank = st.session_state.cached_team_rank

    rank_display = f"#{team_rank} " if team_rank and team_rank <= 25 else ""

    # Header
    nickname = TEAM_NICKNAMES.get(team.name, "")
    team_display = f"{team.name} {nickname}" if nickname else team.name

    st.markdown(f"## {rank_display}{team_display}")
    if season:
        current_date = season.week_to_date(season.current_week)
        st.caption(f"{team.conference} • {current_date}, 2025 • Week {season.current_week + 1}/{season.total_weeks}")
    else:
        st.caption(f"{team.conference} • {st.session_state.current_year} Season")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("RECORD", f"{team.wins}-{team.losses}")
    with col2:
        st.metric("CONF", f"{team.conference_wins}-{team.conference_losses}")
    with col3:
        st.metric("RATING", f"{team.get_team_rating():.1f}")
    with col4:
        if season:
            st.metric("WEEK", f"{season.current_week}/{season.total_weeks}")
        else:
            st.metric("STATUS", "PRE-SEASON")

    st.markdown("---")

    # Weekly Tasks Section
    if season and season.current_week < season.total_weeks:
        st.markdown("### 📋 WEEKLY TASKS")

        tasks = []
        current_week = season.current_week

        # Recruiting tasks
        recruiting_actions = getattr(st.session_state, 'recruiting_actions_remaining', 5)
        if recruiting_actions > 0:
            tasks.append(f"✅ Use {recruiting_actions} recruiting action(s)")
        else:
            tasks.append(f"✓ Recruiting actions complete (0/5 remaining)")

        # Check recruiting class status
        if st.session_state.recruiting_class:
            rc = st.session_state.recruiting_class
            commits = [r for r in rc.recruits if r.committed and r.committed_to == team.name]
            graduating = sum(1 for p in team.roster if p.year >= 4)
            remaining_spots = graduating - len(commits)

            if remaining_spots > 0:
                tasks.append(f"🎓 Fill {remaining_spots} scholarship spot(s) ({len(commits)}/{graduating} committed)")
            else:
                tasks.append(f"✓ Recruiting class full ({len(commits)}/{graduating})")

        # Check if in signing period
        is_early_period = 4 <= current_week <= 6
        is_regular_period = current_week >= 16

        if is_early_period:
            tasks.append("📝 EARLY SIGNING PERIOD - Recruits can commit!")
        elif current_week == 3:
            tasks.append("⏰ Early signing period starts next week")
        elif is_regular_period:
            tasks.append("📝 REGULAR SIGNING PERIOD - Recruits can commit!")
        elif current_week == 15:
            tasks.append("⏰ Regular signing period starts next week")

        # Display tasks
        for task in tasks:
            st.text(task)

        st.markdown("---")

    # Season controls
    if not season:
        st.info("**PRE-SEASON** • Ready to start the season")
        if st.button("▶️ START SEASON", type="primary", use_container_width=True):
            st.session_state.current_season = Season(st.session_state.all_teams, st.session_state.current_year)
            st.session_state.current_season.generate_schedule()
            st.rerun()
    else:
        # In season
        if season.current_week >= season.total_weeks:
            st.success("**REGULAR SEASON COMPLETE**")
            if st.button("🏆 POSTSEASON", type="primary", use_container_width=True):
                run_postseason_tournaments()
        else:
            # Show next game info
            next_game = season.get_next_game_for_team(team)
            if next_game:
                location = "vs" if next_game['is_home'] else "@"
                conf_tag = " (CONFERENCE)" if next_game['is_conference'] else ""
                st.info(f"**NEXT GAME:** {next_game['date']} • {location} {next_game['opponent'].name}{conf_tag}")

            # Simulation controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏭️ SIM TO NEXT GAME", type="primary", use_container_width=True):
                    # Get the team object from season.all_teams (ensure same instance)
                    season_team = next((t for t in season.all_teams if t.name == team.name), team)

                    st.write(f"DEBUG - Before sim: Week={season.current_week}, Played={len(season.played_games)}, Record={team.wins}-{team.losses}")
                    st.write(f"DEBUG - Played games: {list(season.played_games)[:5]}")  # Show first 5

                    result = season.simulate_to_next_game(season_team)
                    if result:
                        st.session_state.last_results = [result]
                        st.write(f"DEBUG - Just played: {result['home_team']} vs {result['away_team']}")
                        st.write(f"DEBUG - After sim: Played={len(season.played_games)}")

                        # Check if team has more games this week
                        next_game = season.get_next_game_for_team(season_team)
                        if next_game:
                            st.write(f"DEBUG - Next game: {next_game['opponent'].name} at week {next_game['week']}")
                        else:
                            st.write("DEBUG - No next game found")

                        if next_game is None or next_game['week'] > season.current_week:
                            # No more games this week, advance to next week
                            season.current_week += 1
                            st.write(f"DEBUG - Advanced to week {season.current_week}")
                            st.session_state.recruiting_actions_remaining = 5
                            # Update recruit interest levels each week
                            if st.session_state.recruiting_class is not None:
                                st.session_state.recruiting_class.update_weekly_interest()

                        # CRITICAL: Explicitly save season back to session state
                        # This ensures played_games set is persisted
                        st.session_state.current_season = season

                    st.rerun()
            with col2:
                if st.button("⏩ SIM TO END", use_container_width=True):
                    season.simulate_full_season()
                    # Update recruit interest levels after simulating multiple weeks
                    if st.session_state.recruiting_class is not None:
                        st.session_state.recruiting_class.update_weekly_interest()
                    # Save season back to session state
                    st.session_state.current_season = season
                    st.rerun()

            # Recent results
            if hasattr(st.session_state, 'last_results') and st.session_state.last_results:
                st.markdown("### RECENT RESULTS")
                for result in st.session_state.last_results:
                    if result['home_team'] == team.name or result['away_team'] == team.name:
                        our_score = result['home_score'] if result['home_team'] == team.name else result['away_score']
                        opp_score = result['away_score'] if result['home_team'] == team.name else result['home_score']
                        opponent = result['away_team'] if result['home_team'] == team.name else result['home_team']

                        # Handle wins and losses (no ties in basketball - games go to OT)
                        won = our_score > opp_score
                        box_class = "win-box" if won else "loss-box"
                        result_text = "W" if won else "L"
                        location = "vs" if result['home_team'] == team.name else "@"

                        st.markdown(f"""
                        <div class="{box_class}">
                            <strong>{result_text}</strong> &nbsp;&nbsp; {team.name} {our_score}, {location} {opponent} {opp_score}
                        </div>
                        """, unsafe_allow_html=True)

    # Always show upcoming games prominently if in season
    if season and season.current_week < season.total_weeks:
        st.markdown("---")
        st.markdown("### 📅 UPCOMING GAMES")
        schedule = season.get_team_schedule(team)
        # Sort by week and day_offset to show chronologically
        schedule_sorted = sorted(schedule, key=lambda g: (g['week'], g.get('day_offset', 0)))
        upcoming = [g for g in schedule_sorted if not g['played']]  # Show ALL upcoming games

        if upcoming:
            # Show in a more visible format
            for game in upcoming:
                location = "vs" if game['is_home'] else "@"
                location_icon = "🏠" if game['is_home'] else "✈️"
                game_type = " (CONFERENCE)" if game['is_conference'] else ""
                day_offset = game.get('day_offset', 0)
                game_date = season.week_to_date(game['week'] - 1, day_offset)
                opponent_nickname = TEAM_NICKNAMES.get(game['opponent'], "")
                opponent_display = f"{game['opponent']} {opponent_nickname}" if opponent_nickname else game['opponent']
                st.text(f"{location_icon} {game_date}: {location} {opponent_display}{game_type}")
        else:
            st.info("No upcoming games scheduled")


def team_page():
    """Team management - roster, stats, systems"""
    team = st.session_state.player_team

    st.markdown(f"## {team.name} TEAM")

    # Systems selection
    st.markdown("### ⚙️ GAME PLAN")
    col1, col2 = st.columns(2)

    with col1:
        offense = st.selectbox(
            "Offensive System:",
            OFFENSIVE_SYSTEMS,
            index=OFFENSIVE_SYSTEMS.index(team.offensive_system) if team.offensive_system in OFFENSIVE_SYSTEMS else 0
        )
        if offense != team.offensive_system:
            team.offensive_system = offense
            st.success(f"Changed to {offense}")

    with col2:
        defense = st.selectbox(
            "Defensive System:",
            DEFENSIVE_SYSTEMS,
            index=DEFENSIVE_SYSTEMS.index(team.defensive_system) if team.defensive_system in DEFENSIVE_SYSTEMS else 0
        )
        if defense != team.defensive_system:
            team.defensive_system = defense
            st.success(f"Changed to {defense}")

    st.markdown("---")

    # Tabs for roster management
    tab1, tab2, tab3, tab4 = st.tabs(["ROSTER", "STATS", "ROTATION", "SCHEDULE"])

    with tab1:
        show_roster(team)

    with tab2:
        show_stats(team)

    with tab3:
        manage_rotation(team)

    with tab4:
        show_schedule(team)


def show_roster(team):
    """Display roster"""
    year_names = {1: "FR", 2: "SO", 3: "JR", 4: "SR"}

    roster_data = []
    for player in sorted(team.roster, key=lambda p: p.overall_rating(), reverse=True):
        roster_data.append({
            "Name": player.name,
            "Pos": player.position,
            "Yr": year_names.get(player.year, ""),
            "OVR": f"{player.overall_rating():.1f}",
            "SHT": f"{player.shooting:.1f}",
            "DEF": f"{player.defense:.1f}",
            "ATH": f"{player.athleticism:.1f}",
            "IQ": f"{player.basketball_iq:.1f}"
        })

    df = pd.DataFrame(roster_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=500)


def show_stats(team):
    """Display player stats"""
    if team.games_played == 0:
        st.info("No games played yet this season.")
        return

    year_names = {1: "FR", 2: "SO", 3: "JR", 4: "SR"}

    stats_data = []
    for player in team.roster:
        if player.games_played > 0:
            stats = player.get_stats_per_game()
            stats_data.append({
                "Name": player.name,
                "Pos": player.position,
                "Yr": year_names.get(player.year, ""),
                "GP": player.games_played,
                "PPG": f"{stats['PPG']:.1f}",
                "RPG": f"{stats['RPG']:.1f}",
                "APG": f"{stats['APG']:.1f}"
            })

    if stats_data:
        df = pd.DataFrame(stats_data)
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)

        # Team averages - calculate from game results
        st.markdown("### TEAM AVERAGES")
        col1, col2, col3 = st.columns(3)

        if team.games_played > 0 and team.results:
            # Calculate team PPG from actual game scores
            total_points = 0
            for result in team.results:
                if result['home_team'] == team.name:
                    total_points += result['home_score']
                else:
                    total_points += result['away_score']

            total_ppg = total_points / team.games_played
            # For rebounds/assists, sum player stats and divide by games
            total_rpg = sum(p.rebounds for p in team.roster) / team.games_played
            total_apg = sum(p.assists for p in team.roster) / team.games_played
        else:
            total_ppg = total_rpg = total_apg = 0

        col1.metric("PPG", f"{total_ppg:.1f}")
        col2.metric("RPG", f"{total_rpg:.1f}")
        col3.metric("APG", f"{total_apg:.1f}")


def manage_rotation(team):
    """Rotation management"""
    st.markdown("### ROTATION STYLE")

    style = st.selectbox(
        "Minutes Distribution:",
        ["BALANCED", "SHORT", "DEEP"],
        index=["BALANCED", "SHORT", "DEEP"].index(team.rotation_style)
    )

    if style != team.rotation_style:
        team.rotation_style = style
        st.success(f"Changed to {style} rotation")

    dist = team.get_rotation_distribution()
    st.caption(f"Starters: {int(dist[0]*100)}% • Backups: {int(dist[1]*100)}% • Bench: {int(dist[2]*100)}%")

    if st.button("AUTO-SET BY RATING"):
        team._set_default_rotation()
        st.success("Rotation updated!")


def show_schedule(team):
    """Display full season schedule with results"""
    st.markdown("### SEASON SCHEDULE")

    season = st.session_state.current_season

    if not season:
        st.info("Schedule will be generated when you start the season")
        return

    schedule = season.get_team_schedule(team)

    if not schedule:
        st.info("Schedule will be generated at season start")
        return

    # Sort schedule chronologically by week and day_offset
    schedule_sorted = sorted(schedule, key=lambda g: (g['week'], g.get('day_offset', 0)))

    # Separate into completed and upcoming games
    completed = [g for g in schedule_sorted if g.get('played', False)]
    upcoming = [g for g in schedule_sorted if not g.get('played', False)]

    # Show record (no ties - games go to OT)
    wins = 0
    losses = 0
    for g in completed:
        team_score = g.get('team_score', 0)
        opp_score = g.get('opp_score', 0)
        if team_score > opp_score:
            wins += 1
        else:
            losses += 1

    st.metric("Record", f"{wins}-{losses}")

    # Display completed games
    if completed:
        st.markdown("#### COMPLETED GAMES")
        for game in completed:
            team_score = game.get('team_score', 0)
            opp_score = game.get('opp_score', 0)

            # Determine W/L (no ties - games go to OT)
            won = team_score > opp_score
            box_class = "win-box" if won else "loss-box"
            result_text = "W" if won else "L"

            location = "vs" if game['is_home'] else "@"
            conf_tag = " (CONF)" if game['is_conference'] else ""
            day_offset = game.get('day_offset', 0)
            game_date = season.week_to_date(game['week'] - 1, day_offset)  # week is 1-indexed

            score_display = f"{team_score}-{opp_score}"

            st.markdown(
                f'<div class="{box_class}">'
                f'<strong>{game_date}</strong> • {result_text} {score_display} • '
                f'{location} {game["opponent"]}{conf_tag}'
                f'</div>',
                unsafe_allow_html=True
            )

    # Display upcoming games
    if upcoming:
        st.markdown("#### UPCOMING GAMES")
        for game in upcoming:  # Show ALL upcoming games
            location = "vs" if game['is_home'] else "@"
            conf_tag = " (CONF)" if game['is_conference'] else ""
            day_offset = game.get('day_offset', 0)
            game_date = season.week_to_date(game['week'] - 1, day_offset)  # week is 1-indexed

            st.markdown(
                f'<div style="padding: 10px; margin: 5px 0; border-left: 3px solid #888; background-color: #1a1a1a;">'
                f'<strong>{game_date}</strong> • {location} {game["opponent"]}{conf_tag}'
                f'</div>',
                unsafe_allow_html=True
            )


def league_page():
    """League standings"""
    st.markdown("## LEAGUE STANDINGS")

    view = st.radio("", ["Top 25", "Conference"], horizontal=True)

    if view == "Top 25":
        # Use preseason rankings if no games played
        player_team = st.session_state.player_team
        if player_team.games_played == 0:
            teams = sorted(st.session_state.all_teams, key=lambda t: t.get_team_rating(), reverse=True)[:25]
            st.caption("Preseason Top 25 (based on team ratings)")
        else:
            teams = sorted(st.session_state.all_teams, key=lambda t: (t.wins, -t.losses), reverse=True)[:25]

        standings_data = []
        for i, t in enumerate(teams, 1):
            standings_data.append({
                "Rank": i,
                "Team": t.name,
                "Record": f"{t.wins}-{t.losses}",
                "Conf": f"{t.conference_wins}-{t.conference_losses}",
                "Rating": f"{t.get_team_rating():.1f}"
            })

        df = pd.DataFrame(standings_data)
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)

    else:
        conferences = sorted(CONFERENCES.keys())
        selected_conf = st.selectbox("Select Conference:", conferences)

        teams = [t for t in st.session_state.all_teams if t.conference == selected_conf]
        teams = sorted(teams, key=lambda t: (t.conference_wins, -t.conference_losses, t.wins), reverse=True)

        standings_data = []
        for i, t in enumerate(teams, 1):
            standings_data.append({
                "Rank": i,
                "Team": t.name,
                "Overall": f"{t.wins}-{t.losses}",
                "Conference": f"{t.conference_wins}-{t.conference_losses}"
            })

        df = pd.DataFrame(standings_data)
        st.dataframe(df, use_container_width=True, hide_index=True, height=600)


def recruiting_page():
    """Recruiting with actions system"""
    team = st.session_state.player_team

    st.markdown("## RECRUITING")

    # Count scholarships
    graduating_seniors = sum(1 for p in team.roster if p.year >= 4)

    # Initialize recruiting class
    if st.session_state.recruiting_class is None:
        st.session_state.recruiting_class = RecruitingClass(
            st.session_state.current_year + 1,
            len(st.session_state.all_teams)
        )
        # Initialize realistic team interests for all recruits across all teams
        st.session_state.recruiting_class.initialize_team_interests(st.session_state.all_teams)

    # Initialize recruiting actions per week (resets each week)
    if not hasattr(st.session_state, 'recruiting_actions_remaining'):
        st.session_state.recruiting_actions_remaining = 5

    rc = st.session_state.recruiting_class
    commits = [r for r in rc.recruits if r.committed and r.committed_to == team.name]
    available_spots = graduating_seniors - len(commits)

    # Header info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ACTIONS LEFT", f"{st.session_state.recruiting_actions_remaining}/5")
    with col2:
        st.metric("COMMITS", f"{len(commits)}/{graduating_seniors}")
    with col3:
        st.metric("SPOTS LEFT", available_spots)

    st.markdown("---")

    # View toggle
    view = st.radio("", ["Recommended", "Search All"], horizontal=True)

    if view == "Recommended":
        # Show realistic recruiting targets based on team prestige and recruit quality
        all_recruits = rc.get_available_recruits()

        # Filter by realistic targets based on prestige
        recruits = []
        for r in all_recruits:
            is_realistic = False

            if r.stars == 5 or r.ranking <= 20:
                # 5-star: Only ELITE/HIGH prestige teams
                if team.prestige in ["ELITE", "HIGH"]:
                    is_realistic = True
            elif r.stars == 4 or r.ranking <= 100:
                # 4-star: ELITE/HIGH/UPPER_MID teams
                if team.prestige in ["ELITE", "HIGH", "UPPER_MID"]:
                    is_realistic = True
            elif r.stars == 3:
                # 3-star: All teams can realistically recruit
                is_realistic = True
            else:
                # 2-star: Lower prestige teams should target these
                if team.prestige in ["MID", "LOW_MID", "LOW"]:
                    is_realistic = True
                elif team.prestige in ["UPPER_MID"] and len([x for x in all_recruits if x.stars >= 3]) < 20:
                    is_realistic = True  # If few 3+ stars available

            if is_realistic:
                recruits.append(r)

        # Sort by: 1) If aware of you (and interest level), 2) Star rating, 3) Ranking
        def sort_key(r):
            aware = team.name in r.team_interests
            interest = r.team_interests.get(team.name, 0) if aware else 0
            return (aware, interest, -r.stars, r.ranking)

        recruits.sort(key=sort_key, reverse=True)
        recruits = recruits[:50]
        st.caption(f"Showing realistic recruiting targets for {team.prestige} prestige team")
    else:
        # Show all recruits with filters
        col1, col2, col3 = st.columns(3)
        with col1:
            position = st.selectbox("Position:", ["All", "PG", "SG", "SF", "PF", "C"])
        with col2:
            stars = st.selectbox("Stars:", ["All", "5⭐", "4⭐", "3⭐", "2⭐"])
        with col3:
            sort_by = st.selectbox("Sort by:", ["Rank", "Interest", "Stars"])

        # Search box
        search_name = st.text_input("🔍 Search by name:", "").strip().lower()

        pos_filter = None if position == "All" else position
        recruits = rc.get_available_recruits(pos_filter)

        # Apply filters
        if stars != "All":
            star_val = int(stars[0])
            recruits = [r for r in recruits if r.stars == star_val]

        if search_name:
            recruits = [r for r in recruits if search_name in r.name.lower()]

        # Sort
        if sort_by == "Rank":
            recruits.sort(key=lambda r: r.ranking)
        elif sort_by == "Interest":
            recruits.sort(key=lambda r: r.interest, reverse=True)
        elif sort_by == "Stars":
            recruits.sort(key=lambda r: r.stars, reverse=True)

        recruits = recruits[:100]  # Show top 100
        st.caption(f"Showing {len(recruits)} recruits")

    if not recruits:
        st.info("No recruits available.")
        return

    # Show commits
    if commits:
        with st.expander(f"YOUR COMMITS ({len(commits)})", expanded=False):
            for commit in commits:
                st.text(f"{'⭐' * commit.stars} {commit.name} ({commit.position}) - #{commit.ranking} - {commit.state}")

    st.markdown("---")
    st.markdown("### RECRUITS (Click to view details)")

    # Initialize selected recruit in session state
    if 'selected_recruit_name' not in st.session_state:
        st.session_state.selected_recruit_name = None

    # Show recruits as clickable cards - limit to 20 at a time for performance
    recruits_display = recruits[:20]

    for r in recruits_display:
        # Show team-specific interest if known, otherwise "Unknown"
        team_interest = r.team_interests.get(team.name, None)
        interest_display = f"{int(team_interest)}%" if team_interest is not None else "?"

        # Highlight if this recruit is selected
        is_selected = st.session_state.selected_recruit_name == r.name
        button_type = "primary" if is_selected else "secondary"

        # Create a clickable button for each recruit
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])
        with col1:
            st.text(f"#{r.ranking}")
        with col2:
            if st.button(f"{'⭐' * r.stars} {r.name}", key=f"recruit_{r.name}_{r.ranking}", type=button_type, use_container_width=True):
                st.session_state.selected_recruit_name = r.name
                st.rerun()
        with col3:
            st.text(f"{r.position} • {r.state}")
        with col4:
            st.text(f"{r.get_offense_rating()} / {r.get_defense_rating()}")
        with col5:
            st.text(f"{interest_display}")

    st.caption(f"Showing {len(recruits_display)} of {len(recruits)} recruits")

    st.markdown("---")

    # Show detailed info for selected recruit
    if st.session_state.selected_recruit_name:
        # Find the selected recruit
        recruit = next((r for r in recruits if r.name == st.session_state.selected_recruit_name), None)

        if not recruit:
            st.warning("Recruit not found")
            st.session_state.selected_recruit_name = None
            return

        # Recruit details
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"### {recruit.name}")
            st.text(f"#{recruit.ranking} • {recruit.position} • {recruit.state}")
            st.text(f"{'⭐' * recruit.stars}")

        with col2:
            st.markdown("### Ratings")
            st.text(f"Offense: {recruit.get_offense_rating()}")
            st.text(f"Defense: {recruit.get_defense_rating()}")
            st.text(f"Fundamentals: {recruit.get_fundamentals_rating()}")

        with col3:
            st.markdown("### Interest")
            team_interest = recruit.team_interests.get(team.name, None)
            if team_interest is not None:
                st.progress(team_interest / 100)
                st.text(f"{int(team_interest)}%")
            else:
                st.text("Unknown")
                st.caption("Scout to reveal interest")

        st.markdown("---")

        # Show top schools if player has been scouted
        if team.name in recruit.scouted_by:
            top_schools = recruit.get_top_schools(5)
            if top_schools:
                st.markdown("### Top Schools")
                for i, (school_name, interest) in enumerate(top_schools, 1):
                    marker = "👉 " if school_name == team.name else "   "
                    st.text(f"{marker}{i}. {school_name} ({int(interest)}%)")
                st.markdown("---")

        # Signing period indicator
        current_week = st.session_state.current_season.current_week if st.session_state.current_season else 0
        is_early_period = 4 <= current_week <= 6
        is_regular_period = current_week >= 16
        if is_early_period:
            st.info("📝 Early Signing Period (Nov 13-20)")
        elif is_regular_period:
            st.info("📝 Regular Signing Period (April)")
        else:
            st.warning("⚠️ Not in signing period - recruits cannot commit yet")

        # Actions
        st.markdown("### RECRUITING ACTIONS")

        col1, col2, col3 = st.columns(3)

        already_scouted = team.name in recruit.scouted_by
        with col1:
            if already_scouted:
                st.button("✅ SCOUTED", use_container_width=True, disabled=True)
            else:
                if st.button("🔍 SCOUT", use_container_width=True, disabled=st.session_state.recruiting_actions_remaining <= 0):
                    success = recruit.scout_action(team)
                    if success:
                        st.session_state.recruiting_actions_remaining -= 1
                        interest = int(recruit.team_interests.get(team.name, 0))
                        st.success(f"Scouted {recruit.name} (Interest: {interest}%)")
                    else:
                        st.warning(f"Already scouted {recruit.name}")
                    st.rerun()

        with col2:
            if st.button("✈️ VISIT", use_container_width=True, disabled=st.session_state.recruiting_actions_remaining <= 0):
                success = recruit.visit_action(team, current_week)
                if success:
                    st.session_state.recruiting_actions_remaining -= 1
                    interest = int(recruit.team_interests.get(team.name, 0))
                    st.success(f"Visited {recruit.name} (Interest: {interest}%)")
                else:
                    st.warning(f"Already visited {recruit.name} this week")
                st.rerun()

        with col3:
            if recruit.scholarship_offered and team.name in recruit.offers_from:
                st.button("✅ OFFERED", use_container_width=True, disabled=True)
            else:
                if st.button("📜 OFFER", use_container_width=True, disabled=st.session_state.recruiting_actions_remaining <= 0 or available_spots <= 0):
                    recruit.offer_scholarship(team)
                    st.session_state.recruiting_actions_remaining -= 1
                    st.success(f"Offered scholarship to {recruit.name}!")
                    st.rerun()

        # Commit attempt
        if recruit.scholarship_offered and recruit.can_commit(team, current_week):
            st.markdown("---")
            if st.button(f"🎯 ATTEMPT TO CLOSE COMMITMENT", type="primary", use_container_width=True):
                success = recruit.attempt_commit(team)
                if success:
                    st.success(f"🎉 {recruit.name} COMMITTED!")
                    player = recruit.to_player()
                    team.roster.append(player)
                else:
                    interest = int(recruit.team_interests.get(team.name, 0))
                    st.error(f"❌ {recruit.name} is not ready to commit yet (Interest: {interest}%)")
                st.rerun()
        elif recruit.scholarship_offered:
            if not (is_early_period or is_regular_period):
                st.caption(f"Wait for signing period to attempt commitment")
            else:
                interest = int(recruit.team_interests.get(team.name, 0))
                st.caption(f"Need higher interest to commit (currently {interest}%)")

        # Show recruiting history
        visit_count = len(recruit.visited_by.get(team.name, []))
        st.caption(f"Scouted: {'Yes' if team.name in recruit.scouted_by else 'No'} • Visited: {visit_count}x • Offered: {'Yes' if team.name in recruit.offers_from else 'No'}")


def run_postseason_tournaments():
    """Run postseason"""
    with st.spinner("Running postseason tournaments..."):
        results = run_postseason(st.session_state.all_teams, st.session_state.game_engine)
        st.session_state.tournament_results = results

    st.balloons()
    st.success(f"**NCAA CHAMPION: {results['ncaa_champion'].name}** 🏆")
    st.info(f"**NIT CHAMPION: {results['nit_champion'].name}**")

    if st.button("CONTINUE TO OFF-SEASON"):
        advance_to_offseason()


def advance_to_offseason():
    """Advance to next season"""
    team = st.session_state.player_team
    season = st.session_state.current_season

    # Advance players (this removes graduating seniors)
    season.advance_players()

    # Have all AI teams recruit to fill their open spots
    # This happens after seniors graduate but before next season
    if st.session_state.recruiting_class:
        rc = st.session_state.recruiting_class
        for t in st.session_state.all_teams:
            if t.name != team.name:  # Skip player's team
                graduating = sum(1 for p in t.roster if p.year >= 4)
                open_spots = max(0, graduating)
                if open_spots > 0:
                    recruit_players_auto(t, rc, open_spots)

    # Reset records
    for t in st.session_state.all_teams:
        t.wins = 0
        t.losses = 0
        t.conference_wins = 0
        t.conference_losses = 0
        t.games_played = 0
        t.results = []

    # Advance year
    st.session_state.current_year += 1
    st.session_state.current_season = None
    st.session_state.recruiting_class = None  # Reset recruiting class for new year
    st.session_state.page = "recruiting"
    st.rerun()


if __name__ == "__main__":
    main()

"""
College Basketball Manager - Simple Dashboard UI
Dark mode, minimal navigation, action-focused
"""

import streamlit as st
import pandas as pd
from models import Team
from teams_data import create_all_teams, get_team_by_name, CONFERENCES
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

    conferences = ["All"] + sorted(CONFERENCES.keys())
    selected_conf = st.selectbox("Conference:", conferences)

    if selected_conf == "All":
        teams = st.session_state.all_teams
    else:
        teams = [t for t in st.session_state.all_teams if t.conference == selected_conf]

    team_data = [{
        "Team": t.name,
        "Conference": t.conference,
        "Rating": f"{t.get_team_rating():.1f}"
    } for t in teams]

    df = pd.DataFrame(team_data)
    st.dataframe(df, use_container_width=True, height=400, hide_index=True)

    team_names = [t.name for t in teams]
    selected = st.selectbox("Choose your team:", [""] + team_names)

    if selected and st.button("START CAREER", type="primary"):
        team = get_team_by_name(st.session_state.all_teams, selected)
        if team:
            st.session_state.player_team = team
            st.rerun()


def dashboard_page():
    """Main dashboard - all key info visible"""
    team = st.session_state.player_team
    season = st.session_state.current_season

    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"## {team.name}")
        st.caption(f"{team.conference} • {st.session_state.current_year} Season")
    with col2:
        if st.button("⚙️ Change Team"):
            st.session_state.player_team = None
            st.session_state.current_season = None
            st.rerun()

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
            # Simulation controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏭️ SIMULATE 1 WEEK", type="primary", use_container_width=True):
                    results = season.simulate_week()
                    st.session_state.last_results = results
                    st.rerun()
            with col2:
                if st.button("⏩ SIM TO END", use_container_width=True):
                    season.simulate_full_season()
                    st.rerun()

            # Recent results
            if hasattr(st.session_state, 'last_results') and st.session_state.last_results:
                st.markdown("### RECENT RESULTS")
                for result in st.session_state.last_results:
                    if result['home_team'] == team.name or result['away_team'] == team.name:
                        our_score = result['home_score'] if result['home_team'] == team.name else result['away_score']
                        opp_score = result['away_score'] if result['home_team'] == team.name else result['home_score']
                        opponent = result['away_team'] if result['home_team'] == team.name else result['home_team']
                        won = our_score > opp_score
                        location = "vs" if result['home_team'] == team.name else "@"

                        box_class = "win-box" if won else "loss-box"
                        result_text = "W" if won else "L"

                        st.markdown(f"""
                        <div class="{box_class}">
                            <strong>{result_text}</strong> &nbsp;&nbsp; {team.name} {our_score}, {location} {opponent} {opp_score}
                        </div>
                        """, unsafe_allow_html=True)

            # Upcoming games
            schedule = season.get_team_schedule(team)
            upcoming = [g for g in schedule if not g['played']][:5]

            if upcoming:
                st.markdown("### UPCOMING GAMES")
                for game in upcoming:
                    location = "vs" if game['is_home'] else "@"
                    game_type = "CONF" if game['is_conference'] else ""
                    st.text(f"Week {game['week']}: {location} {game['opponent']} {game_type}")


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
    tab1, tab2, tab3 = st.tabs(["ROSTER", "STATS", "ROTATION"])

    with tab1:
        show_roster(team)

    with tab2:
        show_stats(team)

    with tab3:
        manage_rotation(team)


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

        # Team averages
        st.markdown("### TEAM AVERAGES")
        col1, col2, col3 = st.columns(3)

        total_ppg = sum(p.points for p in team.roster) / team.games_played
        total_rpg = sum(p.rebounds for p in team.roster) / team.games_played
        total_apg = sum(p.assists for p in team.roster) / team.games_played

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


def league_page():
    """League standings"""
    st.markdown("## LEAGUE STANDINGS")

    view = st.radio("", ["Top 25", "Conference"], horizontal=True)

    if view == "Top 25":
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
    """Recruiting"""
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

    rc = st.session_state.recruiting_class
    commits = [r for r in rc.recruits if r.committed and r.committed_to == team.name]
    available_spots = graduating_seniors - len(commits)

    st.info(f"Class of {st.session_state.current_year + 1} • {graduating_seniors} seniors graduating • {len(commits)} commits • {available_spots} spots left")

    # Quick action
    if available_spots > 0:
        if st.button("AUTO-FILL ROSTER", type="primary"):
            recruited = recruit_players_auto(team, rc, available_spots)
            for recruit in recruited:
                player = recruit.to_player()
                team.roster.append(player)

            # Other teams recruit
            for t in st.session_state.all_teams:
                if t != team:
                    spots = 12 - len(t.roster)
                    if spots > 0:
                        recruit_players_auto(t, rc, min(spots, 3))

            st.success(f"Recruited {len(recruited)} players!")
            st.rerun()

    st.markdown("---")

    # Filter
    position = st.selectbox("Filter by Position:", ["All", "PG", "SG", "SF", "PF", "C"])
    pos_filter = None if position == "All" else position

    recruits = rc.get_available_recruits(pos_filter)[:50]

    if not recruits:
        st.info("No recruits available.")
        return

    # Recruit list
    recruit_data = []
    for r in recruits:
        recruit_data.append({
            "Rank": f"#{r.ranking}",
            "Name": r.name,
            "Pos": r.position,
            "Stars": "⭐" * r.stars,
            "Interest": f"{r.interest}%"
        })

    df = pd.DataFrame(recruit_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)

    # Show commits
    if commits:
        with st.expander(f"YOUR COMMITS ({len(commits)})"):
            for commit in commits:
                st.text(f"{'⭐' * commit.stars} {commit.name} ({commit.position}) - #{commit.ranking}")

    # Recruit selection
    recruit_names = [f"{r.name} ({r.position})" for r in recruits[:20]]
    selected = st.selectbox("Select recruit:", [""] + recruit_names)

    if selected:
        idx = recruit_names.index(selected)
        recruit = recruits[idx]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{recruit.name}**")
            st.text(f"#{recruit.ranking} {recruit.position}")
            st.text(f"{'⭐' * recruit.stars}")

        with col2:
            st.text(f"Interest: {recruit.interest}%")
            st.progress(recruit.interest / 100)

        if st.button(f"RECRUIT {recruit.name}", type="primary"):
            if available_spots <= 0:
                st.error("No scholarship spots available!")
            else:
                success = rc.recruit_player(recruit, team)
                if success:
                    st.success(f"✅ {recruit.name} committed!")
                else:
                    st.error(f"❌ {recruit.name} declined")
                st.rerun()


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

    # Advance players
    season.advance_players()

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
    st.session_state.page = "recruiting"
    st.rerun()


if __name__ == "__main__":
    main()

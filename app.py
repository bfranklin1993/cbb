"""
Streamlit web UI for College Basketball Manager
Simple, clean, intuitive interface
"""

import streamlit as st
import pandas as pd
from models import Team
from teams_data import create_all_teams, get_team_by_name, CONFERENCES
from season import Season
from tournament import run_postseason
from game_engine import GameEngine
from recruiting import RecruitingClass, recruit_players_auto


# Page configuration
st.set_page_config(
    page_title="College Basketball Manager",
    page_icon="🏀",
    layout="wide"
)

# Simple, clean CSS
st.markdown("""
<style>
    .big-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.3em;
    }
    .game-result {
        padding: 0.8em;
        margin: 0.3em 0;
        border-radius: 5px;
        border-left: 4px solid #ddd;
    }
    .game-win {
        border-left-color: #28a745;
        background-color: #f0f9f2;
    }
    .game-loss {
        border-left-color: #dc3545;
        background-color: #fcf0f1;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if 'game_initialized' not in st.session_state:
        st.session_state.all_teams = create_all_teams()
        st.session_state.player_team = None
        st.session_state.current_season = None
        st.session_state.current_year = 2024
        st.session_state.game_engine = GameEngine()
        st.session_state.game_initialized = True
        st.session_state.page = "main"
        st.session_state.recruiting_class = None


def main_menu():
    """Clean, simple main dashboard"""
    st.markdown('<div class="big-title">🏀 College Basketball Manager</div>', unsafe_allow_html=True)

    team = st.session_state.player_team

    if not team:
        # Team selection
        st.markdown("### Welcome! Select your team to begin")
        select_team()
        return

    # Main Dashboard
    st.markdown(f"## {team.name}")
    st.caption(f"{team.conference} • {st.session_state.current_year} Season")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Record", f"{team.wins}-{team.losses}")
    with col2:
        st.metric("Conference", f"{team.conference_wins}-{team.conference_losses}")
    with col3:
        st.metric("Team Rating", f"{team.get_team_rating():.1f}")
    with col4:
        roster_size = len(team.roster)
        st.metric("Roster Size", f"{roster_size}/12")

    st.markdown("---")

    # Main actions
    if not st.session_state.current_season:
        # Pre-season
        st.info("Ready to start the season!")
        if st.button("▶️ Start Season", type="primary", use_container_width=True):
            start_season()
    else:
        # In-season
        season_page()


def select_team():
    """Simple team selection"""
    conferences = ["All"] + sorted(CONFERENCES.keys())
    selected_conf = st.selectbox("Conference:", conferences)

    # Filter teams
    if selected_conf == "All":
        teams = st.session_state.all_teams
    else:
        teams = [t for t in st.session_state.all_teams if t.conference == selected_conf]

    # Create simple dataframe
    team_data = [{
        "Team": t.name,
        "Conference": t.conference,
        "Rating": f"{t.get_team_rating():.1f}"
    } for t in teams]

    df = pd.DataFrame(team_data)
    st.dataframe(df, use_container_width=True, height=400, hide_index=True)

    # Selection
    team_names = [t.name for t in teams]
    selected = st.selectbox("Choose your team:", [""] + team_names)

    if selected and st.button("Confirm", type="primary"):
        team = get_team_by_name(st.session_state.all_teams, selected)
        if team:
            st.session_state.player_team = team
            st.rerun()


def start_season():
    """Initialize season"""
    st.session_state.current_season = Season(st.session_state.all_teams, st.session_state.current_year)
    st.session_state.current_season.generate_schedule()
    st.rerun()


def season_page():
    """Clean season interface"""
    season = st.session_state.current_season
    team = st.session_state.player_team

    # Season progress
    st.progress(season.current_week / season.total_weeks, text=f"Week {season.current_week}/{season.total_weeks}")

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Simulate", "Schedule", "Roster", "Standings", "Recruiting"])

    with tab1:
        simulate_tab(season, team)

    with tab2:
        schedule_tab(season, team)

    with tab3:
        roster_tab(team)

    with tab4:
        standings_tab()

    with tab5:
        recruiting_tab_in_season()


def simulate_tab(season, team):
    """Game simulation tab"""
    if season.current_week >= season.total_weeks:
        st.success("Regular season complete!")
        if st.button("Continue to Postseason", type="primary"):
            run_postseason_phase()
        return

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Simulate 1 Week", type="primary", use_container_width=True):
            results = season.simulate_week()
            st.session_state.last_results = results
            st.rerun()

    with col2:
        if st.button("Simulate Rest of Season", use_container_width=True):
            season.simulate_full_season()
            st.rerun()

    # Show results
    if hasattr(st.session_state, 'last_results') and st.session_state.last_results:
        st.markdown("### Recent Results")

        for result in st.session_state.last_results:
            # Check if our team played
            is_our_game = result['home_team'] == team.name or result['away_team'] == team.name

            if is_our_game:
                # Our game - show result prominently
                our_score = result['home_score'] if result['home_team'] == team.name else result['away_score']
                opp_score = result['away_score'] if result['home_team'] == team.name else result['home_score']
                opponent = result['away_team'] if result['home_team'] == team.name else result['home_team']
                won = our_score > opp_score
                location = "vs" if result['home_team'] == team.name else "@"

                css_class = "game-win" if won else "game-loss"
                result_text = "W" if won else "L"

                st.markdown(f"""
                <div class="game-result {css_class}">
                    <strong>{result_text}</strong> &nbsp;&nbsp; {team.name} {our_score}, {location} {opponent} {opp_score}
                </div>
                """, unsafe_allow_html=True)


def schedule_tab(season, team):
    """Full schedule viewer"""
    st.markdown("### Season Schedule")

    schedule = season.get_team_schedule(team)

    if not schedule:
        st.info("No schedule generated yet.")
        return

    # Create schedule dataframe
    schedule_data = []
    for game in schedule:
        if game['played']:
            result = "W" if game.get('won', False) else "L"
            score = f"{game.get('team_score', 0)}-{game.get('opp_score', 0)}"
        else:
            result = "-"
            score = "-"

        location = "vs" if game['is_home'] else "@"
        game_type = "CONF" if game['is_conference'] else ""

        schedule_data.append({
            "Week": game['week'],
            "Opponent": f"{location} {game['opponent']}",
            "Type": game_type,
            "Result": result,
            "Score": score
        })

    df = pd.DataFrame(schedule_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Summary
    played = sum(1 for g in schedule if g['played'])
    total = len(schedule)
    st.caption(f"Games played: {played}/{total}")


def roster_tab(team):
    """Roster display"""
    st.markdown("### Roster")

    if not team.roster:
        st.info("No players on roster.")
        return

    # Create roster dataframe
    roster_data = []
    year_names = {1: "FR", 2: "SO", 3: "JR", 4: "SR"}

    for player in sorted(team.roster, key=lambda p: p.overall_rating(), reverse=True):
        roster_data.append({
            "Name": player.name,
            "Pos": player.position,
            "Yr": year_names.get(player.year, ""),
            "OVR": f"{player.overall_rating():.1f}",
            "PPG": f"{player.get_stats_per_game()['PPG']:.1f}" if player.games_played > 0 else "-",
            "RPG": f"{player.get_stats_per_game()['RPG']:.1f}" if player.games_played > 0 else "-",
            "APG": f"{player.get_stats_per_game()['APG']:.1f}" if player.games_played > 0 else "-"
        })

    df = pd.DataFrame(roster_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Rotation management
    with st.expander("⚙️ Manage Rotation"):
        col1, col2 = st.columns([1, 3])

        with col1:
            style = st.selectbox(
                "Rotation Style:",
                ["BALANCED", "SHORT", "DEEP"],
                index=["BALANCED", "SHORT", "DEEP"].index(team.rotation_style)
            )
            if style != team.rotation_style:
                team.rotation_style = style
                st.success(f"Changed to {style}")

        with col2:
            dist = team.get_rotation_distribution()
            st.caption(f"Minutes: Starters {int(dist[0]*100)}% • Backups {int(dist[1]*100)}% • Bench {int(dist[2]*100)}%")

        if st.button("Auto-Set Rotation by Rating"):
            team._set_default_rotation()
            st.success("Rotation updated!")


def recruiting_tab_in_season():
    """Recruiting tab during the season"""
    st.markdown("### Recruiting")

    team = st.session_state.player_team
    open_spots = 12 - len(team.roster)

    # Initialize recruiting class if not exists
    if st.session_state.recruiting_class is None:
        st.session_state.recruiting_class = RecruitingClass(
            st.session_state.current_year + 1,  # Next year's class
            len(st.session_state.all_teams)
        )

    rc = st.session_state.recruiting_class

    st.info(f"Recruiting for {st.session_state.current_year + 1} season • {open_spots} scholarships available")

    # Position filter
    position = st.selectbox("Filter by Position:", ["All", "PG", "SG", "SF", "PF", "C"], key="recruit_pos_season")
    pos_filter = None if position == "All" else position

    recruits = rc.get_available_recruits(pos_filter)[:50]

    if not recruits:
        st.warning("No recruits available.")
        return

    # Create recruit dataframe
    recruit_data = []
    for r in recruits:
        recruit_data.append({
            "Rank": f"#{r.ranking}",
            "Name": r.name,
            "Pos": r.position,
            "Stars": "⭐" * r.stars,
            "Interest": f"{r.interest}%",
            "Potential": f"{r.potential:.1f}"
        })

    df = pd.DataFrame(recruit_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=300)

    # Recruit a player
    recruit_names = [f"{r.name} ({r.position})" for r in recruits[:20]]
    selected = st.selectbox("Select recruit:", [""] + recruit_names, key="recruit_select_season")

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

        if st.button(f"Recruit {recruit.name}", type="primary", key="recruit_btn_season"):
            if open_spots <= 0:
                st.error("No scholarship spots available!")
            else:
                success = rc.recruit_player(recruit, team)
                if success:
                    player = recruit.to_player()
                    team.roster.append(player)
                    st.success(f"✅ {recruit.name} committed!")
                else:
                    st.error(f"❌ {recruit.name} declined. Interest decreased.")
                st.rerun()


def standings_tab():
    """League standings"""
    view = st.radio("View:", ["Top 25", "Conference"], horizontal=True)

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
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        # Conference standings
        conferences = sorted(CONFERENCES.keys())
        selected_conf = st.selectbox("Conference:", conferences)

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
        st.dataframe(df, use_container_width=True, hide_index=True)


def run_postseason_phase():
    """Run postseason"""
    with st.spinner("Running tournaments..."):
        results = run_postseason(st.session_state.all_teams, st.session_state.game_engine)
        st.session_state.tournament_results = results

    st.balloons()
    st.success(f"**NCAA Champion:** {results['ncaa_champion'].name} 🏆")
    st.info(f"**NIT Champion:** {results['nit_champion'].name}")

    if st.button("Continue to Off-Season"):
        advance_to_offseason()


def advance_to_offseason():
    """Off-season progression"""
    team = st.session_state.player_team
    season = st.session_state.current_season

    # Count graduating seniors
    graduating = sum(1 for p in team.roster if p.year >= 4)

    # Advance players
    season.advance_players()

    # Reset season records
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

    # Recruiting
    st.session_state.page = "recruiting"
    st.rerun()


def recruiting_page():
    """Recruiting interface"""
    st.markdown('<div class="big-title">🎓 Recruiting</div>', unsafe_allow_html=True)

    team = st.session_state.player_team
    open_spots = 12 - len(team.roster)

    st.metric("Open Scholarships", open_spots)

    if open_spots == 0:
        st.success("Roster is full!")
        if st.button("Continue to Next Season"):
            st.session_state.page = "main"
            st.rerun()
        return

    # Initialize recruiting class
    if st.session_state.recruiting_class is None:
        st.session_state.recruiting_class = RecruitingClass(
            st.session_state.current_year,
            len(st.session_state.all_teams)
        )

    rc = st.session_state.recruiting_class

    # Quick action
    if st.button("Auto-Fill Roster", type="primary"):
        recruited = recruit_players_auto(team, rc, open_spots)
        for recruit in recruited:
            player = recruit.to_player()
            team.roster.append(player)

        # Other teams recruit
        for t in st.session_state.all_teams:
            if t != team:
                spots = 12 - len(t.roster)
                if spots > 0:
                    recruit_players_auto(t, rc, spots)

        st.session_state.recruiting_class = None
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")

    # Show available recruits
    st.markdown("### Available Recruits")

    position = st.selectbox("Filter by Position:", ["All", "PG", "SG", "SF", "PF", "C"])
    pos_filter = None if position == "All" else position

    recruits = rc.get_available_recruits(pos_filter)[:50]

    if not recruits:
        st.info("No recruits available.")
        return

    # Create recruit dataframe
    recruit_data = []
    for r in recruits:
        recruit_data.append({
            "Rank": f"#{r.ranking}",
            "Name": r.name,
            "Pos": r.position,
            "Stars": "⭐" * r.stars,
            "Interest": f"{r.interest}%",
            "Potential": f"{r.potential:.1f}"
        })

    df = pd.DataFrame(recruit_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)

    # Recruit a player
    recruit_names = [f"{r.name} ({r.position}) - {r.ranking}" for r in recruits[:20]]
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

        if st.button(f"Recruit {recruit.name}", type="primary"):
            success = rc.recruit_player(recruit, team)
            if success:
                player = recruit.to_player()
                team.roster.append(player)
                st.success(f"✅ {recruit.name} committed!")
            else:
                st.error(f"❌ {recruit.name} declined. Interest decreased.")
            st.rerun()


# Main app
def main():
    init_session_state()

    # Simple sidebar
    with st.sidebar:
        st.markdown("### 🏀 Navigation")

        if st.session_state.player_team:
            st.info(f"**{st.session_state.player_team.name}**\n{st.session_state.current_year}")

        if st.button("Main Menu", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()

        if st.session_state.player_team and st.button("Change Team", use_container_width=True):
            st.session_state.player_team = None
            st.session_state.current_season = None
            st.session_state.page = "main"
            st.rerun()

        st.markdown("---")
        st.caption("College Basketball Manager")
        st.caption("358 Teams • 31 Conferences")

    # Route to pages
    page = st.session_state.get('page', 'main')

    if page == "recruiting":
        recruiting_page()
    else:
        main_menu()


if __name__ == "__main__":
    main()

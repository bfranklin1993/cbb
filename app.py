"""
Streamlit web UI for College Basketball Manager
"""

import streamlit as st
import pandas as pd
from typing import Optional
from models import Team
from teams_data import create_all_teams, get_team_by_name, CONFERENCES
from season import Season
from tournament import run_postseason
from game_engine import GameEngine
from constants import OFFENSIVE_SYSTEMS, DEFENSIVE_SYSTEMS
from recruiting import RecruitingClass, recruit_players_auto


# Page configuration
st.set_page_config(
    page_title="College Basketball Manager",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #FF6B35;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1em;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .warning-box {
        padding: 1em;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        color: #856404;
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
        st.session_state.page = "main_menu"
        st.session_state.recruiting_class = None


def main_menu():
    """Main menu page"""
    st.markdown('<h1 class="main-title">🏀 COLLEGE BASKETBALL MANAGER</h1>', unsafe_allow_html=True)

    st.markdown(f"### Current Season: **{st.session_state.current_year}**")

    if st.session_state.player_team:
        st.success(f"Coaching: **{st.session_state.player_team.name}** ({st.session_state.player_team.conference})")
        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("▶️ Start New Season", use_container_width=True):
                start_season()

        with col2:
            if st.button("📊 View Team", use_container_width=True):
                st.session_state.page = "view_team"
                st.rerun()

        with col3:
            if st.button("🔄 Change Team", use_container_width=True):
                st.session_state.player_team = None
                st.rerun()
    else:
        st.info("👋 Welcome! Select a team to begin your coaching career.")
        select_team()


def select_team():
    """Team selection interface"""
    st.markdown("## Select Your Team")

    # Conference filter
    conferences = ["All Conferences"] + sorted(CONFERENCES.keys())
    selected_conf = st.selectbox("Filter by Conference:", conferences)

    # Filter teams
    if selected_conf == "All Conferences":
        available_teams = st.session_state.all_teams
    else:
        available_teams = [t for t in st.session_state.all_teams if t.conference == selected_conf]

    # Create dataframe for display
    team_data = []
    for team in available_teams:
        team_data.append({
            "Team": team.name,
            "Conference": team.conference,
            "Rating": f"{team.get_team_rating():.1f}"
        })

    df = pd.DataFrame(team_data)

    # Display with selection
    st.dataframe(df, use_container_width=True, height=400)

    # Team selection
    team_names = [t.name for t in available_teams]
    selected_team = st.selectbox("Choose your team:", [""] + team_names)

    if selected_team and st.button("✅ Confirm Selection", type="primary"):
        team = get_team_by_name(st.session_state.all_teams, selected_team)
        if team:
            st.session_state.player_team = team
            st.success(f"You are now coaching the **{team.name}**!")
            st.rerun()


def start_season():
    """Initialize a new season"""
    st.session_state.current_season = Season(st.session_state.all_teams, st.session_state.current_year)
    st.session_state.current_season.generate_schedule()
    st.session_state.page = "season"
    st.rerun()


def season_page():
    """Season management page"""
    st.markdown(f"# {st.session_state.current_year} Season")
    st.markdown(f"### Week {st.session_state.current_season.current_week + 1} of {st.session_state.current_season.total_weeks}")

    team = st.session_state.player_team

    # Display record
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Record", f"{team.wins}-{team.losses}")
    with col2:
        st.metric("Conference Record", f"{team.conference_wins}-{team.conference_losses}")
    with col3:
        st.metric("Team Rating", f"{team.get_team_rating():.1f}")

    st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⏭️ Simulate Week", use_container_width=True, type="primary"):
            results = st.session_state.current_season.simulate_week()
            st.session_state.last_week_results = results
            st.rerun()

    with col2:
        if st.button("⏩ Simulate Rest of Season", use_container_width=True):
            st.session_state.current_season.simulate_full_season()
            st.success("Regular season complete!")
            st.rerun()

    with col3:
        if st.button("📊 View Standings", use_container_width=True):
            st.session_state.page = "standings"
            st.rerun()

    # Display last week's results if available
    if hasattr(st.session_state, 'last_week_results') and st.session_state.last_week_results:
        st.markdown("### Last Week's Results")
        for result in st.session_state.last_week_results:
            winner = "🟢" if result['winner'] == team.name else "🔴"
            conf_marker = "⭐" if result['is_conference'] else ""
            st.text(f"{winner} {result['home_team']} {result['home_score']} - {result['away_score']} {result['away_team']} {conf_marker}")

    # Check if season is over
    if st.session_state.current_season.current_week >= st.session_state.current_season.total_weeks:
        st.success("🎉 Regular season complete! Starting postseason...")
        if st.button("🏆 Continue to Postseason", type="primary"):
            run_postseason_phase()


def run_postseason_phase():
    """Run postseason tournaments"""
    with st.spinner("Running NCAA Tournament and NIT..."):
        results = run_postseason(st.session_state.all_teams, st.session_state.game_engine)
        st.session_state.tournament_results = results

    st.balloons()

    # Display results
    st.markdown("## 🏆 Tournament Results")

    ncaa_champ = results['ncaa_champion']
    nit_champ = results['nit_champion']

    st.success(f"**NCAA Champion:** {ncaa_champ.name} 🏆")
    st.info(f"**NIT Champion:** {nit_champ.name}")

    if st.button("Continue to Off-Season"):
        advance_to_offseason()


def advance_to_offseason():
    """Handle off-season progression"""
    team = st.session_state.player_team

    # Count graduating seniors
    graduating_count = sum(1 for p in team.roster if p.year >= 4)

    # Advance all players
    st.session_state.current_season.advance_players()

    st.info(f"{graduating_count} seniors graduated from your team.")

    # Reset records for all teams
    for t in st.session_state.all_teams:
        t.wins = 0
        t.losses = 0
        t.conference_wins = 0
        t.conference_losses = 0
        t.games_played = 0
        t.results = []

    # Advance year
    st.session_state.current_year += 1

    # Go to recruiting
    st.session_state.page = "recruiting"
    st.rerun()


def recruiting_page():
    """Recruiting phase"""
    st.markdown("## 🎓 Recruiting")

    team = st.session_state.player_team
    open_spots = 12 - len(team.roster)

    st.metric("Open Scholarships", open_spots)

    if open_spots == 0:
        st.success("Your roster is full!")
        if st.button("Continue to Next Season"):
            st.session_state.page = "main_menu"
            st.rerun()
        return

    # Initialize recruiting class if needed
    if st.session_state.recruiting_class is None:
        num_teams = len(st.session_state.all_teams)
        st.session_state.recruiting_class = RecruitingClass(st.session_state.current_year, num_teams)

    rc = st.session_state.recruiting_class

    # Display class quality
    quality_color = {"ELITE": "🟢", "AVERAGE": "🟡", "WEAK": "🔴"}
    st.markdown(f"### {quality_color.get(rc.class_quality, '')} {rc.class_quality} Recruiting Class")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["All Recruits", "By Position", "Your Commits", "Actions"])

    with tab1:
        display_recruits(rc, None)

    with tab2:
        position = st.selectbox("Filter by Position:", ["All", "PG", "SG", "SF", "PF", "C"])
        pos_filter = None if position == "All" else position
        display_recruits(rc, pos_filter)

    with tab3:
        display_commits(rc)

    with tab4:
        st.markdown("### Quick Actions")
        if st.button("🤖 Auto-Fill Remaining Spots", type="primary"):
            recruited = recruit_players_auto(team, rc, open_spots)
            for recruit in recruited:
                player = recruit.to_player()
                if player not in team.roster:
                    team.roster.append(player)

            # Other teams recruit
            for t in st.session_state.all_teams:
                if t != team:
                    spots = 12 - len(t.roster)
                    if spots > 0:
                        recruit_players_auto(t, rc, spots)

            st.success(f"Recruited {len(recruited)} players!")
            st.session_state.recruiting_class = None
            st.session_state.page = "main_menu"
            st.rerun()


def display_recruits(recruiting_class, position_filter=None):
    """Display available recruits"""
    recruits = recruiting_class.get_available_recruits(position_filter)[:100]

    if not recruits:
        st.warning("No recruits available at this position.")
        return

    # Create dataframe
    recruit_data = []
    for r in recruits:
        recruit_data.append({
            "Rank": f"#{r.ranking}",
            "Name": r.name,
            "Pos": r.position,
            "Stars": "⭐" * r.stars,
            "Interest": f"{r.interest}%",
            "OVR": f"{r.overall_rating():.1f}"
        })

    df = pd.DataFrame(recruit_data)
    st.dataframe(df, use_container_width=True, height=400)

    # Recruit selection
    recruit_names = [f"#{r.ranking} {r.name} ({r.position}) - {r.get_star_display()}" for r in recruits[:50]]
    selected = st.selectbox("Select recruit to view:", [""] + recruit_names)

    if selected:
        idx = recruit_names.index(selected)
        recruit = recruits[idx]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{recruit.name}**")
            st.text(f"Ranking: #{recruit.ranking}")
            st.text(f"Position: {recruit.position}")
            st.text(f"Stars: {recruit.get_star_display()}")

        with col2:
            st.text(f"Overall: {recruit.overall_rating():.1f}")
            st.text(f"Interest: {recruit.interest}%")
            st.progress(recruit.interest / 100)

        if st.button(f"🎓 Recruit {recruit.name}", type="primary"):
            success = recruiting_class.recruit_player(recruit, st.session_state.player_team)
            if success:
                player = recruit.to_player()
                st.session_state.player_team.roster.append(player)
                st.success(f"✅ {recruit.name} commits to {st.session_state.player_team.name}!")
            else:
                st.error(f"❌ {recruit.name} declined your offer. Interest decreased to {recruit.interest}%")
            st.rerun()


def display_commits(recruiting_class):
    """Display your recruiting commits"""
    commits = [r for r in recruiting_class.recruits
               if r.committed and r.committed_to == st.session_state.player_team.name]

    if not commits:
        st.info("No commits yet. Start recruiting!")
        return

    st.markdown(f"### Your Commits ({len(commits)})")

    commit_data = []
    for r in commits:
        commit_data.append({
            "Name": r.name,
            "Position": r.position,
            "Stars": "⭐" * r.stars,
            "Potential": r.potential,
            "OVR": f"{r.overall_rating():.1f}"
        })

    df = pd.DataFrame(commit_data)
    st.dataframe(df, use_container_width=True)


def view_team_page():
    """View team information"""
    team = st.session_state.player_team

    st.markdown(f"# {team.name}")
    st.markdown(f"**Conference:** {team.conference}")
    st.markdown(f"**Team Rating:** {team.get_team_rating():.1f}/10")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Roster", "Stats", "Schedule", "Rotation"])

    with tab1:
        display_roster(team)

    with tab2:
        display_player_stats(team)

    with tab3:
        display_schedule(team)

    with tab4:
        manage_rotation(team)

    if st.button("⬅️ Back to Main Menu"):
        st.session_state.page = "main_menu"
        st.rerun()


def display_roster(team):
    """Display team roster"""
    st.markdown("### Roster")

    roster_data = []
    for player in team.roster:
        year_name = {1: "FR", 2: "SO", 3: "JR", 4: "SR"}.get(player.year, "")
        roster_data.append({
            "Name": player.name,
            "Pos": player.position,
            "Year": year_name,
            "OVR": f"{player.overall_rating():.1f}",
            "SHT": f"{player.shooting:.1f}",
            "DEF": f"{player.defense:.1f}",
            "ATH": f"{player.athleticism:.1f}",
            "IQ": f"{player.basketball_iq:.1f}",
            "REB": f"{player.rebounding:.1f}"
        })

    df = pd.DataFrame(roster_data)
    st.dataframe(df, use_container_width=True)


def display_player_stats(team):
    """Display player statistics"""
    st.markdown("### Player Statistics")

    stats_data = []
    for player in team.roster:
        if player.games_played > 0:
            stats = player.get_stats_per_game()
            stats_data.append({
                "Name": player.name,
                "GP": player.games_played,
                "PPG": f"{stats['PPG']:.1f}",
                "RPG": f"{stats['RPG']:.1f}",
                "APG": f"{stats['APG']:.1f}",
                "SPG": f"{stats['SPG']:.1f}",
                "BPG": f"{stats['BPG']:.1f}"
            })

    if stats_data:
        df = pd.DataFrame(stats_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No games played yet this season.")


def display_schedule(team):
    """Display team schedule and results"""
    st.markdown("### Season Results")

    if not team.results:
        st.info("No games played yet.")
        return

    results_data = []
    for result in team.results:
        is_home = result["home_team"] == team.name
        opponent = result["away_team"] if is_home else result["home_team"]
        team_score = result["home_score"] if is_home else result["away_score"]
        opp_score = result["away_score"] if is_home else result["home_score"]
        location = "vs" if is_home else "@"
        outcome = "W" if team_score > opp_score else "L"

        results_data.append({
            "Result": outcome,
            "Score": f"{team_score}-{opp_score}",
            "Opponent": f"{location} {opponent}",
            "Type": "CONF" if result["is_conference"] else "NON-CONF"
        })

    df = pd.DataFrame(results_data)
    st.dataframe(df, use_container_width=True)


def manage_rotation(team):
    """Manage player rotation"""
    st.markdown("### Rotation Management")

    # Display current style
    dist = team.get_rotation_distribution()
    st.info(f"**Current Style:** {team.rotation_style} - Starters: {int(dist[0]*100)}%, Backups: {int(dist[1]*100)}%, Bench: {int(dist[2]*100)}%")

    # Style selector
    style = st.selectbox("Rotation Style:", ["BALANCED", "SHORT", "DEEP"], index=["BALANCED", "SHORT", "DEEP"].index(team.rotation_style))
    if style != team.rotation_style:
        team.rotation_style = style
        st.success(f"Rotation style changed to {style}")
        st.rerun()

    # Display rotations
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Starters (5)**")
        for idx in team.rotation_starters:
            if idx < len(team.roster):
                p = team.roster[idx]
                st.text(f"{p.name} ({p.position}) - {p.overall_rating():.1f}")

    with col2:
        st.markdown("**Backup (5)**")
        for idx in team.rotation_backups:
            if idx < len(team.roster):
                p = team.roster[idx]
                st.text(f"{p.name} ({p.position}) - {p.overall_rating():.1f}")

    with col3:
        st.markdown("**Deep Bench (2)**")
        for idx in team.rotation_bench:
            if idx < len(team.roster):
                p = team.roster[idx]
                st.text(f"{p.name} ({p.position}) - {p.overall_rating():.1f}")

    if st.button("🔄 Auto-Set Rotation"):
        team._set_default_rotation()
        st.success("Rotation automatically set by player ratings!")
        st.rerun()


def standings_page():
    """Display league standings"""
    st.markdown("## 📊 Standings")

    # Conference selector
    conferences = ["National Top 50"] + sorted(CONFERENCES.keys())
    selected_conf = st.selectbox("View Standings:", conferences)

    if selected_conf == "National Top 50":
        teams = sorted(st.session_state.all_teams, key=lambda t: (t.wins, -t.losses), reverse=True)[:50]
        st.markdown("### Top 50 Teams")
    else:
        teams = [t for t in st.session_state.all_teams if t.conference == selected_conf]
        teams = sorted(teams, key=lambda t: (t.conference_wins, -t.conference_losses), reverse=True)
        st.markdown(f"### {selected_conf} Standings")

    standings_data = []
    for i, team in enumerate(teams, 1):
        standings_data.append({
            "Rank": i,
            "Team": team.name,
            "Overall": f"{team.wins}-{team.losses}",
            "Conference": f"{team.conference_wins}-{team.conference_losses}",
            "Rating": f"{team.get_team_rating():.1f}"
        })

    df = pd.DataFrame(standings_data)
    st.dataframe(df, use_container_width=True, height=600)

    if st.button("⬅️ Back to Season"):
        st.session_state.page = "season"
        st.rerun()


# Main app logic
def main():
    init_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🏀 Navigation")

        if st.session_state.player_team:
            st.markdown(f"**Team:** {st.session_state.player_team.name}")
            st.markdown(f"**Year:** {st.session_state.current_year}")
            st.markdown("---")

        if st.button("🏠 Main Menu", use_container_width=True):
            st.session_state.page = "main_menu"
            st.rerun()

        if st.session_state.player_team:
            if st.button("📊 View Team", use_container_width=True):
                st.session_state.page = "view_team"
                st.rerun()

            if st.session_state.current_season:
                if st.button("🏀 Season", use_container_width=True):
                    st.session_state.page = "season"
                    st.rerun()

        st.markdown("---")
        st.markdown("### About")
        st.caption("College Basketball Manager v2.0")
        st.caption("358 Teams • 31 Conferences")
        st.caption("Made with Streamlit")

    # Route to appropriate page
    page = st.session_state.get('page', 'main_menu')

    if page == "main_menu":
        main_menu()
    elif page == "season":
        season_page()
    elif page == "recruiting":
        recruiting_page()
    elif page == "view_team":
        view_team_page()
    elif page == "standings":
        standings_page()


if __name__ == "__main__":
    main()

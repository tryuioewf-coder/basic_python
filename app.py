# =========================================
# IPL Analytics Project
# app.py
# =========================================

import os
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# -----------------------------------------
# Page Config
# -----------------------------------------

st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 IPL Analytics Dashboard")
st.markdown("---")

# -----------------------------------------
# Paths (relative to app.py location)
# -----------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

zip_path = os.path.join(BASE_DIR, "archive.zip")
extract_path = os.path.join(BASE_DIR, "data")
visuals_path = os.path.join(BASE_DIR, "visuals")

os.makedirs(extract_path, exist_ok=True)
os.makedirs(visuals_path, exist_ok=True)

# -----------------------------------------
# Extract ZIP File
# -----------------------------------------

if not os.path.exists(zip_path):
    st.error(f"❌ archive.zip not found at: `{zip_path}`")
    st.stop()

matches_path = os.path.join(extract_path, "matches.csv")
deliveries_path = os.path.join(extract_path, "deliveries.csv")

if not os.path.exists(matches_path) or not os.path.exists(deliveries_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# -----------------------------------------
# Load Dataset
# -----------------------------------------

matches = pd.read_csv(matches_path)
deliveries = pd.read_csv(deliveries_path)

# Fill Missing Winner Values
matches['winner'] = matches['winner'].fillna("No Result")

# -----------------------------------------
# Summary Stats
# -----------------------------------------

total_matches = matches.shape[0]
total_teams = matches['team1'].nunique()
total_seasons = matches['season'].nunique()
total_players = deliveries['batter'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Matches", total_matches)
col2.metric("Total Teams", total_teams)
col3.metric("Total Seasons", total_seasons)
col4.metric("Total Batters", total_players)

st.markdown("---")

# -----------------------------------------
# Team Wins Analysis
# -----------------------------------------

st.subheader("🏆 Team Wins")

team_wins = matches['winner'].value_counts()
team_wins = team_wins[team_wins.index != "No Result"]

fig1, ax1 = plt.subplots(figsize=(12, 5))
team_wins.plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_title("IPL Team Wins")
ax1.set_xlabel("Teams")
ax1.set_ylabel("Wins")
ax1.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

st.markdown("---")

# -----------------------------------------
# Toss Decision Analysis
# -----------------------------------------

st.subheader("🪙 Toss Decision Analysis")

col_toss1, col_toss2 = st.columns([1, 1])

toss_decision = matches['toss_decision'].value_counts()

with col_toss1:
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(
        toss_decision,
        labels=toss_decision.index,
        autopct='%1.1f%%',
        startangle=90
    )
    ax2.set_title("Toss Decision")
    st.pyplot(fig2)
    plt.close(fig2)

with col_toss2:
    toss_winner = matches.groupby('toss_winner')['toss_winner'].count().sort_values(ascending=False).head(10)
    fig_tw, ax_tw = plt.subplots(figsize=(6, 5))
    toss_winner.plot(kind='barh', ax=ax_tw, color='coral')
    ax_tw.set_title("Most Toss Wins (Top 10)")
    ax_tw.set_xlabel("Toss Wins")
    plt.tight_layout()
    st.pyplot(fig_tw)
    plt.close(fig_tw)

st.markdown("---")

# -----------------------------------------
# Top Run Scorers
# -----------------------------------------

st.subheader("🏏 Top 10 Run Scorers")

top_batsmen = deliveries.groupby(
    'batter'
)['batsman_runs'].sum().sort_values(ascending=False).head(10)

fig3, ax3 = plt.subplots(figsize=(12, 5))
top_batsmen.plot(kind='bar', ax=ax3, color='darkorange')
ax3.set_title("Top 10 Run Scorers")
ax3.set_xlabel("Batsman")
ax3.set_ylabel("Runs")
ax3.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

st.dataframe(
    top_batsmen.reset_index().rename(columns={'batter': 'Player', 'batsman_runs': 'Total Runs'}),
    use_container_width=True
)

st.markdown("---")

# -----------------------------------------
# Strike Rate Analysis
# -----------------------------------------

st.subheader("⚡ Top Strike Rate Players (min. 200 balls)")

runs = deliveries.groupby('batter')['batsman_runs'].sum()
balls = deliveries.groupby('batter')['ball'].count()
strike_rate = ((runs / balls) * 100).round(2)

# Filter players with at least 200 balls faced
qualified = balls[balls >= 200].index
strike_rate = strike_rate[qualified].sort_values(ascending=False).head(10)

fig4, ax4 = plt.subplots(figsize=(12, 5))
strike_rate.plot(kind='bar', ax=ax4, color='gold')
ax4.set_title("Top Strike Rate Players (min. 200 balls)")
ax4.set_xlabel("Player")
ax4.set_ylabel("Strike Rate")
ax4.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig4)
plt.close(fig4)

st.markdown("---")

# -----------------------------------------
# Wicket Analysis
# -----------------------------------------

st.subheader("🎯 Top Wicket Takers")

wickets = deliveries[deliveries['is_wicket'] == 1]
top_bowlers = wickets['bowler'].value_counts().head(10)

fig5, ax5 = plt.subplots(figsize=(12, 5))
top_bowlers.plot(kind='bar', ax=ax5, color='crimson')
ax5.set_title("Top 10 Wicket Takers")
ax5.set_xlabel("Bowler")
ax5.set_ylabel("Wickets")
ax5.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig5)
plt.close(fig5)

st.dataframe(
    top_bowlers.reset_index().rename(columns={'bowler': 'Player', 'count': 'Wickets'}),
    use_container_width=True
)

st.markdown("---")

# -----------------------------------------
# Match Scores & NumPy Stats
# -----------------------------------------

st.subheader("📊 Match Score Distribution")

match_scores = deliveries.groupby('match_id')['total_runs'].sum()
scores_array = np.array(match_scores)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
col_s1.metric("Avg Score", f"{np.mean(scores_array):.1f}")
col_s2.metric("Max Score", int(np.max(scores_array)))
col_s3.metric("Min Score", int(np.min(scores_array)))
col_s4.metric("Std Dev", f"{np.std(scores_array):.1f}")

fig6, ax6 = plt.subplots(figsize=(12, 5))
ax6.hist(scores_array, bins=20, color='mediumseagreen', edgecolor='white')
ax6.set_title("Match Score Distribution")
ax6.set_xlabel("Total Runs")
ax6.set_ylabel("Frequency")
plt.tight_layout()
st.pyplot(fig6)
plt.close(fig6)

st.markdown("---")

# -----------------------------------------
# Venue Analysis
# -----------------------------------------

st.subheader("🏟️ Top IPL Venues")

venues = matches['venue'].value_counts().head(10)

fig7, ax7 = plt.subplots(figsize=(12, 5))
venues.plot(kind='bar', ax=ax7, color='slateblue')
ax7.set_title("Top 10 IPL Venues")
ax7.set_xlabel("Venue")
ax7.set_ylabel("Matches Hosted")
ax7.tick_params(axis='x', rotation=90)
plt.tight_layout()
st.pyplot(fig7)
plt.close(fig7)

st.markdown("---")

# -----------------------------------------
# Season-wise Matches
# -----------------------------------------

st.subheader("📅 Matches Per Season")

season_matches = matches['season'].value_counts().sort_index()

fig8, ax8 = plt.subplots(figsize=(12, 5))
season_matches.plot(marker='o', ax=ax8, color='teal', linewidth=2, markersize=6)
ax8.set_title("Matches Per Season")
ax8.set_xlabel("Season")
ax8.set_ylabel("Number of Matches")
ax8.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
st.pyplot(fig8)
plt.close(fig8)

st.markdown("---")

# -----------------------------------------
# Correlation Heatmap
# -----------------------------------------

st.subheader("🔥 Correlation Heatmap (Deliveries)")

numeric_cols = deliveries.select_dtypes(include=np.number)
correlation = numeric_cols.corr()

fig9, ax9 = plt.subplots(figsize=(12, 8))
sns.heatmap(
    correlation,
    annot=True,
    cmap='coolwarm',
    fmt='.2f',
    ax=ax9
)
ax9.set_title("Correlation Heatmap")
plt.tight_layout()
st.pyplot(fig9)
plt.close(fig9)

st.markdown("---")
st.success("✅ IPL Analytics Dashboard loaded successfully!")

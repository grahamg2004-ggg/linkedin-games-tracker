import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import easyocr
from PIL import Image
import re
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="LinkedIn Game Squad", layout="wide")
GAMES = ["Queens", "Sudoku", "Zip", "Tango", "Patches"]

# Initialize OCR (This stays in memory for speed)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# --- GOOGLE SHEETS CONNECTION ---
# This connects to the URL you'll put in your Streamlit Secrets later
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(worksheet="Sheet1")

# --- HELPER: CONVERT TIME TO SECONDS ---
def time_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return (minutes * 60) + seconds
    except:
        return 9999 # Default high number for errors

# --- APP UI ---
st.title("🏆 LinkedIn Games: Group Leaderboard")
st.markdown("Upload your screenshot to compete with the squad!")

# Sidebar for Input
with st.sidebar:
    st.header("Upload Result")
    player_name = st.text_input("Your Name", placeholder="e.g., Alex")
    uploaded_file = st.file_uploader("Screenshot", type=['png', 'jpg', 'jpeg'])

if uploaded_file and player_name:
    img = Image.open(uploaded_file)
    st.image(img, caption="Preview", width=200)
    
    if st.button("Analyze & Submit"):
        with st.spinner("OCR Reading..."):
            # Convert image to list of strings
            results = reader.readtext(uploaded_file, detail=0)
            full_text = " ".join(results)
            
            # 1. Identify Game
            detected_game = next((g for g in GAMES if g.lower() in full_text.lower()), None)
            
            # 2. Identify Time (looks for 0:00 or 00:00)
            time_match = re.search(r'(\d{1,2}:\d{2})', full_text)
            
            if detected_game and time_match:
                final_time = time_match.group(1)
                seconds = time_to_seconds(final_time)
                
                # Save to Google Sheets
                new_data = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Player": player_name,
                    "Game": detected_game,
                    "Time": final_time,
                    "Seconds": seconds
                }])
                
                existing_df = get_data()
                updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                
                st.success(f"Added {detected_game} score: {final_time}!")
            else:
                st.error("Could not find game name or time. Make sure the 'You Solved It' screen is visible!")

# --- DISPLAY LEADERBOARD ---
# --- DISPLAY LEADERBOARD ---
st.divider()
all_scores = get_data()

if not all_scores.empty:
    selected_game = st.selectbox("View Leaderboard For:", GAMES)
    
    # Filter and Sort
    game_df = all_scores[all_scores['Game'] == selected_game].copy()
    
    if not game_df.empty:
        # Sort by Seconds (Fastest first)
        game_df = game_df.sort_values(by="Seconds", ascending=True).reset_index(drop=True)
        
        # Add Medal column
        def assign_medal(index):
            if index == 0: return "🥇"
            if index == 1: return "🥈"
            if index == 2: return "🥉"
            return str(index + 1)

        game_df['Rank'] = [assign_medal(i) for i in range(len(game_df))]
        
        st.subheader(f"Rankings for {selected_game}")
        # Show specific columns to the user
        st.dataframe(
            game_df[['Rank', 'Player', 'Time', 'Date']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(f"No scores yet for {selected_game}. Be the first to upload!")

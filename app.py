import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import easyocr
import re
from datetime import datetime

# --- 1. OCR CACHING ---
# This saves the model in memory so it doesn't download every time
@st.cache_resource
def load_ocr_reader():
    # 'en' is for English. You can add others like 'es' for Spanish.
    return easyocr.Reader(['en'], gpu=False) 

reader = load_ocr_reader()

# --- 2. STURDIER GOOGLE SHEETS CONNECTION ---
def get_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # We use ttl=0 to ensure we always get the freshest scores
        return conn.read(worksheet="Sheet1", ttl=0)
    except Exception as e:
        st.error("⚠️ Connection Error: Please check if the Google Sheet is 'Published to Web' and Shared as 'Editor'.")
        return pd.DataFrame() # Returns an empty table so the app doesn't crash

# --- APP CONFIG ---
st.set_page_config(page_title="LinkedIn Games Squad", layout="wide", page_icon="🏆")
GAMES = ["Queens", "Sudoku", "Zip", "Tango", "Patches"]

# --- SIDEBAR: INPUT ---
with st.sidebar:
    st.title("📤 Submit Score")
    player_name = st.text_input("Your Name", placeholder="e.g., Alex")
    method = st.radio("Entry Method", ["Scan Screenshot", "Type Manually"])
    
    found_game, found_time = None, None

    if method == "Scan Screenshot":
        uploaded_file = st.file_uploader("Upload Game Result", type=['png', 'jpg', 'jpeg'])
        if uploaded_file and st.button("🔍 Analyze Image"):
            with st.spinner("OCR engine reading pixels..."):
                # .read() is required to pass bytes to EasyOCR
                img_bytes = uploaded_file.read()
                results = reader.readtext(img_bytes, detail=0)
                full_text = " ".join(results)
                
                # Logic to find Game and Time
                found_game = next((g for g in GAMES if g.lower() in full_text.lower()), None)
                time_match = re.search(r'(\d{1,2}:\d{2})', full_text)
                if time_match: found_time = time_match.group(1)
                
                if found_game and found_time:
                    st.success(f"Detected {found_game} in {found_time}!")
                else:
                    st.warning("OCR couldn't find the game/time. Try 'Manual Entry'.")
    else:
        found_game = st.selectbox("Select Game", GAMES)
        found_time = st.text_input("Time (m:ss)", placeholder="1:24")

    if st.button("🚀 Post to Leaderboard"):
        if player_name and found_game and found_time:
            # Logic for conversion to seconds for sorting
            def to_sec(ts):
                try:
                    m, s = map(int, ts.split(':'))
                    return m * 60 + s
                except: return 9999
            
            new_entry = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Player": player_name, "Game": found_game,
                "Time": found_time, "Seconds": to_sec(found_time)
            }])
            
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                existing_data = get_data()
                updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.balloons()
                st.success("Leaderboard Updated!")
            except:
                st.error("Failed to save. Check Google Sheet 'Editor' permissions.")

# --- MAIN PAGE ---
st.title("🥇 Squad Leaderboard")
all_scores = get_data()

if not all_scores.empty:
    tabs = st.tabs(GAMES)
    for i, game in enumerate(GAMES):
        with tabs[i]:
            df = all_scores[all_scores['Game'] == game].copy()
            if not df.empty:
                df = df.sort_values(by="Seconds").reset_index(drop=True)
                df['Rank'] = [("🥇" if x==0 else "🥈" if x==1 else "🥉" if x==2 else str(x+1)) for x in range(len(df))]
                st.table(df[['Rank', 'Player', 'Time', 'Date']])
            else:
                st.info(f"No scores for {game} yet.")
else:
    st.info("The leaderboard is currently empty.")

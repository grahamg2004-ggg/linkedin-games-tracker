🏆 LinkedIn Games: Squad Leaderboard
This is a Python-based web application designed for a group of 7–8 friends to track their daily LinkedIn game results. The app uses OCR (Optical Character Recognition) to "read" screenshots and automatically updates a shared Google Sheets leaderboard.

🎮 Supported Games
The app is specifically tuned to recognize results from:

Queens 👑

Sudoku 🔢

Zip ⚡

Tango 💃

Patches 🧩

🚀 How to Use (For Players)
Play the Game: Complete your daily game on LinkedIn.

Screenshot: Take a screenshot of the "You solved it!" screen (ensure the Game Name and Time are clearly visible).

Upload: * Open our [Streamlit App URL].

Enter your name in the sidebar.

Upload your screenshot.

Compete: Click "Analyze & Submit" to see where you rank on the daily leaderboard!

🛠️ How it Works (Technical)
Frontend: Built with Streamlit.

OCR Engine: Powered by EasyOCR to extract text from images.

Database: A Google Sheet acts as the backend database via the streamlit-gsheets connector.

Sorting Logic: The app converts "Minutes:Seconds" into total seconds to ensure the leaderboard is perfectly sorted from fastest to slowest.

📂 Project Structure
app.py: The main application logic.

requirements.txt: List of Python libraries needed to run the app.

README.md: This file!

🔧 Setup Instructions (For the Admin)
Google Sheet: Create a sheet with headers: Date, Player, Game, Time, Seconds.

Secrets: In Streamlit Cloud, add your Google Sheet URL to the .toml secrets:
Ini, TOML
[connections.gsheets]
spreadsheet = "YOUR_GOOGLE_SHEET_URL"
Deploy: Connect this GitHub repo to Streamlit Cloud and wait for the build to finish.
Pro-Tip for Accuracy
For the best results, try to crop your screenshots so that the Game Title and Final Time are the main focus. If the app can't read your time, ensure the text isn't obscured by any screen overlays or "Dark Mode" filters that might lower contrast.

# 🌟 Visionary – AI Screen Detector

Visionary is a lightweight AI-powered screen detector that captures your screen and tells you what is currently displayed.
It’s especially useful for terminal monitoring and quick screen summaries.

# 🚀 Features

🖥️ Screen Detection – Captures the current screen or terminal window.

🔍 AI-Powered Analysis – Identifies visible content (text, windows, icons).

📢 Simple Output – Prints a description of what’s on screen in the terminal.

🔒 Secure API Key Management – Uses .env for safe API storage.

# 🛠️ Installation

1. Clone the repository
git clone https://github.com/Arnav301/Visionary.git
cd visionary

2. Install dependencies
pip install -r requirements.txt

3. Add your API key in .env

Create a .env file:

API_KEY=your_api_key_here

4. Start the Server

   python app.py
   
6. Start detector

   python auto_screen_analysis.py

# ⚙️ Usage

Once running, Visionary will wait for commands:

==================================================
Press ENTER to capture and analyze your current screen
Type 'quit' to exit
==================================================
Command:


✅ Press ENTER → Visionary captures your screen and prints a short description.
✅ Type quit → Exit Visionary.

Example Output:

[Visionary]: Detected a terminal window with Python running. 
[Visionary]: Text on screen includes 'Initializing server...' and 'Port 4000 open'.

# 🧩 Tech Stack

Python 🐍

OpenCV – Screen capture

Tesseract OCR – Text recognition (optional, for terminals)

AI Vision API – For generating natural descriptions

python-dotenv – API key managemen

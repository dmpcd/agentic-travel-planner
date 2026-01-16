@echo off
echo Starting AI Travel Planner Streamlit App...
echo.
cd /d %~dp0
call ..\venv\Scripts\activate.bat
streamlit run app.py
pause

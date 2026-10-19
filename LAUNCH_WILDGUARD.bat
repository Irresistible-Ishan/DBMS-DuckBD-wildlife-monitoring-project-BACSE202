@echo off
title WildGuard - Wildlife Conservation Platform
color 0A
echo.
echo  ============================================================
echo    WILDGUARD - Wildlife Conservation ^& IoT Telemetry Platform
echo    Powered by DuckDB + Streamlit + Plotly
echo  ============================================================
echo.
echo  [1] Initializing database (if not already done)...
python init_db.py
echo.
echo  [2] Launching Streamlit App...
echo      Open browser at: http://localhost:8501
echo.
streamlit run app.py
pause

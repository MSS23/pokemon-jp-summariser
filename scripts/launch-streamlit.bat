@echo off
echo ========================================
echo   Pokemon VGC Summariser - Streamlit
echo ========================================
echo.

cd streamlit-app
echo Starting Streamlit application...
echo URL: http://localhost:8501
echo.
python -m streamlit run Summarise_Article.py --server.port 8501

pause 
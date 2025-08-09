@echo off
echo Setting up Pokemon Translation Web App...
echo.

echo Installing Streamlit dependencies...
cd streamlit-app
pip install -r requirements.txt
cd ..

echo.
echo Installing React dependencies...
cd react-app
npm install
cd ..

echo.
echo Setup complete!
echo.
echo To run the applications:
echo - Streamlit: launch-streamlit.bat
echo - React: launch-react.bat
echo.
echo Don't forget to set up your Gemini API key!
echo See GEMINI_SETUP.md for instructions.
pause 
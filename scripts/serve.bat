@echo off
echo Starting Jekyll server...
echo.
echo Open http://127.0.0.1:4000 in your browser
echo Press Ctrl+C to stop the server
echo.
jekyll serve --host 127.0.0.1 --port 4000 --watch
pause


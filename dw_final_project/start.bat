@echo off
REM Start the CASI Financial Data Warehouse locally
REM Prerequisites: Python 3.12+, Node.js 18+, Cassandra running on localhost:9042

echo === Starting Backend ===
cd /d "%~dp0backend"
start "CASI Backend" cmd /k "pip install -r requirements.txt >nul 2>&1 & uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo === Starting Frontend ===
cd /d "%~dp0frontend"
start "CASI Frontend" cmd /k "npm install >nul 2>&1 & npm run dev"

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Make sure Cassandra is running on localhost:9042
echo   (e.g. docker run -d --name cassandra -p 9042:9042 cassandra:5.0)

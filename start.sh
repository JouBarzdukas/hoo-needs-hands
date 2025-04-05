set -e
echo "🔁 Starting full stack..."
echo "🧹 Clearing backend/output.txt..."
> backend/output.txt
echo "📦 Activating Python virtual environment..."
if [ -f backend/venv/bin/activate ]; then
    source backend/venv/bin/activate
elif [ -f backend/venv/Scripts/activate ]; then
    source backend/venv/Scripts/activate
else
    echo "❌ Could not find virtual environment activation script."
    exit 1
fi
echo "🛰️ Launching backend_watcher (SSE stream) on port 8000..."
cd backend_watcher
uvicorn main:app --host 127.0.0.1 --port 8000 --reload &
WATCHER_PID=$!
cd ..
echo "🤖 Starting backend agent/voice system..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..
echo "💻 Launching Electron frontend..."
cd electron-app
npm run dev &
FRONTEND_PID=$!
cd ..
echo "✅ All services started successfully."
echo "🔧 To stop everything, run: kill $WATCHER_PID $BACKEND_PID $FRONTEND_PID"
wait

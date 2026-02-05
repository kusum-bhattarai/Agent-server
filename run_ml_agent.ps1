$PORT = 8000

Write-Host "--------------------------------------"
Write-Host " Magic Leap Local Agent Dev Script"
Write-Host "--------------------------------------"

# 1) Verify adb
if (-not (Get-Command adb -ErrorAction SilentlyContinue)) {
    Write-Host "❌ adb not found. Install Android platform-tools and add to PATH."
    exit
}

# 2) Check device
Write-Host "🔍 Checking Magic Leap connection..."
$devices = adb devices | Select-String "device$"

if (-not $devices) {
    Write-Host "❌ No Magic Leap device detected."
    Write-Host "➡ Enable Developer Mode + USB Debugging on ML2"
    exit
}

Write-Host "✅ Magic Leap detected."

# 3) Reverse port
Write-Host "🔁 Setting up adb reverse tcp:$PORT → tcp:$PORT"
adb reverse tcp:$PORT tcp:$PORT

# 4) Start server
Write-Host "🚀 Starting FastAPI server on localhost:$PORT"
Write-Host "--------------------------------------"

uvicorn main:app --host 127.0.0.1 --port $PORT --reload

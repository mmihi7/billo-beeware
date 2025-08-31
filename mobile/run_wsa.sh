#!/bin/bash

# WSA Autoconnect and Run Script for Billo
# Save this as run_wsa.sh in your project root

# Exit on error
set -e

echo "🔍 Looking for WSA ADB port..."

# Find WSA's ADB port
WSA_PORT=$(netstat -ano | grep 'LISTENING' | grep '127.0.0.1' | grep -E ':58[0-9]{2}' | awk '{print $4}' | cut -d':' -f2 | head -1)

if [ -z "$WSA_PORT" ]; then
    echo "❌ Could not find WSA ADB port. Is WSA running with Developer Mode enabled?"
    echo "💡 Make sure to enable 'Developer Mode' in WSA settings and restart WSA if needed."
    exit 1
fi

WSA_ADDRESS="127.0.0.1:$WSA_PORT"

echo "📱 Found WSA at $WSA_ADDRESS"

# Kill any existing ADB server to avoid conflicts
echo "🔄 Restarting ADB server..."
adb kill-server >/dev/null 2>&1

# Connect to WSA
echo "🔌 Connecting to WSA..."
adb connect $WSA_ADDRESS

# Wait for device to be ready
echo -n "⏳ Waiting for device to be ready..."
adb wait-for-device
echo "✅ Device ready!"

# Uninstall previous version if needed
# Uncomment the line below if you want to force reinstall each time
# echo "🗑️  Uninstalling previous version..."
# adb uninstall com.billo >/dev/null 2>&1 || true

# Build and run the app
echo "🚀 Building and launching Billo..."
cd "$(dirname "$0")"  # Change to script directory
briefcase run android -d $WSA_ADDRESS

echo "✨ All done! Check WSA for your app."
echo "📝 To view logs: adb logcat | grep -i billo"

# iOS Setup Checklist

This checklist turns the SwiftUI skeleton in `ios/NuvoraIOS/` into a runnable Xcode app.

## 1. Create the Xcode project

1. Open Xcode
2. Choose `Create a new project`
3. Select `iOS` -> `App`
4. Product Name: `NuvoraIOS`
5. Interface: `SwiftUI`
6. Language: `Swift`
7. Testing System: `Swift Testing` or default
8. Save the project anywhere you want

## 2. Replace the starter files

Copy these folders from this repo into the Xcode project:

- `ios/NuvoraIOS/API`
- `ios/NuvoraIOS/App`
- `ios/NuvoraIOS/Models`
- `ios/NuvoraIOS/Services`
- `ios/NuvoraIOS/ViewModels`
- `ios/NuvoraIOS/Views`

When dragging into Xcode:

- Choose `Copy items if needed`
- Choose `Create groups`

Delete the default starter app files if they conflict.

## 3. Update Info.plist

Add:

- `Privacy - Microphone Usage Description`
  - Example value: `Nuvora needs microphone access so you can record voice health entries.`

## 4. Set the API base URL

Edit:

- `ios/NuvoraIOS/API/APIEnvironment.swift`

Use one of these:

- Simulator with local backend:
  - `http://127.0.0.1:5000`
- Real device with local backend:
  - replace with your Mac's LAN IP, for example `http://192.168.1.20:5000`
- Render:
  - `https://your-service.onrender.com`

## 5. Run the backend first

In this repo:

```bash
cd /Users/xiaolaohu/nuvora
source .venv/bin/activate
flask db upgrade
python app.py
```

Make sure these env vars are set:

- `OPENAI_API_KEY`
- `SECRET_KEY`
- `DATABASE_URL` if not using local SQLite

## 6. First app test flow

1. Launch app in simulator
2. Register a new account
3. Confirm dashboard opens
4. Submit text input
5. Confirm history list refreshes
6. Record audio
7. Upload audio
8. Confirm parsed result appears

## 7. If running on a real device

You will likely need:

- backend reachable on the same Wi-Fi
- firewall/network access allowed
- `APIEnvironment.baseURL` changed from localhost to your Mac LAN IP

## 8. Known MVP limitations

- No password reset
- No polished loading/error UX
- No production app icon / launch assets
- No App Store privacy materials yet

## 9. Recommended next steps

1. Create the Xcode project
2. Verify login + history + text submit
3. Verify voice recording on real device
4. Add account deletion
5. Prepare privacy policy and App Store assets

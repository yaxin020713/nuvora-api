# Nuvora iOS MVP

This folder contains a paste-ready SwiftUI app skeleton for the current Flask backend.

## Recommended setup

1. Open Xcode and create a new iOS App project named `NuvoraIOS`
2. Choose `SwiftUI` + `Swift`
3. Copy the files in this folder into the Xcode project
4. Add `NSMicrophoneUsageDescription` to the app's `Info.plist`
5. Update `APIEnvironment.baseURL`

## Backend requirements

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /health-data`
- `POST /health-data`
- `POST /parse-text`
- `POST /whisper`

## Notes

- Auth uses Bearer token storage in Keychain
- Voice recording uses `AVAudioRecorder`
- The dashboard is intentionally simple so you can iterate quickly

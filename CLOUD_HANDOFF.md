# Nuvora Cloud Handoff

This file captures the important deployment and iOS handoff details so the project can be resumed on another Mac.

## Source of truth

- GitHub repo: `https://github.com/yaxin020713/nuvora-api.git`
- Current branch: `main`
- Latest synced backend/frontend commit before this handoff:
  - `c237624` Add account deletion flow
- Latest synced iOS skeleton commit before this handoff:
  - `153f245` Add SwiftUI iOS app skeleton

## Existing Apple app identity

- App name: `Nuvora`
- Bundle identifier: `com.yaxinzhu.nuvora`
- Existing TestFlight version history shows:
  - latest known version: `1.0.1`
  - latest known build: `53`

When recreating the Xcode project on another Mac:

- Use bundle id: `com.yaxinzhu.nuvora`
- Suggested next upload version: `1.0.2`
- Suggested next upload build: `54` or higher

## Existing backend deployment

- Render service: `nuvora-api`
- Render base URL:
  - `https://nuvora-api-kili.onrender.com`
- Health check endpoint:
  - `https://nuvora-api-kili.onrender.com/status`

Expected iOS API base URL:

```swift
enum APIEnvironment {
    static let baseURL = URL(string: "https://nuvora-api-kili.onrender.com")!
}
```

## Required environment variables

Backend requires:

- `OPENAI_API_KEY`
- `SECRET_KEY`
- `DATABASE_URL`
- `BETA_INVITE_ONLY` (optional, set `true` for closed beta)
- `ADMIN_API_KEY` (optional, used for invite code management)
- `APPLE_SIGN_IN_AUDIENCE` (optional, defaults to `com.yaxinzhu.nuvora`)

## iOS source files already in repo

The SwiftUI app skeleton is already saved in git here:

- `ios/NuvoraIOS/API`
- `ios/NuvoraIOS/App`
- `ios/NuvoraIOS/Models`
- `ios/NuvoraIOS/Services`
- `ios/NuvoraIOS/ViewModels`
- `ios/NuvoraIOS/Views`
- `ios/README.md`
- `ios/SETUP_CHECKLIST.md`

Important:

- The temporary `.xcodeproj` created locally during setup was **not** found inside this repository, so it is not part of git.
- On the next Mac, create a fresh iOS App project in Xcode and import the files above.

## Why TestFlight upload failed on this Mac

- Installed Xcode version on this Mac: `15.4 (15F31d)`
- Apple upload validation now requires at least iOS 18 SDK / Xcode 16 or later
- Result: this Mac cannot currently upload new TestFlight builds

## Rebuild checklist on the next Mac

1. Install a current Xcode version that supports App Store upload requirements
2. Clone this repo
3. Create a new iOS `App` project in Xcode
4. Use bundle id `com.yaxinzhu.nuvora`
5. Set version/build to `1.0.2 (54)` or newer
6. Import the folders from `ios/NuvoraIOS`
7. Add `Privacy - Microphone Usage Description`
8. Point `APIEnvironment.swift` to Render
9. Fill AppIcon completely
10. Archive and upload through Organizer

## Backend/product state already completed

- Flask backend running on Render
- token auth for iOS
- session auth for web
- closed-beta invite code system
- Sign in with Apple backend support
- account deletion flow
- health data endpoints
- text parsing endpoint
- whisper upload endpoint
- SwiftUI iOS skeleton ready

## Closed beta endpoints already in repo

- `GET /beta/access`
- `POST /beta/invite-codes/validate`
- `POST /auth/apple`
- `GET /admin/invite-codes` with `X-Admin-Key`
- `POST /admin/invite-codes` with `X-Admin-Key`
- `PATCH /admin/invite-codes/<code>` with `X-Admin-Key`
- CLI helper: `flask create-invite-code`

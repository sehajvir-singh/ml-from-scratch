# Doorman 🚪

**A smart bouncer for your phone.**

Doorman keeps your distracting apps (TikTok, Instagram, YouTube, X…) behind a door.
When you open one, Doorman shows you one line about your day and asks **why**.
Say a good reason and you get a short pass. When the time is up, the door closes again.

| When | What happens |
|---|---|
| You open TikTok | Block screen: *"Deck review in 47 min · 6th open today"* |
| You tap **Ask Doorman** | A notification appears. Tap it, then say why: *"reply to Maya"* |
| Doorman decides | *"Granted: 3 minutes to reply. Then out."* The countdown runs in the Dynamic Island |
| Time is up | The app locks again by itself. Later: *"Did you reply to Maya?"* |
| At night | **Night door:** only very short, real reasons get in |
| In the morning | **Morning door:** set your first task before scrolling |
| Every week | **Attention Wrapped:** *"212 opens, 61% just checking, worst hour 10pm"* |

Everything runs **on your iPhone**. The AI is Apple's on-device model (Apple Intelligence, iOS 26+).
On phones without it, Doorman uses built-in rules. No server, no account, no data leaves the phone.

---

## 1. What you need

- A Mac with **Xcode** (the latest version from the Mac App Store)
- An **iPhone** with iOS 17 or newer. Screen Time blocking does **not** work in the Simulator, so use a real iPhone.
- An **Apple ID**. A free account works for testing on your own phone.

## 2. Open the project

1. Download this folder (`doorman-ios`).
2. Double-click **`Doorman.xcodeproj`**.

> If `Doorman.xcodeproj` is missing, create it from `project.yml`:
> ```bash
> brew install xcodegen
> cd doorman-ios
> xcodegen generate
> ```

## 3. Set your team and IDs (one time)

Bundle IDs must be unique to you. Pick a prefix, for example `com.yourname.doorman`.

1. In Xcode, click the blue **Doorman** project at the top left.
2. For **each of the 5 targets** (Doorman, DoormanMonitor, DoormanShieldConfig, DoormanShieldAction, DoormanWidgets):
   - Open **Signing & Capabilities**.
   - Set **Team** to your Apple ID.
   - Change the **Bundle Identifier** to start with your prefix. Keep each target's ending:
     - `com.yourname.doorman`
     - `com.yourname.doorman.monitor`
     - `com.yourname.doorman.shieldconfig`
     - `com.yourname.doorman.shieldaction`
     - `com.yourname.doorman.widgets`
   - Under **App Groups**, replace `group.com.doorman.app` with `group.com.yourname.doorman`.
3. Open `Shared/Core/AppGroup.swift` and change `id` to the same App Group name.

Tip: you can make these changes in `project.yml` instead and run `xcodegen generate` again.

## 4. Run it

1. Plug in your iPhone and pick it at the top of Xcode.
2. Press **▶ Run**.
3. On the iPhone, if asked, trust the developer in **Settings → General → VPN & Device Management**.
4. In Doorman, allow **Screen Time**, pick your apps, and tap **Close the door**.
5. Open one of the picked apps. You should see the Doorman block screen.

## 5. Before the App Store

| Step | Why |
|---|---|
| **Request the Family Controls (Distribution) entitlement** from Apple | Needed to ship any app that blocks apps. Development works without it. Search "Family Controls entitlement request" on developer.apple.com. Do this early, because approval takes time. |
| Create the subscriptions in **App Store Connect** | Product IDs used in the code: `doorman.pro.yearly`, `doorman.pro.monthly`, `doorman.pro.lifetime` |
| Add an **App Icon** | `Doorman/Assets.xcassets/AppIcon` is empty |
| Write a **privacy policy** | Say clearly: no data leaves the phone |
| Have a **patent lawyer** check one sec's US patent 12,468,828 | Doorman uses Apple's shield, not one sec's Shortcuts method, but get it checked |

## 6. How the code is organised

```
doorman-ios/
├── project.yml              ← Xcode project spec (XcodeGen)
├── Package.swift            ← lets you run the core tests with `swift test`
├── Shared/
│   ├── Core/                ← pure Swift rules, used by every target (unit tested)
│   │   ├── DoorPolicy.swift     night/morning door, pass limits, fallback "AI"
│   │   ├── SharedStore.swift    data shared between app and extensions (App Group)
│   │   ├── ShieldCopy.swift     text on the block screen
│   │   ├── Wrapped.swift        weekly Attention Wrapped numbers
│   │   └── Models.swift
│   ├── Shielding/ShieldManager.swift   lock / unlock / re-lock (Screen Time)
│   └── LiveActivity/                   countdown data for the Dynamic Island
├── Doorman/                 ← the app (SwiftUI screens, AI judge, passes, store)
├── DoormanMonitor/          ← re-locks apps when a pass ends, runs the night door
├── DoormanShieldConfig/     ← draws the block screen
├── DoormanShieldAction/     ← "Ask Doorman" button → notification
├── DoormanWidgets/          ← Dynamic Island countdown + Lock Screen widget
└── Tests/CoreTests/         ← unit tests for Shared/Core
```

### Run the tests

```bash
cd doorman-ios
swift test
```

## 7. Known limits of iOS (not bugs)

- **The block screen cannot open Doorman directly.** Apple doesn't allow it, so "Ask Doorman" sends a notification and you tap it. Allow notifications for the smoothest flow. You can also open Doorman yourself and tap **Ask for a pass**.
- **Doorman blocks whole apps.** It can't allow "DMs only" inside Instagram.
- **Short passes:** Apple's timer has a 15-minute minimum, so Doorman uses an early-warning trick to re-lock after 1–14 minutes. Test this on your own phone.

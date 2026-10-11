# TGLite Android

Minimal Android WebView UI with Telethon embedded through Chaquopy.

## Build on GitHub Actions
1. Create a GitHub repository and upload all files from this project.
2. Push to the `main` branch, or run Actions -> Build TGLite APK -> Run workflow.
3. Open the workflow run and download the `TGLite-debug-apk` artifact.
4. Extract `app-debug.apk` and install it on your Android device.

## Notes
- The app uses the existing session name `tglite`.
- Replace `api_hash` in `app/src/main/python/teleclient.py` yourself as planned.
- The first build may take several minutes while Chaquopy installs Python packages.
- This is an initial prototype. It refreshes chats/messages every 4 seconds while open.
- Do not share the APK/session file/API credentials publicly.

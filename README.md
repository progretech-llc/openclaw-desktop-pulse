# OpenClaw Desktop Pulse

A GNOME Shell 50 wallpaper overlay that pulses when local OpenClaw agents have recent session activity. Adapted from the ProgreTech workstation presence display and intentionally separated from its private factory runtime.

The bridge scans `~/.openclaw/agents/*/sessions/*.jsonl` **file modification times only**. It never reads messages or session content, and writes a compact JSON frame to `$XDG_RUNTIME_DIR/openclaw-desktop-pulse/frame.json` with agent IDs and timestamps. A recent file write means activity was observed; it does not prove a tool is currently running or identify the task. Deleted/compressed session archives are ignored. The wallpaper extension reads that frame, shows the latest active agent, and animates three translucent rings. If there is no fresh frame, it displays a quiet waiting state.

Requirements: Ubuntu/GNOME Shell 50, Python 3, a user systemd session, and local OpenClaw sessions. Other GNOME Shell versions are untested. The extension uses GNOME Shell's internal background group API, which may change between releases.

```bash
./install.sh
systemctl --user enable --now openclaw-desktop-pulse.service
# Log out and back in so GNOME registers the new extension, then:
gnome-extensions enable openclaw-desktop-pulse@progretech.com
```

`./install.sh --enable` attempts to start and enable both. The extension can be disabled without stopping the bridge: `gnome-extensions disable openclaw-desktop-pulse@progretech.com`. To pause across logins, also run `systemctl --user disable --now openclaw-desktop-pulse.service`.

The bridge can be tested without installation:

```bash
python3 bridge.py --once --sessions-root /path/to/agents --frame-path /tmp/openclaw-pulse-frame.json
```

`--active-seconds` defaults to 20 and `--interval` to 2. Applications that already produce normalized presence can write the same local frame contract (`schema_version`, `updated_at` Unix seconds, `state`, `agent`, `cue`, `color`) instead of running this bridge. Keep the frame in user-only storage. Do not run multiple producers against the same path.

This package ships no personal wallpapers, factory configuration, credentials, or OpenClaw transcripts. It does not modify OpenClaw itself.

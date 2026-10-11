#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
uuid=openclaw-desktop-pulse@progretech.com
extension_dir="${XDG_DATA_HOME:-$HOME/.local/share}/gnome-shell/extensions/$uuid"
unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
bridge_dir="${XDG_DATA_HOME:-$HOME/.local/share}/openclaw-desktop-pulse"
mkdir -p "$extension_dir" "$unit_dir" "$bridge_dir"
install -m 644 "$root/extension/extension.js" "$root/extension/stylesheet.css" "$root/extension/metadata.json" "$extension_dir/"
install -m 755 "$root/bridge.py" "$bridge_dir/bridge.py"
cat > "$unit_dir/openclaw-desktop-pulse.service" <<EOF
[Unit]
Description=OpenClaw desktop pulse metadata bridge

[Service]
Type=simple
ExecStart=$bridge_dir/bridge.py
Restart=on-failure

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
if [[ ${1:-} == --enable ]]; then
    systemctl --user enable --now openclaw-desktop-pulse.service
    gnome-extensions enable "$uuid" || echo 'Log out and back in to load the new extension, then enable it.' >&2
fi
printf 'Installed. Enable the service and extension when ready; a GNOME logout/login may be required.\n'

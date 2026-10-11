#!/usr/bin/env python3
"""Project OpenClaw session file activity into a small, local desktop pulse frame."""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path


def snapshot(root: Path, now: float, active_seconds: float) -> dict:
    agents = []
    if root.is_dir():
        for directory in sorted(root.iterdir()):
            session_dir = directory / 'sessions'
            if not directory.is_dir() or not session_dir.is_dir():
                continue
            latest = max((p.stat().st_mtime for p in session_dir.glob('*.jsonl') if p.is_file()), default=0)
            if latest:
                agents.append({'name': directory.name, 'last_activity': latest})
    agents.sort(key=lambda item: item['last_activity'], reverse=True)
    recent = [item for item in agents if 0 <= now - item['last_activity'] <= active_seconds]
    leader = recent[0] if recent else None
    color = '#' + hashlib.sha256(leader['name'].encode()).hexdigest()[:6] if leader else '#8092ad'
    return {
        'schema_version': 1,
        'updated_at': now,
        'state': 'processing' if leader else 'available',
        'agent': leader['name'] if leader else None,
        'cue': f"{leader['name']} active" if leader else 'Waiting for activity',
        'color': color,
        'active_agents': [item['name'] for item in recent],
        'agents': agents,
        'source': 'openclaw-session-mtime',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sessions-root', type=Path, default=Path.home() / '.openclaw' / 'agents')
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
    parser.add_argument('--frame-path', type=Path, default=runtime / 'openclaw-desktop-pulse' / 'frame.json')
    parser.add_argument('--active-seconds', type=float, default=20)
    parser.add_argument('--interval', type=float, default=2)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    if args.active_seconds <= 0 or args.interval <= 0:
        parser.error('intervals must be positive')
    frame_path = args.frame_path.expanduser()
    frame_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    while True:
        frame = snapshot(args.sessions_root.expanduser(), time.time(), args.active_seconds)
        temporary = frame_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(frame, separators=(',', ':')) + '\n')
        os.chmod(temporary, 0o600)
        temporary.replace(frame_path)
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == '__main__':
    main()

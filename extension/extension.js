import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const FRAME = GLib.build_filenamev([GLib.get_user_runtime_dir(), 'openclaw-desktop-pulse', 'frame.json']);
const COLOR = /^#[0-9a-fA-F]{6}$/;

export default class OpenClawDesktopPulse extends Extension {
    enable() {
        this._phase = 0;
        this._state = 'available';
        this._color = '#8092ad';
        this._pulse = new St.Widget({style_class: 'oc-pulse', reactive: false});
        this._rings = [0, 1, 2].map(index => {
            const ring = new St.Widget({style_class: `oc-pulse-ring oc-pulse-ring-${index}`});
            ring.set_pivot_point(0.5, 0.5);
            this._pulse.add_child(ring);
            return ring;
        });
        this._label = new St.Label({style_class: 'oc-pulse-label', text: 'OpenClaw · waiting'});
        this._pulse.add_child(this._label);
        Main.layoutManager._backgroundGroup.add_child(this._pulse);
        this._position();
        this._monitorSignal = Main.layoutManager.connect('monitors-changed', () => this._position());
        this._poll();
        this._pollId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 2, () => {
            this._poll();
            return GLib.SOURCE_CONTINUE;
        });
        this._animationId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 80, () => {
            this._animate();
            return GLib.SOURCE_CONTINUE;
        });
    }

    disable() {
        for (const id of [this._pollId, this._animationId])
            if (id) GLib.Source.remove(id);
        if (this._monitorSignal) Main.layoutManager.disconnect(this._monitorSignal);
        this._pulse?.destroy();
        this._pulse = null;
    }

    _position() {
        const monitor = Main.layoutManager.primaryMonitor;
        const width = monitor?.width ?? 1920;
        const height = monitor?.height ?? 1080;
        const size = Math.min(width, height) * 0.72;
        this._pulse.set_position(monitor?.x ?? 0, monitor?.y ?? 0);
        this._pulse.set_size(width, height);
        this._rings.forEach((ring, index) => {
            const diameter = size * (1 - index * 0.2);
            ring.set_size(diameter, diameter);
            ring.set_position((width - diameter) / 2, (height - diameter) / 2);
        });
        this._label.set_position(24, height - 48);
    }

    _poll() {
        try {
            const [ok, bytes] = GLib.file_get_contents(FRAME);
            if (!ok) throw new Error('No frame');
            const frame = JSON.parse(new TextDecoder().decode(bytes));
            if (Math.abs(Date.now() / 1000 - frame.updated_at) > 10) throw new Error('Stale frame');
            this._state = frame.state === 'processing' ? 'processing' : 'available';
            this._color = COLOR.test(frame.color) ? frame.color : '#8092ad';
            const cue = typeof frame.cue === 'string' ? frame.cue.slice(0, 60) : 'OpenClaw';
            this._label.set_text(`OpenClaw · ${cue}`);
        } catch (_error) {
            this._state = 'available';
            this._color = '#8092ad';
            this._label.set_text('OpenClaw · waiting');
        }
        for (const ring of this._rings) ring.set_style(`border-color: ${this._color};`);
        this._label.set_style(`color: ${this._color};`);
    }

    _animate() {
        this._phase += 0.09;
        const activity = this._state === 'processing' ? 1 : 0.3;
        this._rings.forEach((ring, index) => {
            const wave = (Math.sin(this._phase - index * 0.7) + 1) / 2;
            ring.set_scale(0.985 + wave * 0.05 * activity, 0.985 + wave * 0.05 * activity);
            ring.set_opacity(Math.round(32 + wave * 110 * activity));
        });
    }
}

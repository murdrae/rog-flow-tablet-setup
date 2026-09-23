#!/usr/bin/env python3
import os
import sys
import time
import json
import subprocess
from evdev import InputDevice, list_devices, ecodes

# Swipe threshold in raw digitizer units (~15mm on a 3408x2064 panel)
THRESHOLD = 180

def find_real_touch_device():
    """Scan and match the physical touchscreen panel."""
    for path in list_devices():
        try:
            dev = InputDevice(path)
            caps = dev.capabilities()
            if ecodes.EV_ABS in caps:
                abs_codes = [code for code, _ in caps[ecodes.EV_ABS]]
                if ecodes.ABS_MT_POSITION_X in abs_codes:
                    return path, dev.name
        except Exception:
            continue
    return None, None

def get_monitor_transform():
    """Fetch current monitor transform from Hyprland."""
    try:
        res = subprocess.run(['hyprctl', 'monitors', '-j'], capture_output=True, text=True, timeout=1)
        if res.returncode == 0:
            monitors = json.loads(res.stdout)
            for m in monitors:
                if m.get('name') == 'eDP-1' or m.get('focused'):
                    return m.get('transform', 0)
    except Exception:
        pass
    return 0

def adjust_for_transform(dx, dy, transform):
    """Adjust physical swipe vectors according to screen rotation."""
    if transform == 1:       # 90 deg clockwise
        return dy, -dx
    elif transform == 2:     # 180 deg
        return -dx, -dy
    elif transform == 3:     # 270 deg
        return -dy, dx
    return dx, dy            # 0 normal

def send_hypr_dispatch(lua_cmd, log_msg=""):
    """Dispatch Hyprland Lua command with proper environment."""
    env = os.environ.copy()
    uid = str(os.getuid())
    env['XDG_RUNTIME_DIR'] = f"/run/user/{uid}"
    hypr_dir = f"/run/user/{uid}/hypr/"
    if os.path.exists(hypr_dir):
        sigs = [s for s in os.listdir(hypr_dir) if not s.endswith(('.lock', '.sock'))]
        if sigs:
            env['HYPRLAND_INSTANCE_SIGNATURE'] = sigs[0]

    if 'WAYLAND_DISPLAY' not in env:
        env['WAYLAND_DISPLAY'] = 'wayland-1'

    res = subprocess.run(['hyprctl', 'dispatch', lua_cmd], env=env, capture_output=True, text=True)
    if res.returncode == 0:
        if log_msg:
            print(f"[Gesture] {log_msg} -> {res.stdout.strip()}", flush=True)
    else:
        print(f"[Gesture Error] {lua_cmd} -> {res.stderr.strip()}", flush=True)

def main():
    print("[TouchDaemon] Starting touchscreen gesture daemon...", flush=True)
    device_path, device_name = None, None
    for _ in range(15):
        device_path, device_name = find_real_touch_device()
        if device_path:
            break
        time.sleep(1)

    if not device_path:
        print("[TouchDaemon Error] No touchscreen device found!", flush=True)
        sys.exit(1)

    print(f"[TouchDaemon] Bound to {device_name} ({device_path})", flush=True)

    try:
        dev = InputDevice(device_path)
    except Exception as e:
        print(f"[TouchDaemon Error] Could not open device: {e}", flush=True)
        sys.exit(1)

    slots = {}
    current_slot = 0
    max_fingers = 0
    start_x, start_y = 0, 0
    last_x, last_y = 0, 0
    gesture_fired = False
    touch_active = False

    for event in dev.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_MT_SLOT:
                current_slot = event.value
            elif event.code == ecodes.ABS_MT_TRACKING_ID:
                if event.value == -1:
                    slots.pop(current_slot, None)
                else:
                    slots[current_slot] = {'x': 0, 'y': 0}
            elif event.code == ecodes.ABS_MT_POSITION_X:
                if current_slot in slots:
                    slots[current_slot]['x'] = event.value
            elif event.code == ecodes.ABS_MT_POSITION_Y:
                if current_slot in slots:
                    slots[current_slot]['y'] = event.value

        elif event.type == ecodes.EV_SYN:
            if event.code == ecodes.SYN_REPORT:
                active_count = len(slots)

                if active_count > 0:
                    xs = [s['x'] for s in slots.values() if s['x'] > 0]
                    ys = [s['y'] for s in slots.values() if s['y'] > 0]

                    if xs and ys:
                        cx = sum(xs) / len(xs)
                        cy = sum(ys) / len(ys)

                        if not touch_active:
                            touch_active = True
                            max_fingers = active_count
                            start_x, start_y = cx, cy
                            last_x, last_y = cx, cy
                            gesture_fired = False
                        else:
                            max_fingers = max(max_fingers, active_count)
                            last_x, last_y = cx, cy

                        # Check if a gesture should fire during active multi-finger touch
                        if not gesture_fired and max_fingers >= 3:
                            raw_dx = last_x - start_x
                            raw_dy = last_y - start_y
                            dist = (raw_dx**2 + raw_dy**2)**0.5

                            if dist >= THRESHOLD:
                                transform = get_monitor_transform()
                                dx, dy = adjust_for_transform(raw_dx, raw_dy, transform)
                                abs_dx = abs(dx)
                                abs_dy = abs(dy)

                                if max_fingers == 4:
                                    if abs_dx > abs_dy:
                                        if dx > 0:
                                            send_hypr_dispatch('hl.dsp.focus({ workspace = "r-1" })', "4-finger swipe right -> Prev Workspace")
                                        else:
                                            send_hypr_dispatch('hl.dsp.focus({ workspace = "r+1" })', "4-finger swipe left -> Next Workspace")
                                    else:
                                        if dy > 0:
                                            send_hypr_dispatch('hl.dsp.window.fullscreen({ mode = 1 })', "4-finger swipe down -> Fullscreen toggle")
                                        else:
                                            send_hypr_dispatch('hl.dsp.window.float({ action = "toggle" })', "4-finger swipe up -> Float toggle")
                                    gesture_fired = True

                                elif max_fingers == 3:
                                    if abs_dx > abs_dy:
                                        if dx > 0:
                                            send_hypr_dispatch('hl.dsp.focus({ direction = "l" })', "3-finger swipe right -> Focus Left")
                                        else:
                                            send_hypr_dispatch('hl.dsp.focus({ direction = "r" })', "3-finger swipe left -> Focus Right")
                                    else:
                                        if dy > 0:
                                            send_hypr_dispatch('hl.dsp.focus({ direction = "d" })', "3-finger swipe down -> Focus Down")
                                        else:
                                            send_hypr_dispatch('hl.dsp.focus({ direction = "u" })', "3-finger swipe up -> Focus Up")
                                    gesture_fired = True

                                elif max_fingers == 5:
                                    send_hypr_dispatch('hl.dsp.window.close()', "5-finger swipe/pinch -> Close Window")
                                    gesture_fired = True

                else:
                    # All fingers released
                    if touch_active:
                        # If a 5-finger tap occurred without swipe movement
                        if not gesture_fired and max_fingers == 5:
                            send_hypr_dispatch('hl.dsp.window.close()', "5-finger tap -> Close Window")

                        touch_active = False
                        max_fingers = 0
                        gesture_fired = False

if __name__ == '__main__':
    main()

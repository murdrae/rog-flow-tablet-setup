#!/usr/bin/env python3
"""
Touch Window Drag & Close Daemon for Hyprland on ASUS ROG Flow Z13.

Features:
1. Hold still in the top strip (60px) for 300ms to grab and drag/swap windows.
2. Double-tap the top-right corner (65x65px) to close the active window.
"""

import os
import sys
import time
import json
import math
import socket
import threading
from evdev import InputDevice, list_devices, ecodes

# ================= Configuration =================
HOLD_DURATION_SEC = 0.30       # Hold time required to initiate grab (300ms)
TOP_MARGIN_PX = 60             # Height of top grab strip (in logical pixels)
JITTER_THRESHOLD_PX = 40.0     # Allowable finger drift during hold (contact settling)
TILE_SWAP_THRESHOLD_PX = 45.0  # Drag distance to trigger a swap in the tiling grid

# Corner Close Configuration
CORNER_CLOSE_SIZE_PX = 65.0    # 65x65px square in top-right corner of window
DOUBLE_TAP_MAX_DELAY = 0.35    # Max time between taps for a double-tap (350ms)

DEBUG_LOGS = True              # Print debug logs to journal
# =================================================

def log(msg):
    if DEBUG_LOGS:
        print(f"[TouchDrag] {msg}", flush=True)

def get_hypr_socket_path():
    uid = str(os.getuid())
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not sig:
        hypr_dir = f"/run/user/{uid}/hypr"
        if os.path.exists(hypr_dir):
            sigs = [s for s in os.listdir(hypr_dir) if not s.endswith(('.lock', '.sock'))]
            if sigs:
                sig = sigs[0]
    if not sig:
        return None
    return f"/run/user/{uid}/hypr/{sig}/.socket.sock"

def hypr_ipc(cmd: str, timeout: float = 0.5) -> str:
    sock_path = get_hypr_socket_path()
    if not sock_path or not os.path.exists(sock_path):
        return ""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(sock_path)
        s.sendall(cmd.encode("utf-8"))
        s.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        s.close()
        return b"".join(chunks).decode("utf-8", errors="replace")
    except Exception:
        return ""

def hypr_notify(msg: str, ms: int = 800, color: str = "rgb(88c0d0)"):
    hypr_ipc(f"notify 0 {ms} {color} {msg}")

def get_active_window():
    res = hypr_ipc("j/activewindow")
    if not res:
        return None
    try:
        win = json.loads(res)
        if win and "at" in win and "size" in win:
            return win
    except Exception:
        pass
    return None

def get_edp1_monitor():
    res = hypr_ipc("j/monitors")
    if not res:
        return None
    try:
        monitors = json.loads(res)
        for m in monitors:
            if m.get("name") == "eDP-1":
                return m
        for m in monitors:
            if m.get("focused"):
                return m
    except Exception:
        pass
    return None

def find_touchscreen_device():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            caps = dev.capabilities()
            if ecodes.EV_ABS in caps:
                abs_codes = [c for c, _ in caps[ecodes.EV_ABS]]
                if ecodes.ABS_MT_POSITION_X in abs_codes and ecodes.ABS_MT_POSITION_Y in abs_codes:
                    x_info = dev.absinfo(ecodes.ABS_MT_POSITION_X)
                    y_info = dev.absinfo(ecodes.ABS_MT_POSITION_Y)
                    return path, dev.name, x_info.max, y_info.max
        except Exception:
            continue
    return None, None, 3408, 2064

class TouchWindowDragManager:
    def __init__(self, raw_max_x, raw_max_y):
        self.raw_max_x = float(raw_max_x) or 3408.0
        self.raw_max_y = float(raw_max_y) or 2064.0

        self.slots = {}
        self.current_slot = 0

        self.timer = None
        self.state_lock = threading.Lock()

        self.is_grabbed = False
        self.is_floating = False
        self.grabbed_window_addr = None

        self.start_canvas_x = 0.0
        self.start_canvas_y = 0.0
        self.current_canvas_x = 0.0
        self.current_canvas_y = 0.0

        # Corner Double-Tap Close State
        self.touch_started_in_corner = False
        self.last_corner_tap_time = 0.0
        self.last_corner_tap_addr = None

        # For floating window dragging
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.last_dispatched_x = 0
        self.last_dispatched_y = 0
        self.last_dispatch_time = 0.0

        # For tiled window swap step & debounce
        self.tile_drag_origin_x = 0.0
        self.tile_drag_origin_y = 0.0
        self.last_swap_time = 0.0

        # Cached monitor geometry
        self.mon_cache_time = 0
        self.mon_info = None

    def get_monitor_info(self):
        now = time.time()
        if now - self.mon_cache_time > 2.0 or not self.mon_info:
            mon = get_edp1_monitor()
            if mon:
                scale = float(mon.get("scale", 1.0))
                self.mon_info = {
                    "x": float(mon.get("x", 0)),
                    "y": float(mon.get("y", 0)),
                    "width": float(mon.get("width", 2560)) / scale,
                    "height": float(mon.get("height", 1600)) / scale,
                    "transform": int(mon.get("transform", 0)),
                }
                self.mon_cache_time = now
        return self.mon_info

    def raw_to_canvas(self, rx, ry):
        mon = self.get_monitor_info()
        if not mon:
            return 0.0, 0.0

        nx = max(0.0, min(1.0, rx / self.raw_max_x))
        ny = max(0.0, min(1.0, ry / self.raw_max_y))
        tr = mon["transform"]

        if tr == 1:       # 90 deg clockwise
            sx = ny * mon["width"]
            sy = (1.0 - nx) * mon["height"]
        elif tr == 2:     # 180 deg
            sx = (1.0 - nx) * mon["width"]
            sy = (1.0 - ny) * mon["height"]
        elif tr == 3:     # 270 deg
            sx = (1.0 - ny) * mon["width"]
            sy = nx * mon["height"]
        else:             # 0 normal
            sx = nx * mon["width"]
            sy = ny * mon["height"]

        return mon["x"] + sx, mon["y"] + sy

    def cancel_timer(self):
        with self.state_lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None

    def on_hold_timeout(self, win):
        with self.state_lock:
            self.timer = None

            if len(self.slots) != 1:
                return

            self.is_floating = win.get("floating", False)
            title = win.get("title", "") or win.get("class", "window")
            mode_str = "Floating" if self.is_floating else "Tile"
            log(f"Hold reached on '{title}' [{mode_str}]")

            wx, wy = win["at"]

            # Floating setup
            self.offset_x = self.current_canvas_x - wx
            self.offset_y = self.current_canvas_y - wy
            self.last_dispatched_x = int(wx)
            self.last_dispatched_y = int(wy)
            self.last_dispatch_time = time.time()

            # Tiled setup
            self.tile_drag_origin_x = self.current_canvas_x
            self.tile_drag_origin_y = self.current_canvas_y
            self.last_swap_time = time.time()

            self.is_grabbed = True
            self.grabbed_window_addr = win.get("address")

        if self.is_floating:
            hypr_notify("✥ Move Window (Drag freely)", ms=1000)
        else:
            hypr_notify("✥ Move Tile (Drag toward target)", ms=1000)

        log(f"Grab active! Window stays {mode_str}.")

    def handle_touch_down(self, cx, cy):
        with self.state_lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            self.is_grabbed = False
            self.touch_started_in_corner = False

        if len(self.slots) != 1:
            return

        win = get_active_window()
        if not win:
            return

        wx, wy = win["at"]
        ww, wh = win["size"]

        # Check if touch is within top grab strip of active window
        if wx <= cx <= wx + ww and wy <= cy <= wy + TOP_MARGIN_PX:
            self.start_canvas_x = cx
            self.start_canvas_y = cy
            self.current_canvas_x = cx
            self.current_canvas_y = cy

            # Check if this touch is specifically in the top-right corner (close target)
            is_corner = (wx + ww - CORNER_CLOSE_SIZE_PX <= cx <= wx + ww) and (wy <= cy <= wy + CORNER_CLOSE_SIZE_PX)
            self.touch_started_in_corner = is_corner
            self.active_window_addr = win.get("address")

            log(f"Touch down in header zone at ({cx:.1f}, {cy:.1f}) [corner={is_corner}], starting {HOLD_DURATION_SEC*1000:.0f}ms timer")
            with self.state_lock:
                self.timer = threading.Timer(HOLD_DURATION_SEC, self.on_hold_timeout, args=[win])
                self.timer.daemon = True
                self.timer.start()

    def handle_touch_move(self, cx, cy):
        self.current_canvas_x = cx
        self.current_canvas_y = cy

        with self.state_lock:
            pending_timer = self.timer
            currently_grabbed = self.is_grabbed

        # If hold timer is pending, check for movement jitter
        if pending_timer:
            drift = math.hypot(cx - self.start_canvas_x, cy - self.start_canvas_y)
            if drift > JITTER_THRESHOLD_PX:
                log(f"Swipe detected ({drift:.1f}px > {JITTER_THRESHOLD_PX}px); canceling hold timer")
                self.cancel_timer()
                self.touch_started_in_corner = False

        # If currently grabbed, handle movement based on window mode
        elif currently_grabbed:
            now = time.time()

            if self.is_floating:
                # Floating: update pixel coordinates smoothly (~80Hz)
                if now - self.last_dispatch_time < 0.012:
                    return

                target_x = int(cx - self.offset_x)
                target_y = int(cy - self.offset_y)

                if abs(target_x - self.last_dispatched_x) >= 2 or abs(target_y - self.last_dispatched_y) >= 2:
                    lua_cmd = f'eval return hl.dispatch(hl.dsp.window.move({{ x = {target_x}, y = {target_y}, relative = false }}))'
                    hypr_ipc(lua_cmd)
                    self.last_dispatched_x = target_x
                    self.last_dispatched_y = target_y
                    self.last_dispatch_time = now

            else:
                # Tiled: swap window within the tiling layout
                if now - self.last_swap_time < 0.22:
                    return

                dx = cx - self.tile_drag_origin_x
                dy = cy - self.tile_drag_origin_y

                if abs(dx) >= abs(dy):
                    if dx >= TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap right")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "r" }))')
                        hypr_notify("✥ Swapped Right", ms=400)
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now
                    elif dx <= -TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap left")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "l" }))')
                        hypr_notify("✥ Swapped Left", ms=400)
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now
                else:
                    if dy >= TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap down")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "d" }))')
                        hypr_notify("✥ Swapped Down", ms=400)
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now
                    elif dy <= -TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap up")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "u" }))')
                        hypr_notify("✥ Swapped Up", ms=400)
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now

    def handle_touch_up(self):
        was_timer_active = (self.timer is not None)
        self.cancel_timer()

        with self.state_lock:
            was_grabbed = self.is_grabbed
            started_in_corner = self.touch_started_in_corner
            win_addr = self.active_window_addr

            if was_grabbed:
                log("Touch released; window placement complete")
                self.is_grabbed = False
                self.grabbed_window_addr = None
                hypr_notify("✓ Placed", ms=400, color="rgb(a3be8c)")
                return

        # Check for Double-Tap in Top-Right Corner (quick tap, timer didn't expire, didn't grab)
        if started_in_corner and was_timer_active:
            now = time.time()
            if (now - self.last_corner_tap_time) <= DOUBLE_TAP_MAX_DELAY and self.last_corner_tap_addr == win_addr:
                log("Double-tap in top-right corner -> Closing window!")
                hypr_ipc('eval return hl.dispatch(hl.dsp.window.close())')
                hypr_notify("✕ Closed Window", ms=600, color="rgb(bf616a)")
                self.last_corner_tap_time = 0.0
                self.last_corner_tap_addr = None
            else:
                log("Corner tap 1 recorded; waiting for tap 2")
                self.last_corner_tap_time = now
                self.last_corner_tap_addr = win_addr

def main():
    print("[TouchDrag] Starting Touch Window Drag & Close Daemon...", flush=True)

    dev_path, dev_name, max_x, max_y = None, None, 3408, 2064
    for _ in range(15):
        dev_path, dev_name, max_x, max_y = find_touchscreen_device()
        if dev_path:
            break
        time.sleep(1)

    if not dev_path:
        print("[TouchDrag Error] No touchscreen device detected!", flush=True)
        sys.exit(1)

    print(f"[TouchDrag] Bound to {dev_name} ({dev_path}) [{max_x}x{max_y}]", flush=True)

    try:
        dev = InputDevice(dev_path)
    except Exception as e:
        print(f"[TouchDrag Error] Could not open {dev_path}: {e}", flush=True)
        sys.exit(1)

    manager = TouchWindowDragManager(max_x, max_y)
    current_slot = 0

    for event in dev.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_MT_SLOT:
                current_slot = event.value
            elif event.code == ecodes.ABS_MT_TRACKING_ID:
                if event.value == -1:
                    manager.slots.pop(current_slot, None)
                else:
                    manager.slots[current_slot] = {"x": 0, "y": 0, "new": True}
            elif event.code == ecodes.ABS_MT_POSITION_X:
                if current_slot in manager.slots:
                    manager.slots[current_slot]["x"] = event.value
            elif event.code == ecodes.ABS_MT_POSITION_Y:
                if current_slot in manager.slots:
                    manager.slots[current_slot]["y"] = event.value

        elif event.type == ecodes.EV_SYN and event.code == ecodes.SYN_REPORT:
            active_count = len(manager.slots)

            if active_count == 1:
                slot_data = next(iter(manager.slots.values()))
                rx = slot_data["x"]
                ry = slot_data["y"]
                if rx > 0 and ry > 0:
                    cx, cy = manager.raw_to_canvas(rx, ry)
                    if slot_data.get("new", False):
                        slot_data["new"] = False
                        manager.handle_touch_down(cx, cy)
                    else:
                        manager.handle_touch_move(cx, cy)

            elif active_count == 0:
                manager.handle_touch_up()

            else:
                manager.cancel_timer()
                if manager.is_grabbed:
                    manager.handle_touch_up()

if __name__ == "__main__":
    main()

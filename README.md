# ASUS ROG Flow Tablet Setup & Configuration Guide (Omarchy / Hyprland)

This document provides a comprehensive record of all configurations, custom scripts, keyboard layout modifications, background services, and udev rules implemented on the ASUS ROG Flow Z13/X13 tablet running Omarchy (Arch Linux + Hyprland). It also includes a complete step-by-step fresh installation guide and automated setup script.

---

## 1. Hardware & System Context

* **Device Model:** ASUS ROG Flow Z13 / X13 (`ROG Flow Z13 GZ302EA`)
* **Processor / APU:** AMD Ryzen AI Max+ 395 ("Strix Halo")
* **Display:** 2.5K Tianma Display (`eDP-1`, 2560x1600 @ 180Hz)
* **Touchscreen Digitizer:** ELAN9008 (`04F3:43C7`)
* **Base OS:** Omarchy Linux (Arch Linux rolling base)
* **Compositor:** Hyprland 0.54+ (configured with Lua)
* **Kernel:** `Linux 7.2.5-3-omarchy` (Standard Omarchy kernel; CachyOS kernel is **not** required)

---

## 2. Tablet Features Overview

1. **Automatic Screen & Stylus Rotation:** Screen, touchscreen coordinates, and stylus orientation automatically follow device orientation using the onboard accelerometer.
2. **On-Screen Virtual Keyboard (`wvkbd-deskintl`):**
   * Custom-compiled 5-row layout.
   * `F1`–`F12` row removed for vertical screen savings.
   * `Esc` key on the number row (with Shift giving `~` / `` ` ``).
   * **Layer Switch Key (`[ ⌨ ]`):** Located on the left side of the home row (above `Shift`, replacing the unused `Cmp`/Compose key).
   * **Bottom-Left Corner:** Standard PC keyboard layout (`[Ctr] [Sup] [Alt]`).
   * **Dedicated Dictation Key (`[ 🎙 ]`):** Positioned next to the spacebar to trigger Voxtype speech dictation with one tap.
   * **Clean & Extra-Wide Spacebar:** Width expanded to 7.5 for effortless thumb typing.
   * **Unused Keys Removed:** Unnecessary `Cmp` (Compose), `AGr` (AltGr), and duplicate right `Ctrl` removed.
   * Toggled via the tablet physical side button (`XF86Launch3`).
   * `SUPER + B` is mapped to toggle the status bar Bitwarden vault plugin (`io.github.elevate08.qs-bitwarden-cli`).
3. **Tap-to-Dictate Status Bar Widget (`user.dictation`):**
   * Sits in the top Omarchy status bar for instant voice access without opening the keyboard.
   * Live status feedback: dim when idle (`󰍬`), brightly active when recording, spinner when transcribing (`󰔟`).
   * Tap to start or stop; right-click to abort.
4. **Touch Window Drag & Close Daemon:**
   * **Hold to Grab**: Press and hold still in the top ~60px header strip of any window for 300ms to grab it.
   * **Tiled Windows**: Dragging toward an adjacent window (left, right, up, down) swaps tiles directly in the layout tree (`hl.dsp.window.swap`). Windows remain 100% tiled.
   * **Floating Windows**: Drags smoothly across screen by pixel coordinates.
   * **Corner Double-Tap to Close**: Quickly double-tapping the top-right 65×65px corner instantly closes the active window (`hl.dsp.window.close()`).
   * **Zero App Conflict**: Single taps and touches below the top 60px pass directly into apps with zero interference.
   * **Dynamic Rotation**: Works across all display rotations/transforms on `eDP-1`.
   * **Theme-Aware Notifications**: Notification pills dynamically adapt in real-time to match the active Omarchy theme colors (accent, success green, alert red).
4. **Battery Health Optimization:**
   * Charge limit set to **80%** to avoid cell degradation.
   * Persisted via `asusd` (`asusctl battery limit 80`).
   * One-shot travel override: `asusctl battery oneshot 100`.

---

## 3. Touch Window Drag & Close Cheat Sheet

| Action | Target | Behavior |
| :--- | :--- | :--- |
| **Double-Tap Top-Right Corner** | Active Window | Instantly closes window (`hl.dsp.window.close()`) with `✕ Closed Window` confirmation |
| **Hold Top 60px (300ms)** | Active Window | Grabs window and displays `✥ Move Tile` or `✥ Move Window` notification |
| **Drag Left / Right** | Tiled Window | Swaps tile with neighbor window (`hl.dsp.window.swap`) |
| **Drag Up / Down** | Tiled Window | Swaps tile vertically with neighbor window |
| **Drag Anywhere** | Floating Window | Freely repositions window across canvas coordinates |
| **Lift Finger** | Active Drag | Drops window in place with `✓ Placed` confirmation |
| **Single Tap (<300ms)** | Window Header | Normal in-app click (switches tabs, clicks buttons, focuses window) |
| **Touch Body (>60px)** | Anywhere in App | Normal in-app interaction (scroll, type, zoom, select) |

---

## 4. Virtual Keyboard Layout Matrix

The customized `wvkbd-deskintl` binary is located at `~/.local/bin/wvkbd-deskintl` (taking priority over `/usr/bin/wvkbd-deskintl` in `$PATH`).

### A. Primary Layer (`Full` - Alphabetical):
* **Row 1 (Numbers):** `[Esc]` `1` `2` `3` `4` `5` `6` `7` `8` `9` `0` `-` `=` `[ ⌫ ]`
* **Row 2 (QWERTY):** `[Tab]` `q` `w` `e` `r` `t` `y` `u` `i` `o` `p` `[` `]` `\`
* **Row 3 (Home Row):** `[ ⌨ ]` `[Caps]` `a` `s` `d` `f` `g` `h` `j` `k` `l` `;` `'` `[Enter]`
* **Row 4 (Shift / Nav):** `[ ⇧ ]` `z` `x` `c` `v` `b` `n` `m` `,` `.` `/` `[↑]` `[ ⇧ ]`
* **Row 5 (Bottom Row):** `[Ctr]` `[Sup]` `[Alt]` `[ 🎙 ]` `[           Space (7.5)           ]` `[←]` `[↓]` `[→]`

### B. Secondary Layer (`Special` - Non-Alpha Characters, Symbols & Nav):
Accessed by tapping `[ ⌨ ]` on the left of Row 3. Tap `[Abc]` in that exact same position to return to letters.
* **Row 1 (Numbers):** `[Esc]` `1` `2` `3` `4` `5` `6` `7` `8` `9` `0` `-` `=` `[ ⌫ ]`
* **Row 2 (Direct Symbols):** `[Tab]` `~` `!` `@` `#` `$` `%` `^` `&` `*` `(` `)` `_` `+`
* **Row 3 (Brackets & Quotes):** `[Abc]` `[Del]` `` ` `` `[` `]` `{` `}` `\` `|` `;` `:` `'` `"` `[Enter]`
* **Row 4 (Math & Currency):** `[ ⇧ ]` `<` `>` `/` `?` `=` `€` `£` `¥` `°` `±` `[PgUp]` `[Ins]`
* **Row 5 (Nav & Modifiers):** `[Ctr]` `[Sup]` `[Alt]` `[ 🎙 ]` `[           Space (7.5)           ]` `[Home]` `[PgDn]` `[End]`

---

## 5. Fresh Install Instructions (Step-by-Step)

If installing from a fresh Omarchy / Arch Linux installation, follow these steps:

### Step 1: Install Required System & AUR Packages

```bash
# Core tools, sensor proxy, build dependencies, and python evdev
sudo pacman -S --needed \
    base-devel git pango cairo libxkbcommon wayland wayland-protocols scdoc \
    iio-sensor-proxy python-evdev

# Auto-rotation daemon and ASUS hardware control daemon from AUR
yay -S --needed iio-hyprland-git asusctl
```

---

### Step 2: Configure ASUS Daemon (`asusd`) & Battery Threshold

Some upstream packages for `asusd` do not include an `[Install]` section in their systemd unit. Add a drop-in override:

```bash
# 1. Add install override
sudo mkdir -p /etc/systemd/system/asusd.service.d
sudo tee /etc/systemd/system/asusd.service.d/install.conf << 'EOF'
[Install]
WantedBy=multi-user.target
EOF

# 2. Reload and enable asusd
sudo systemctl daemon-reload
sudo systemctl enable --now asusd

# 3. Set battery charging threshold to 80%
asusctl battery limit 80
```

Verify with:
```bash
asusctl battery info
```

---

### Step 3: Configure Accelerometer & Auto-Rotation

```bash
# 1. Enable and start the system sensor daemon
sudo systemctl enable --now iio-sensor-proxy

# 2. Create the user service for iio-hyprland
mkdir -p ~/.config/systemd/user
cat << 'EOF' > ~/.config/systemd/user/iio-hyprland.service
[Unit]
Description=iio-hyprland auto-rotation service
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/iio-hyprland
Restart=on-failure
RestartSec=2

[Install]
WantedBy=graphical-session.target
EOF

# 3. Enable and start the user service
systemctl --user daemon-reload
systemctl --user enable --now iio-hyprland.service
```

---

### Step 4: Configure Touchscreen Udev Rules & User Permissions

Ensure regular users have read access to touchscreen event streams:

```bash
# 1. Create udev rule
sudo tee /etc/udev/rules.d/99-touchscreen.rules << 'EOF'
SUBSYSTEM=="input", KERNEL=="event*", ENV{ID_INPUT_TOUCHSCREEN}=="1", MODE="0666"
EOF

# 2. Add current user to input group
sudo usermod -aG input "$USER"

# 3. Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

### Step 5: Hyprland Lua Configuration Updates

#### A. Lock Touch Input to the Built-in Screen
Add the following to `~/.config/hypr/input.lua`:

```lua
-- Tablet and Touchscreen input mapping to built-in display
hl.config({
  input = {
    touchdevice = {
      output = "eDP-1",
    },
    tablet = {
      output = "eDP-1",
    },
  },
})
```

#### B. Configure Keybindings
Add the following to `~/.config/hypr/bindings.lua`:

```lua
-- Bitwarden status bar plugin toggle
o.bind("SUPER + B", "Bitwarden vault", "omarchy-shell io.github.elevate08.qs-bitwarden-cli toggle")

-- Tablet On-Screen Virtual Keyboard Toggle (deskintl has Sup/Ctrl/Alt on the main screen)
o.bind("XF86Launch3", "Toggle virtual keyboard", "pkill -x wvkbd-deskintl || pkill -x wvkbd-mobintl || /home/jason/.local/bin/wvkbd-deskintl -L 360", { locked = true })
```

---

### Step 6: Install Touch Window Drag & Close Daemon

#### A. Create `~/.config/hypr/touch_window_drag.py`

```bash
cat << 'EOF' > ~/.config/hypr/touch_window_drag.py
#!/usr/bin/env python3
"""
Touch Window Drag & Close Daemon for Hyprland on ASUS ROG Flow Z13.

Features:
1. Hold still in the top strip (60px) for 300ms to grab and drag/swap windows.
2. Double-tap the top-right corner (65x65px) to close the active window.
3. Automatically adapts notification colors to the active Omarchy theme.
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

_cached_theme_colors = None
_cached_theme_mtime = 0.0

def log(msg):
    if DEBUG_LOGS:
        print(f"[TouchDrag] {msg}", flush=True)

def get_theme_colors():
    """Dynamically load colors from the active Omarchy theme."""
    global _cached_theme_colors, _cached_theme_mtime
    colors_path = os.path.expanduser("~/.local/state/omarchy/current/theme/colors.toml")

    try:
        if os.path.exists(colors_path):
            mtime = os.path.getmtime(colors_path)
            if _cached_theme_colors and mtime == _cached_theme_mtime:
                return _cached_theme_colors

            colors = {"accent": "rgb(7aa2f7)", "red": "rgb(f7768e)", "green": "rgb(9ece6a)"}
            with open(colors_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if v.startswith("#") and len(v) == 7:
                            colors[k] = f"rgb({v[1:]})"

            _cached_theme_colors = colors
            _cached_theme_mtime = mtime
            return colors
    except Exception:
        pass

    return {"accent": "rgb(7aa2f7)", "red": "rgb(f7768e)", "green": "rgb(9ece6a)"}

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

def hypr_notify(msg: str, ms: int = 800, color_type: str = "accent"):
    colors = get_theme_colors()
    color = colors.get(color_type, colors.get("accent", "rgb(7aa2f7)"))
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
            hypr_notify("✥ Move Window (Drag freely)", ms=1000, color_type="accent")
        else:
            hypr_notify("✥ Move Tile (Drag toward target)", ms=1000, color_type="accent")

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
                        hypr_notify("✥ Swapped Right", ms=400, color_type="accent")
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now
                    elif dx <= -TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap left")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "l" }))')
                        hypr_notify("✥ Swapped Left", ms=400, color_type="accent")
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now
                else:
                    if dy >= TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap down")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "d" }))')
                        hypr_notify("✥ Swapped Down", ms=400, color_type="accent")
                        self.tile_drag_origin_x = cx
                        self.tile_drag_origin_y = cy
                        self.last_swap_time = now
                    elif dy <= -TILE_SWAP_THRESHOLD_PX:
                        log("Tiled drag -> swap up")
                        hypr_ipc('eval return hl.dispatch(hl.dsp.window.swap({ direction = "u" }))')
                        hypr_notify("✥ Swapped Up", ms=400, color_type="accent")
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
                hypr_notify("✓ Placed", ms=400, color_type="green")
                return

        # Check for Double-Tap in Top-Right Corner (quick tap, timer didn't expire, didn't grab)
        if started_in_corner and was_timer_active:
            now = time.time()
            if (now - self.last_corner_tap_time) <= DOUBLE_TAP_MAX_DELAY and self.last_corner_tap_addr == win_addr:
                log("Double-tap in top-right corner -> Closing window!")
                hypr_ipc('eval return hl.dispatch(hl.dsp.window.close())')
                hypr_notify("✕ Closed Window", ms=600, color_type="red")
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
EOF
chmod +x ~/.config/hypr/touch_window_drag.py
```

#### B. Create & Enable User Service for Window Management

```bash
cat << 'EOF' > ~/.config/systemd/user/touch-window-drag.service
[Unit]
Description=Touchscreen Window Drag Daemon for Hyprland
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/.config/hypr/touch_window_drag.py
Restart=always
RestartSec=2

[Install]
WantedBy=graphical-session.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now touch-window-drag.service
```

---

### Step 7: Build & Install Customized Virtual Keyboard (`wvkbd-deskintl`)

Run this script block to clone upstream `wvkbd`, apply our custom layout patch, compile, and place the executable in `~/.local/bin`:

```bash
# 1. Clone upstream repository
rm -rf /tmp/wvkbd-src
git clone --depth 1 https://github.com/jjsullivan5196/wvkbd.git /tmp/wvkbd-src
cd /tmp/wvkbd-src

# 2. Apply Python layout patch
python3 - << 'EOF'
import re

path = 'layout.deskintl.h'
with open(path, 'r') as f:
    content = f.read()

# Pattern for keys_full
full_pattern = r'static struct key keys_full\[\] = \{.*?\n\};\n'

new_keys_full = r"""static struct key keys_full[] = {
  {"Esc", "~", 1.0, Code, KEY_ESC, .shift_code = KEY_GRAVE, .scheme = 1},
  {"1", "!", 1.0, Code, KEY_1},
  {"2", "@", 1.0, Code, KEY_2},
  {"3", "#", 1.0, Code, KEY_3},
  {"4", "$", 1.0, Code, KEY_4},
  {"5", "%", 1.0, Code, KEY_5},
  {"6", "^", 1.0, Code, KEY_6},
  {"7", "&", 1.0, Code, KEY_7},
  {"8", "*", 1.0, Code, KEY_8},
  {"9", "(", 1.0, Code, KEY_9, &layouts[ComposeBracket]},
  {"0", ")", 1.0, Code, KEY_0, &layouts[ComposeBracket]},
  {"-", "_", 1.0, Code, KEY_MINUS, &layouts[ComposeBracket]},
  {"=", "+", 1.0, Code, KEY_EQUAL, &layouts[ComposeBracket]},
  {"⌫", "⌫", 1.5, Code, KEY_BACKSPACE, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"Tab", "Tab", 1.5, Code, KEY_TAB, .scheme = 1},
  {"q", "Q", 1.0, Code, KEY_Q},
  {"w", "W", 1.0, Code, KEY_W, &layouts[ComposeW]},
  {"e", "E", 1.0, Code, KEY_E, &layouts[ComposeE]},
  {"r", "R", 1.0, Code, KEY_R, &layouts[ComposeR]},
  {"t", "T", 1.0, Code, KEY_T, &layouts[ComposeT]},
  {"y", "Y", 1.0, Code, KEY_Y, &layouts[ComposeY]},
  {"u", "U", 1.0, Code, KEY_U, &layouts[ComposeU]},
  {"i", "I", 1.0, Code, KEY_I, &layouts[ComposeI]},
  {"o", "O", 1.0, Code, KEY_O, &layouts[ComposeO]},
  {"p", "P", 1.0, Code, KEY_P, &layouts[ComposeP]},
  {"[", "{", 1.0, Code, KEY_LEFTBRACE},
  {"]", "}", 1.0, Code, KEY_RIGHTBRACE},
  {"\\", "|", 1.0, Code, KEY_BACKSLASH},
  {"", "", 0.0, EndRow},

  {"⌨͕", "⌨͔", 1.0, NextLayer, .scheme = 1},
  {"Caps", "Caps", 1.0, Mod, CapsLock, .scheme = 1},
  {"a", "A", 1.0, Code, KEY_A, &layouts[ComposeA]},
  {"s", "S", 1.0, Code, KEY_S, &layouts[ComposeS]},
  {"d", "D", 1.0, Code, KEY_D, &layouts[ComposeD]},
  {"f", "F", 1.0, Code, KEY_F, &layouts[ComposeF]},
  {"g", "G", 1.0, Code, KEY_G, &layouts[ComposeG]},
  {"h", "H", 1.0, Code, KEY_H, &layouts[ComposeH]},
  {"j", "J", 1.0, Code, KEY_J, &layouts[ComposeJ]},
  {"k", "K", 1.0, Code, KEY_K, &layouts[ComposeK]},
  {"l", "L", 1.0, Code, KEY_L, &layouts[ComposeL]},
  {";", ":", 1.0, Code, KEY_SEMICOLON},
  {"'", "''", 1.0, Code, KEY_APOSTROPHE, &layouts[ComposeBracket]},
  {"Enter", "Enter", 1.5, Code, KEY_ENTER, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"⇧", "⇫", 2.5, Mod, Shift, .scheme = 1},
  {"z", "Z", 1.0, Code, KEY_Z, &layouts[ComposeZ]},
  {"x", "X", 1.0, Code, KEY_X, &layouts[ComposeX]},
  {"c", "C", 1.0, Code, KEY_C, &layouts[ComposeC]},
  {"v", "V", 1.0, Code, KEY_V, &layouts[ComposeV]},
  {"b", "B", 1.0, Code, KEY_B, &layouts[ComposeB]},
  {"n", "N", 1.0, Code, KEY_N, &layouts[ComposeN]},
  {"m", "M", 1.0, Code, KEY_M, &layouts[ComposeM]},
  {",", "<", 1.0, Code, KEY_COMMA, &layouts[ComposeMath]},
  {".", ">", 1.0, Code, KEY_DOT, &layouts[ComposePunctuation]},
  {"/", "?", 1.0, Code, KEY_SLASH},
  {"↑", "↑", 1.0, Code, KEY_UP, .scheme = 1},
  {"⇧", "⇫", 1.0, Mod, Shift, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"Ctr", "Ctr", 1.0, Mod, Ctrl, .scheme = 1},
  {"Sup", "Sup", 1.0, Mod, Super, .scheme = 1},
  {"Alt", "Alt", 1.0, Mod, Alt, .scheme = 1},
  {"", "", 8.5, Code, KEY_SPACE},
  {"←", "←", 1.0, Code, KEY_LEFT, .scheme = 1},
  {"↓", "↓", 1.0, Code, KEY_DOWN, .scheme = 1},
  {"→", "→", 1.0, Code, KEY_RIGHT, .scheme = 1},
  /* end of layout */
  {"", "", 0.0, Last},
};
"""

# Pattern for keys_special
special_pattern = r'static struct key keys_special\[\] = \{.*?\n\};\n'

new_keys_special = r"""static struct key keys_special[] = {
  {"Esc", "Esc", 1.0, Code, KEY_ESC, .scheme = 1},
  {"1", "!", 1.0, Code, KEY_1},
  {"2", "@", 1.0, Code, KEY_2},
  {"3", "#", 1.0, Code, KEY_3},
  {"4", "$", 1.0, Code, KEY_4},
  {"5", "%", 1.0, Code, KEY_5},
  {"6", "^", 1.0, Code, KEY_6},
  {"7", "&", 1.0, Code, KEY_7},
  {"8", "*", 1.0, Code, KEY_8},
  {"9", "(", 1.0, Code, KEY_9},
  {"0", ")", 1.0, Code, KEY_0},
  {"-", "_", 1.0, Code, KEY_MINUS},
  {"=", "+", 1.0, Code, KEY_EQUAL},
  {"⌫", "⌫", 1.5, Code, KEY_BACKSPACE, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"Tab", "Tab", 1.5, Code, KEY_TAB, .scheme = 1},
  {"~", "`", 1.0, Code, KEY_GRAVE, 0, Shift},
  {"!", "1", 1.0, Code, KEY_1, 0, Shift},
  {"@", "2", 1.0, Code, KEY_2, 0, Shift},
  {"#", "3", 1.0, Code, KEY_3, 0, Shift},
  {"$", "4", 1.0, Code, KEY_4, 0, Shift},
  {"%", "5", 1.0, Code, KEY_5, 0, Shift},
  {"^", "6", 1.0, Code, KEY_6, 0, Shift},
  {"&", "7", 1.0, Code, KEY_7, 0, Shift},
  {"*", "8", 1.0, Code, KEY_8, 0, Shift},
  {"(", "9", 1.0, Code, KEY_9, 0, Shift},
  {")", "0", 1.0, Code, KEY_0, 0, Shift},
  {"_", "-", 1.0, Code, KEY_MINUS, 0, Shift},
  {"+", "=", 1.0, Code, KEY_EQUAL, 0, Shift},
  {"", "", 0.0, EndRow},

  {"Abc", "Abc", 1.0, BackLayer, .scheme = 1},
  {"Del", "Ins", 1.0, Code, KEY_DELETE, .shift_code = KEY_INSERT, .scheme = 1},
  {"`", "~", 1.0, Code, KEY_GRAVE},
  {"[", "{", 1.0, Code, KEY_LEFTBRACE},
  {"]", "}", 1.0, Code, KEY_RIGHTBRACE},
  {"{", "[", 1.0, Code, KEY_LEFTBRACE, 0, Shift},
  {"}", "]", 1.0, Code, KEY_RIGHTBRACE, 0, Shift},
  {"\\", "|", 1.0, Code, KEY_BACKSLASH},
  {"|", "\\", 1.0, Code, KEY_BACKSLASH, 0, Shift},
  {";", ":", 1.0, Code, KEY_SEMICOLON},
  {":", ";", 1.0, Code, KEY_SEMICOLON, 0, Shift},
  {"'", "\"", 1.0, Code, KEY_APOSTROPHE},
  {"\"", "'", 1.0, Code, KEY_APOSTROPHE, 0, Shift},
  {"Enter", "Enter", 1.5, Code, KEY_ENTER, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"⇧", "⇫", 2.5, Mod, Shift, .scheme = 1},
  {"<", "<", 1.0, Code, KEY_COMMA, 0, Shift},
  {">", ">", 1.0, Code, KEY_DOT, 0, Shift},
  {"/", "?", 1.0, Code, KEY_SLASH},
  {"?", "/", 1.0, Code, KEY_SLASH, 0, Shift},
  {"=", "+", 1.0, Code, KEY_EQUAL},
  {"€", "€", 1.0, Copy, 0x20AC, 0, 0x20AC},
  {"£", "£", 1.0, Copy, 0x00A3, 0, 0x00A3},
  {"¥", "¥", 1.0, Copy, 0x00A5, 0, 0x00A5},
  {"°", "°", 1.0, Copy, 0x00B0, 0, 0x00B0},
  {"±", "±", 1.0, Copy, 0x00B1, 0, 0x00B1},
  {"PgUp", "PgUp", 1.0, Code, KEY_PAGEUP, .scheme = 1},
  {"Ins", "Ins", 1.0, Code, KEY_INSERT, .scheme = 1},
  {"", "", 0.0, EndRow},

  {"Ctr", "Ctr", 1.0, Mod, Ctrl, .scheme = 1},
  {"Sup", "Sup", 1.0, Mod, Super, .scheme = 1},
  {"Alt", "Alt", 1.0, Mod, Alt, .scheme = 1},
  {"", "", 8.5, Code, KEY_SPACE},
  {"Home", "Home", 1.0, Code, KEY_HOME, .scheme = 1},
  {"PgDn", "PgDn", 1.0, Code, KEY_PAGEDOWN, .scheme = 1},
  {"End", "End", 1.0, Code, KEY_END, .scheme = 1},
  /* end of layout */
  {"", "", 0.0, Last},
};
"""

content, n1 = re.subn(full_pattern, lambda m: new_keys_full, content, flags=re.DOTALL)
content, n2 = re.subn(special_pattern, lambda m: new_keys_special, content, flags=re.DOTALL)

if n1 != 1 or n2 != 1:
    raise RuntimeError(f"Regex replacement failed: n1={n1}, n2={n2}")

with open(path, 'w') as f:
    f.write(content)

print("wvkbd layout.deskintl.h successfully patched!")
EOF

# 3. Build deskintl layout
make LAYOUT=deskintl

# 4. Install into ~/.local/bin
mkdir -p ~/.local/bin
cp wvkbd-deskintl ~/.local/bin/wvkbd-deskintl
chmod 755 ~/.local/bin/wvkbd-deskintl

# 5. Clean up temporary build files
cd ~
rm -rf /tmp/wvkbd-src
```

---

## 6. Verification & Troubleshooting

1. **Verify Services Running:**
   ```bash
   # System daemons
   systemctl status iio-sensor-proxy
   systemctl status asusd

   # User daemons
   systemctl --user status iio-hyprland.service
   systemctl --user status touch-window-drag.service
   ```

2. **Verify Window Drag Logs in Real Time:**
   ```bash
   journalctl --user -u touch-window-drag.service -f
   ```

3. **Verify Battery Charge Threshold:**
   ```bash
   asusctl battery info
   ```

4. **Verify On-Screen Keyboard & Bitwarden Plugin:**
   * Test Bitwarden panel: Press `SUPER + B` to toggle the status bar Bitwarden vault.
   * Test virtual keyboard: Click the physical tablet side button (`XF86Launch3`).
   * Verify location: `which wvkbd-deskintl` should print `/home/<user>/.local/bin/wvkbd-deskintl`.

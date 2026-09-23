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
   * **Clean & Extra-Wide Spacebar:** Width expanded to 8.5 for effortless thumb typing.
   * **Unused Keys Removed:** Unnecessary `Cmp` (Compose), `AGr` (AltGr), and duplicate right `Ctrl` removed.
   * Toggled via the tablet physical side button (`XF86Launch3`).
   * `SUPER + B` is mapped to toggle the status bar Bitwarden vault plugin (`io.github.elevate08.qs-bitwarden-cli`).
3. **Multi-Touch Gestures Daemon:**
   * 4-finger swipes: Switch workspaces, toggle fullscreen, toggle floating/tiling.
   * 3-finger swipes: Directional focus movement (left, right, down, up).
   * 5-finger pinch/tap: Close active window.
   * Dynamic rotation compensation: Swiping physically "up" is always visually "up", even when rotated portrait or inverted.
4. **Battery Health Optimization:**
   * Charge limit set to **80%** to avoid cell degradation.
   * Persisted via `asusd` (`asusctl battery limit 80`).
   * One-shot travel override: `asusctl battery oneshot 100`.

---

## 3. Gesture Cheat Sheet

| Gesture | Action | Dispatched Command |
| :--- | :--- | :--- |
| **4 Fingers Swipe Left** | Switch to Next Workspace | `hl.dsp.focus({ workspace = "r+1" })` |
| **4 Fingers Swipe Right** | Switch to Previous Workspace | `hl.dsp.focus({ workspace = "r-1" })` |
| **4 Fingers Swipe Down** | Fullscreen / Restore Window | `hl.dsp.window.fullscreen({ mode = 1 })` |
| **4 Fingers Swipe Up** | Toggle Floating / Tiling Window | `hl.dsp.window.float({ action = "toggle" })` |
| **3 Fingers Swipe Left** | Move Focus Left | `hl.dsp.focus({ direction = "l" })` |
| **3 Fingers Swipe Right** | Move Focus Right | `hl.dsp.focus({ direction = "r" })` |
| **3 Fingers Swipe Down** | Move Focus Down | `hl.dsp.focus({ direction = "d" })` |
| **3 Fingers Swipe Up** | Move Focus Up | `hl.dsp.focus({ direction = "u" })` |
| **5 Fingers Tap or Pinch** | Close Active Window | `hl.dsp.window.close()` |

---

## 4. Virtual Keyboard Layout Matrix

The customized `wvkbd-deskintl` binary is located at `~/.local/bin/wvkbd-deskintl` (taking priority over `/usr/bin/wvkbd-deskintl` in `$PATH`).

### A. Primary Layer (`Full` - Alphabetical):
* **Row 1 (Numbers):** `[Esc]` `1` `2` `3` `4` `5` `6` `7` `8` `9` `0` `-` `=` `[ ⌫ ]`
* **Row 2 (QWERTY):** `[Tab]` `q` `w` `e` `r` `t` `y` `u` `i` `o` `p` `[` `]` `\`
* **Row 3 (Home Row):** `[ ⌨ ]` `[Caps]` `a` `s` `d` `f` `g` `h` `j` `k` `l` `;` `'` `[Enter]`
* **Row 4 (Shift / Nav):** `[ ⇧ ]` `z` `x` `c` `v` `b` `n` `m` `,` `.` `/` `[↑]` `[ ⇧ ]`
* **Row 5 (Bottom Row):** `[Ctr]` `[Sup]` `[Alt]` `[             Space (8.5)             ]` `[←]` `[↓]` `[→]`

### B. Secondary Layer (`Special` - Non-Alpha Characters, Symbols & Nav):
Accessed by tapping `[ ⌨ ]` on the left of Row 3. Tap `[Abc]` in that exact same position to return to letters.
* **Row 1 (Numbers):** `[Esc]` `1` `2` `3` `4` `5` `6` `7` `8` `9` `0` `-` `=` `[ ⌫ ]`
* **Row 2 (Direct Symbols):** `[Tab]` `~` `!` `@` `#` `$` `%` `^` `&` `*` `(` `)` `_` `+`
* **Row 3 (Brackets & Quotes):** `[Abc]` `[Del]` `` ` `` `[` `]` `{` `}` `\` `|` `;` `:` `'` `"` `[Enter]`
* **Row 4 (Math & Currency):** `[ ⇧ ]` `<` `>` `/` `?` `=` `€` `£` `¥` `°` `±` `[PgUp]` `[Ins]`
* **Row 5 (Nav & Modifiers):** `[Ctr]` `[Sup]` `[Alt]` `[             Space (8.5)             ]` `[Home]` `[PgDn]` `[End]`

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
o.bind("XF86Launch3", "Toggle virtual keyboard", "pkill -x wvkbd-deskintl || pkill -x wvkbd-mobintl || wvkbd-deskintl -L 360", { locked = true })
```

---

### Step 6: Install Multi-Touch Gestures Daemon

#### A. Create `~/.config/hypr/touch_gestures.py`

```bash
cat << 'EOF' > ~/.config/hypr/touch_gestures.py
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

                        # Trigger gesture during active swipe once threshold is exceeded
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
                    # Fingers released
                    if touch_active:
                        if not gesture_fired and max_fingers == 5:
                            send_hypr_dispatch('hl.dsp.window.close()', "5-finger tap -> Close Window")

                        touch_active = False
                        max_fingers = 0
                        gesture_fired = False

if __name__ == '__main__':
    main()
EOF
chmod +x ~/.config/hypr/touch_gestures.py
```

#### B. Create & Enable User Service for Gestures

```bash
cat << 'EOF' > ~/.config/systemd/user/touch-gestures.service
[Unit]
Description=Touchscreen Gestures Daemon
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/.config/hypr/touch_gestures.py
Restart=always
RestartSec=2

[Install]
WantedBy=graphical-session.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now touch-gestures.service
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
   systemctl --user status touch-gestures.service
   ```

2. **Verify Gesture Logs in Real Time:**
   ```bash
   journalctl --user -u touch-gestures.service -f
   ```

3. **Verify Battery Charge Threshold:**
   ```bash
   asusctl battery info
   ```

4. **Verify On-Screen Keyboard & Bitwarden Plugin:**
   * Test Bitwarden panel: Press `SUPER + B` to toggle the status bar Bitwarden vault.
   * Test virtual keyboard: Click the physical tablet side button (`XF86Launch3`).
   * Verify location: `which wvkbd-deskintl` should print `/home/<user>/.local/bin/wvkbd-deskintl`.

-- Tablet On-Screen Virtual Keyboard Toggle
-- Append or merge into ~/.config/hypr/bindings.lua
o.bind("SUPER + B", "Toggle virtual keyboard", "pkill -x wvkbd-deskintl || pkill -x wvkbd-mobintl || /home/jason/.local/bin/wvkbd-deskintl -L 360")
o.bind("XF86Launch3", "Toggle virtual keyboard", "pkill -x wvkbd-deskintl || pkill -x wvkbd-mobintl || /home/jason/.local/bin/wvkbd-deskintl -L 360", { locked = true })

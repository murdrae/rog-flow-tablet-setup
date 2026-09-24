-- Hyprland window rules and personal overrides
-- Append or merge into ~/.config/hypr/hyprland.lua

-- TradingView: Disable follow-mouse focus so hovering over the chart doesn't steal focus
-- from confirmation dialogs and cause them to close (same fix Omarchy uses for JetBrains).
o.window("^tradingview$", { no_follow_mouse = true })

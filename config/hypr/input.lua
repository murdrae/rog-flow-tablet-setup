-- Tablet and Touchscreen input mapping to built-in display
-- Append or merge into ~/.config/hypr/input.lua
hl.config({
  input = {
    float_switch_override_focus = 0,
    touchdevice = {
      output = "eDP-1",
    },
    tablet = {
      output = "eDP-1",
    },
  },
})

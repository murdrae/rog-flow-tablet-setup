#!/usr/bin/env python3
import sys
import re

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <path/to/layout.deskintl.h>")
    sys.exit(1)

path = sys.argv[1]
with open(path, 'r') as f:
    content = f.read()

# 1. Update keys_full
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

# 2. Update keys_special to be a complete non-alpha symbol layout
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

print(f"Successfully patched {path}!")

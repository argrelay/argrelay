#!/usr/bin/env bash

# Simulates keystrokes on specified X11 window to demo `argrelay` interaction.
# See: `docs/dev_notes/screencast_notes.md`.

# The script relies on `xdotool` which, in turn, relies on running GUI in X11.
# If GUI runs in Wayland, it has to be changed, for example:
#     https://apploye.com/help/switch-from-wayland-to-xorg-ubuntu/
# On Fedora 36:
#     grep -r WaylandEnable /etc/gdm/
#     /etc/gdm/custom.conf:WaylandEnable=false

# Define with `s` in value to debug:
if [[ "${ARGRELAY_DEBUG-}" == *s* ]]
then
    set -x
    set -v
fi

# Debug: Print commands before execution:
set -x
# Debug: Print commands after reading from a script:
set -v
# Return non-zero exit code from commands within a pipeline:
set -o pipefail
# Exit on non-zero exit code from a command:
set -e
# Inherit trap on ERR by sub-shells:
set -E
# Error on undefined variables:
set -u

# The process requires two terminal windows:
# - "target" window where keystrokes are simulated
# - "control" window where this script runs to send keystrokes to "target" window

# To specify target window, run this command there:
# xdotool getactivewindow
# The output value should be passed to this script:
target_window="${1}"

# Keystroke delays in ms:
keystroke_delay="100"
# Sleep delays in s:
keystroke_pause="0.1"
step_pause="0.5"
attention_pause="1.0"

function clear_screen {
    # Clear screen and line:
    xdotool key "ctrl+l"
    xdotool key "ctrl+u"
}

function press_tab {
    xdotool key "Tab"
    xdotool sleep "${attention_pause}"
}

# shellcheck disable=SC2120
function press_enter {
    pause_sec="${1:-${attention_pause}}"
    xdotool key "Return"
    xdotool sleep "${pause_sec}"
}

function press_alt_shift_q {
    xdotool keydown "alt"
    xdotool keydown "shift"
    xdotool key "q"
    xdotool keyup "alt"
    xdotool keyup "shift"
    xdotool sleep "${attention_pause}"
}

function type_comment {
    comment_string="${1}"
    type_string "${comment_string}"
}

function type_string {
    typed_string="${1}"
    xdotool type --delay="${keystroke_delay}" "${typed_string}"
    xdotool sleep "${step_pause}"
}

function press_backspace_times {
    press_count="${1}"
    for i in $( seq "${press_count}" )
    do
        xdotool key BackSpace
    done
}

function press_left_arrow_times {
    press_count="${1}"
    for i in $( seq "${press_count}" )
    do
        xdotool key Left
    done
}

function flash_comment_and_remove {
    next_comment="${1}"
    next_comment_len="${#next_comment}"
    type_comment "${next_comment}"
    xdotool sleep "${attention_pause}"
    press_backspace_times "${next_comment_len}"
    xdotool sleep "${step_pause}"
}

# Set window size: width height (in chars):
xdotool windowsize --sync --usehints "${target_window}" 100 42
xdotool sleep 1

# Select target window as active:
xdotool windowactivate "${target_window}"
# Making sure all chars are printed correctly:
# https://bugs.launchpad.net/ubuntu/+source/xdotool/+bug/1609420
setxkbmap -layout us

clear_screen

type_string "asciinema rec --stdin"
press_enter

# Banner:
type_comment "# This screencast demos \`argrelay\` with mocked data."
press_enter "${keystroke_pause}"
press_enter "${keystroke_pause}"
press_enter "${keystroke_pause}"
press_enter "${keystroke_pause}"
press_enter

# Show help:
if false
then
    xdotool sleep "${attention_pause}"
    type_string "l"
    press_tab
    # curr line: lay |

    type_string "h"
    press_tab
    # curr line: lay h|

    type_string "e"
    press_tab
    # curr line: lay help |

    press_enter
fi

# Select function:
if true
then
    # `lay`:
    type_string "l"
    press_tab
    # curr line: lay |

    press_alt_shift_q

    # `goto`:
    type_string "g"
    press_tab
    # curr line: lay goto |

    press_alt_shift_q

    # `service`:
    type_string "s"
    press_tab
    # curr line: lay goto service |

    flash_comment_and_remove "# This fully qualifies one specific function."
    flash_comment_and_remove "# Functions require input which follows now..."

    press_alt_shift_q
fi

# Select service :
if true
then
    # `apac`:
    press_tab
    type_string "a"
    press_tab
    type_string "p"
    press_tab
    # curr line: lay goto service apac |

    # `dev`:
    press_tab
    type_string "d"
    press_tab
    # curr line: lay goto service apac dev |

    # `downstream`:
    press_tab
    type_string "u"
    press_tab
    # curr line: lay goto service apac dev upstream |

    flash_comment_and_remove "# Suggestions are based on the context."

    # Show service options:
    press_tab
    # curr line: lay goto service apac dev upstream s_|
    # Remove service prefix:
    press_backspace_times 2
    xdotool sleep "${attention_pause}"
    # curr line: lay goto service apac dev upstream |

    # Replace `upstream` by `downstream`:
    press_backspace_times 9
    xdotool sleep "${attention_pause}"
    type_string "d"
    press_tab
    # curr line: lay goto service apac dev downstream |

    # Show service options:
    press_tab

    # Replace `dev` by `prod`:
    press_left_arrow_times 12
    xdotool sleep "${attention_pause}"
    press_backspace_times 3
    xdotool sleep "${attention_pause}"
    press_tab
    type_string "p"
    press_tab
    # TODO: instead of modifying `dev`->`prod` in-place, remove `dev`, add `prod` to the tail.
    # curr line: lay goto service apac prod| downstream

    # Move cursor to EOL:
    xdotool key End
    # curr line: lay goto service apac prod downstream |
    press_tab
    # curr line: lay goto service apac prod downstream |

    flash_comment_and_remove "# Wait a sec..."
fi

# Demo describe:
if true
then
    xdotool key "ctrl+c"

    press_enter "${keystroke_pause}"
    press_enter "${keystroke_pause}"
    press_enter "${keystroke_pause}"
    press_enter "${keystroke_pause}"
    press_enter
    type_comment "# What is going on...?!?!?!"

    press_enter
    type_comment "# Alt+Shift+Q can explain."
    press_enter "${keystroke_pause}"

    press_enter
    type_string "lay goto service "
    # curr line: lay goto service |
    next_comment="# = All possible services."
    type_comment "${next_comment}"
    # curr line: lay goto service # = All possible services.|

    press_alt_shift_q

    press_backspace_times "${#next_comment}"
    # curr line: lay goto service |
    flash_comment_and_remove "# Alt+Shift+Q was pressed."

    type_string "prod upstream apac "
    # curr line: lay goto service prod upstream apac |

    next_comment="# = Limit by \"prod upstream apac\"."
    type_comment "${next_comment}"
    # curr line: lay goto service prod upstream apac # Limit by "prod upstream apac".|

    press_alt_shift_q

    press_backspace_times "${#next_comment}"
    flash_comment_and_remove "# Alt+Shift+Q was pressed again."

    # curr line: lay goto service prod upstream apac |
    xdotool sleep "${attention_pause}"
    press_backspace_times 55
    type_comment "# Alt+Shift+Q (producing the output above) lists options based on:"

    press_enter
    type_comment "#     (A) already made choices, and"

    press_enter
    type_comment "#     (B) data limited by these choices."

    press_enter
    type_comment "# It shows already selected function to run = (A): 1 possible candidate."
    press_enter
    type_comment "# The function requires selecting a service = (B): 6 possible candidates."
fi

if true
then
    press_enter "${keystroke_pause}"
    press_enter
    type_comment "# Can selection be done by any property?"
    press_enter
    type_comment "# Yep."
    press_enter
    type_comment "# For example, what if only IP address is known?"
    press_enter

    press_enter
    type_string "lay goto service "
    # curr line: lay goto service |

    press_alt_shift_q

    type_string "ip.192.168.7"
    press_tab
    type_string "2"
    press_tab
    # curr line: lay goto service ip.192.168.7.2 |

    press_alt_shift_q

    flash_comment_and_remove "# Everything is auto-selected by one IP!"

    xdotool key "ctrl+c"

    press_enter
    type_comment "# But how?"

    press_enter "${keystroke_pause}"
    press_enter
    type_comment "# It turns out there is only one service with that IP address,"
    press_enter
    type_comment "# which makes all other options disambiguated (narrowed down to 1)."
fi

if true
then
    press_enter "${keystroke_pause}"
    press_enter "${keystroke_pause}"
    press_enter "${keystroke_pause}"
    press_enter "${keystroke_pause}"
    press_enter
    type_comment "# \`argrelay\` is extensible by:"
    press_enter
    type_comment "#    (A) external|internal functions (commands to delegate to)"
    press_enter
    type_comment "#    (B) data sources"
    press_enter
    type_comment "#    (C) syntax interpreters"

    press_enter "${keystroke_pause}"
    press_enter
    type_comment "# Any standard shell composition obviously works too."
    press_enter
    type_comment "# Let's try \"list\" function - it retrieves N services (instead of 1 for \"goto\")."

    press_enter "${keystroke_pause}"
    press_enter
    type_string "lay list service | grep dc.22"
    press_enter

    press_enter
    xdotool sleep "${step_pause}"
    xdotool key Up
    # curr line: lay list service | grep dc.22|
    xdotool sleep "${step_pause}"
    press_backspace_times 10
    xdotool sleep "${step_pause}"
    type_string "wc -l"
    press_enter

    press_enter
    xdotool sleep "${step_pause}"
    xdotool key Up
    # curr line: lay list service | wc -l|
    xdotool sleep "${step_pause}"
    press_left_arrow_times 8
    xdotool sleep "${step_pause}"
    type_string " d"
    press_tab
    # curr line: lay list service dev | wc -l
    press_enter
fi

press_enter "${keystroke_pause}"
press_enter "${keystroke_pause}"
press_enter "${keystroke_pause}"
press_enter "${keystroke_pause}"
press_enter
type_comment "# Try it yourself by running \`@/exe/relay_demo.bash\` from this repo:"
press_enter
type_comment "# https://github.com/argrelay/argrelay"
press_enter
type_string "exit"
press_enter

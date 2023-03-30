// GUI argrelay client
// It is a self-contained minimalistic client for demo only.
// TODO: set up E2E tests

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Relevant elements

const command_history_elem = document.querySelector("#command_history");
const command_line_input_elem = document.querySelector("#command_line_input");
const suggestion_output_elem = document.querySelector("#suggestion_output");
const describe_output_elem = document.querySelector("#describe_output");
const invocation_output = document.querySelector("#invocation_output");

const command_history_option_temp = document.querySelector("#command_history_option_temp");
const suggested_item_temp = document.querySelector("#suggested_item_temp");
const envelope_container_temp = document.querySelector("#envelope_container_temp")
const arg_container_temp = document.querySelector("#arg_container_temp")

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// API URL-s

const propose_arg_values_url = document.currentScript.getAttribute("propose_arg_values_url");
const describe_line_args_url = document.currentScript.getAttribute("describe_line_args_url");
const relay_line_args_url = document.currentScript.getAttribute("relay_line_args_url");

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Global state

const command_history_key = "command_history"
const command_history_max_size = 10
let command_history_list = []

let suggested_token_list = []
let common_token_prefix = ""

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Event listeners registration

// Detect changes and cursor moves within command line input:
// https://stackoverflow.com/a/50661249/441652
for (const event_type of [
    "focusin",
    "keyup",
    "mouseup",
    "touchstart",
    "input",
    "paste",
    "cut",
    "select",
    "selectstart",
]) {
    command_line_input_elem.addEventListener(
        event_type,
        handle_command_line_change,
    );
}
command_line_input_elem.addEventListener(
    "keydown",
    handle_keydown,
);

command_history_elem.addEventListener(
    "click",
    handle_select_history,
)

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Server requests

function fetch_completion_response(
    input_line,
    cursor_cpos,
) {
    fetch(
        propose_arg_values_url,
        {
            method: "POST",
            headers: {
                "Accept": "text/plain",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "command_line": input_line,
                "comp_type": "PrefixShown",
                "cursor_cpos": cursor_cpos.toString(),
                "is_debug_enabled": false,
            }),
        }
    )
        .then(server_response => server_response.text())
        .then(response_text => {
            populate_suggestions(response_text);
        })
}

function fetch_description_response(
    input_line,
    cursor_cpos,
) {
    fetch(
        describe_line_args_url,
        {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "command_line": input_line,
                "comp_type": "DescribeArgs",
                "cursor_cpos": cursor_cpos.toString(),
                "is_debug_enabled": false,
            }),
        }
    )
        .then(server_response => server_response.json())
        .then(response_json => {
            outline_search_plan(response_json)
        })
}

function fetch_invocation_response(
    input_line,
    cursor_cpos,
) {
    fetch(
        relay_line_args_url,
        {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                "command_line": input_line,
                "comp_type": "InvokeAction",
                "cursor_cpos": cursor_cpos.toString(),
                "is_debug_enabled": false,
            }),
        }
    )
        .then(server_response => server_response.json())
        .then(response_json => invocation_output.textContent = JSON.stringify(response_json, null, 4))
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Command history

function handle_select_history(
    input_event,
) {
    command_line_input_elem.value = input_event.target.options[input_event.target.selectedIndex].text;
    on_command_line_change(command_line_input_elem);
}

function load_command_history() {
    command_history_list = localStorage.getItem(command_history_key);
    if (command_history_list == null) {
        command_history_list = [];
    } else {
        command_history_list = JSON.parse(command_history_list);
    }

    remove_child_elements(command_history_elem);
    for (let i = 0; i < command_history_list.length; i++) {
        const command_history_item = command_history_list[i]
        const command_history_option_elem = command_history_option_temp.content.cloneNode(true).children[0];
        command_history_option_elem.value = i
        command_history_option_elem.innerText = command_history_item
        command_history_elem.append(command_history_option_elem)
    }
}

function store_command_line_history(
    command_line_text,
) {
    // Skip if existing:
    command_line_text = command_line_text.trim()
    for (const command_history_item of command_history_list) {
        if (command_history_item === command_line_text) {
            return;
        }
    }
    // Insert head:
    command_history_list = [command_line_text].concat(command_history_list)
    // Truncate tail:
    command_history_list = command_history_list.slice(0, command_history_max_size);
    localStorage.setItem(command_history_key, JSON.stringify(command_history_list));
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Client logic

function handle_command_line_change(
    input_event,
) {
    on_command_line_change(input_event.target);
}

function on_command_line_change(command_line_element) {
    const input_line = command_line_element.value
    const cursor_cpos = command_line_element.selectionStart
    fetch_completion_response(input_line, cursor_cpos);
    fetch_description_response(input_line, cursor_cpos);
}

function handle_keydown(
    input_event,
) {
    switch (input_event.key) {
        case "Tab":
            // Prevent Tab from changing focus on another element:
            input_event.preventDefault();
            const replacement_string = (suggested_token_list.length === 1 && common_token_prefix.length !== 0)
                // If it is single suggestion, it should finalize current token.
                // Therefore, add space after replaced token (to suggest next):
                ? common_token_prefix + " "
                : common_token_prefix
            complete_curr_token(input_event.target, replacement_string);
            break;
        case "Enter":
            const input_line = input_event.target.value;
            const cursor_cpos = input_event.target.selectionStart;
            store_command_line_history(input_event.target.value);
            load_command_history()
            fetch_invocation_response(input_line, cursor_cpos);
            break;
        default:
            return;
    }
}

function on_suggestion_click(
    input_event,
) {
    const suggested_item_elem = input_event.target;
    use_selected_suggestion(suggested_item_elem);
}

function use_selected_suggestion(suggested_item_elem) {
    if (!suggested_item_elem.classList.contains("suggested_item")) {
        // handle by parent:
        use_selected_suggestion(suggested_item_elem.parentNode);
        return
    }

    // Concatenate inner text of all span elements without outter formatting whitespaces:
    let suggested_text = "";
    for (const span_child of suggested_item_elem.children) {
        suggested_text += span_child.textContent;
    }

    // See FS_71_87_33_52 help_hint:
    // Server provides suggestion with extra comment after a space.
    // Comment does not necessarily start with `#`.
    const space_ipos = suggested_text.indexOf(" ")
    const suggestion_only = space_ipos >= 0
        ? suggested_text.substring(0, space_ipos)
        : suggested_text

    // Selecting exact suggestions always completes token - append space to suggest next:
    const replacement_string = suggestion_only + " ";
    complete_curr_token(command_line_input_elem, replacement_string);
}

function populate_suggestions(response_text) {
    // Store suggested tokens in a separate list:
    suggested_token_list = response_text
        .split(/\r?\n/)
        // Filter empty strings:
        .filter(suggested_token => suggested_token);

    // Get common prefix from suggestions:
    common_token_prefix = longest_common_prefix(suggested_token_list)

    const input_sting = command_line_input_elem.value;
    const cursor_ipos_start = command_line_input_elem.selectionStart;
    const cursor_ipos_end = command_line_input_elem.selectionEnd;
    const [
        token_ipos_start,
        token_ipos_end,
    ] = describe_curr_token(
        input_sting,
        cursor_ipos_start,
        cursor_ipos_end,
    );
    const input_part_string = input_sting.substring(token_ipos_start, cursor_ipos_start)

    remove_child_elements(suggestion_output_elem);
    // Append new children:
    for (let i = 0; i < suggested_token_list.length; i++) {
        const suggested_token_text = suggested_token_list[i];
        const suggested_item_elem = suggested_item_temp.content.cloneNode(true).children[0];
        suggested_item_elem.addEventListener(
            "click",
            on_suggestion_click,
        );

        const space_ipos = suggested_token_text.indexOf(" ");
        const suggestion_only = space_ipos >= 0
            ? suggested_token_text.substring(0, space_ipos)
            : suggested_token_text;

        const incomplete_part_string = suggestion_only.substring(input_part_string.length, common_token_prefix.length);
        const unique_part_string = suggestion_only.substring(common_token_prefix.length);
        const comment_part_string = space_ipos >= 0
            ? suggested_token_text.substring(space_ipos)
            : "";

        const input_part_elem = suggested_item_elem.querySelector(".input_part");
        const incomplete_part_elem = suggested_item_elem.querySelector(".incomplete_part");
        const unique_part_elem = suggested_item_elem.querySelector(".unique_part");
        const comment_part_elem = suggested_item_elem.querySelector(".comment_part");

        input_part_elem.textContent = input_part_string;
        incomplete_part_elem.textContent = incomplete_part_string;
        unique_part_elem.textContent = unique_part_string;
        comment_part_elem.textContent = comment_part_string;

        suggestion_output_elem.append(suggested_item_elem);
    }
}

function complete_curr_token(input_elem, replacement_string) {
    console.assert(command_line_input_elem === input_elem);
    const input_sting = input_elem.value;
    const cursor_ipos_start = input_elem.selectionStart;
    const cursor_ipos_end = input_elem.selectionEnd;
    const [
        result_string,
        token_ipos_start,
    ] = replace_curr_token(
        input_sting,
        cursor_ipos_start,
        cursor_ipos_end,
        replacement_string,
    );
    input_elem.value = result_string;
    const new_cursor_ipos = token_ipos_start + replacement_string.length;
    input_elem.focus();
    input_elem.setSelectionRange(new_cursor_ipos, new_cursor_ipos);
}

/**
 * Return range for curr token (based on selection)
 */
function describe_curr_token(
    input_sting,
    cursor_ipos_start,
    cursor_ipos_end,
) {
    const prev_space_index = input_sting.lastIndexOf(" ", cursor_ipos_start - 1);
    const next_space_index = input_sting.indexOf(" ", cursor_ipos_end);
    const token_ipos_start = prev_space_index < 0 ? 0 : prev_space_index + 1;
    const token_ipos_end = next_space_index < 0 ? input_sting.length : next_space_index;
    return [
        token_ipos_start,
        token_ipos_end,
    ];
}

/**
 * Detect ipos range of curr token (pointed by cursor/caret) and replace it with `replacement_string`.
 *
 * Return list [result_string, token_ipos_start]
 */
function replace_curr_token(
    input_sting,
    cursor_ipos_start,
    cursor_ipos_end,
    replacement_string,
) {
    const [
        token_ipos_start,
        token_ipos_end,
    ] = describe_curr_token(
        input_sting,
        cursor_ipos_start,
        cursor_ipos_end,
    );
    const result_string = (
        input_sting.substring(0, token_ipos_start)
        +
        replacement_string
        +
        input_sting.substring(token_ipos_end)
    )
    return [
        result_string,
        token_ipos_start,
    ];
}

function longest_common_prefix(
    string_list,
) {
    let common_prefix = "";
    if (string_list.length !== 0) {
        // Iterate over chars within one string to check if they exist in other strings:
        const first_string = string_list[0];
        for (let i = 0; i < first_string.length; i++) {
            if (string_list.every(curr_string => curr_string.charAt(i) === first_string.charAt(i))) {
                common_prefix += first_string.charAt(i);
            } else {
                break;
            }
        }
    }
    return common_prefix;
}

function remove_child_elements(
    parent_elem,
) {
    while (parent_elem.firstChild) {
        parent_elem.removeChild(parent_elem.lastChild);
    }
}

// Equivalent of `InterpResult.describe_data`:
function outline_search_plan(
    response_json,
) {
    populate_envelope_containers(response_json);
}

// Equivalent of `EnvelopeContainer.describe_data`:
function populate_envelope_containers(
    response_json,
) {
    remove_child_elements(describe_output_elem);
    let is_first_missing_found = false;
    for (const envelope_container of response_json.envelope_containers) {

        const envelope_container_elem = envelope_container_temp.content.cloneNode(true).children[0]

        const envelope_class_elem = envelope_container_elem.querySelector(".envelope_class")
        const found_count_elem = envelope_container_elem.querySelector(".found_count")
        const arg_list_container_elem = envelope_container_elem.querySelector(".arg_list_container")
        envelope_class_elem.textContent = envelope_container.search_control.envelope_class + ": "
        found_count_elem.textContent = envelope_container.found_count

        for (const key_to_type_dict of envelope_container.search_control.keys_to_types_list) {

            const arg_key = Object.keys(key_to_type_dict)[0];
            const arg_type = key_to_type_dict[arg_key];

            const arg_container_elem = arg_container_temp.content.cloneNode(true).children[0]

            const arg_type_elem = arg_container_elem.querySelector(".arg_type")
            const arg_value_elem = arg_container_elem.querySelector(".arg_value")
            const arg_source_elem = arg_container_elem.querySelector(".arg_source")
            const remaining_values_elem = arg_container_elem.querySelector(".remaining_values")

            if (arg_type in envelope_container.assigned_types_to_values) {
                arg_type_elem.textContent = arg_type + ": "
                arg_value_elem.textContent = envelope_container.assigned_types_to_values[arg_type].arg_value
                arg_source_elem.textContent = `[${envelope_container.assigned_types_to_values[arg_type].arg_source}]`

                if (envelope_container.assigned_types_to_values[arg_type].arg_source === "ExplicitPosArg") {
                    arg_container_elem.classList.add("explicit_arg_value");
                } else {
                    arg_container_elem.classList.add("selected_arg_value");
                }
            } else if (arg_type in envelope_container.remaining_types_to_values) {
                if (!is_first_missing_found) {
                    arg_type_elem.textContent = "*" + arg_type + ": ";
                    is_first_missing_found = true;
                } else {
                    arg_type_elem.textContent = arg_type + ": ";
                }
                arg_value_elem.textContent = "?";
                arg_source_elem.textContent = "";
                remaining_values_elem.textContent = envelope_container.remaining_types_to_values[arg_type].join(" ")

                arg_type_elem.classList.add("unknown_arg_value");
                arg_type_elem.classList.add("unknown_arg_value");
                remaining_values_elem.classList.add("suggested_arg_value");
            } else {
                arg_type_elem.textContent = arg_type + ": ";
                arg_value_elem.textContent = "[none]";
                arg_container_elem.classList.add("no_data");
            }

            arg_list_container_elem.append(arg_container_elem)
        }

        describe_output_elem.append(envelope_container_elem)
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main

load_command_history();
on_command_line_change(command_line_input_elem);
command_line_input_elem.focus();

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

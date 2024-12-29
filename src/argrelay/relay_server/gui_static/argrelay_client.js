// GUI argrelay client
// It is a self-contained minimalistic client for demo only.

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

const remaining_item_temp = document.querySelector("#remaining_item_temp");

const reset_all_elem = document.querySelector("#id_reset_all_button")

const outer_spinner_elem = document.querySelector("#outer_spinner")
const inner_spinner_elem = document.querySelector("#inner_spinner")
const copy_command_elem = document.querySelector("#id_copy_command_button")
const copy_link_elem = document.querySelector("#id_copy_link_button")

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// API URL-s

const propose_arg_values_url = document.currentScript.getAttribute("propose_arg_values_url");
const describe_line_args_url = document.currentScript.getAttribute("describe_line_args_url");
const relay_line_args_url = document.currentScript.getAttribute("relay_line_args_url");

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Misc script params

const argrelay_gui_url = document.currentScript.getAttribute("argrelay_gui_url");
const server_start_time = new Date(document.currentScript.getAttribute("server_start_time"));
const command_line = document.currentScript.getAttribute("command_line");

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Params from `PluginType.ConfiguratorPlugin`

// Converts Unix time to Date object with local time zone:
const project_git_commit_time = new Date(document.currentScript.getAttribute("project_git_commit_time"));

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Global state

const abort_error_reason = "input invalidated";

const generated_client_uid_key = "generated_client_uid";
let generated_client_uid_value = null;

const static_client_conf_target = "_embedded_web_";

const command_history_key = "command_history";
const command_history_max_size = 10;
// NOTE: Match it with `animation-duration` in `*.css` file:
const request_delay_ms = 800;
const clipboard_disabled = "clipboard disabled";
let command_history_list = [];
let input_version = 0;

let last_suggested_token_list = null;
let last_search_response_json = null;

let common_token_prefix = "";

class abstract_state_class {

    // TODO: rename from state_name to something else (or rename io_state):
    state_name = null

    // synced_* = last received from the server and synced with output GUI
    // request_* = last sent to the server (pending response)
    // curr_* = last received from input GUI

    synced_input_line = null
    synced_cursor_cpos = null

    request_input_line = null
    request_cursor_cpos = null

    curr_input_line = null
    curr_cursor_cpos = null
    curr_version = -1

    timer_id = -1

    io_state = "client_synced"

    request_controller = new AbortController()

    constructor(state_name) {
        this.state_name = state_name
    }

    update_synced_state() {
        this.synced_input_line = this.request_input_line;
        this.synced_cursor_cpos = this.request_cursor_cpos;
    }

    update_request_state() {
        this.request_input_line = this.curr_input_line;
        this.request_cursor_cpos = this.curr_cursor_cpos;
    }

    is_synced_state_equal() {
        return (
            this.synced_input_line === this.curr_input_line
            &&
            this.synced_cursor_cpos === this.curr_cursor_cpos
        );
    }

    is_request_state_equal() {
        return (
            this.request_input_line === this.curr_input_line
            &&
            this.request_cursor_cpos === this.curr_cursor_cpos
        );
    }

    reset_request_controller() {
        this.request_controller.abort(abort_error_reason);
        this.request_controller = new AbortController();
        this.request_controller.signal.addEventListener("abort", () => {
            console.log(`[${this.state_name}] attempt to abort request if any`);
        });
    }

    map_io_state_to_gui_state() {
        console.log(`[${this.state_name}] io_state: ${this.io_state}`)
        console.trace()
    }

    set_io_state_client_synced() {
        if (this.io_state !== "client_synced") {
            this.io_state = "client_synced";
            this.map_io_state_to_gui_state();
        }
    }

    set_io_state_pending_request() {
        if (this.io_state !== "pending_request") {
            this.io_state = "pending_request";
            this.map_io_state_to_gui_state();
        }
    }

    set_io_state_pending_response() {
        if (this.io_state !== "pending_response") {
            this.io_state = "pending_response";
            this.map_io_state_to_gui_state();
        }
    }

    set_io_state_request_failed() {
        if (this.io_state !== "request_failed") {
            this.io_state = "request_failed";
            this.map_io_state_to_gui_state();
        }
    }

    schedule_update(
        curr_version,
        curr_input_line,
        curr_cursor_cpos,
    ) {
        this.curr_version = curr_version;
        this.curr_input_line = curr_input_line;
        this.curr_cursor_cpos = curr_cursor_cpos;

        if (this.is_synced_state_equal()) {
            this.set_io_state_client_synced()
            return
        }
        if (this.is_request_state_equal() && this.io_state === "pending_response") {
            return
        }
        this.set_io_state_pending_request()

        clearInterval(this.timer_id);
        const version_scheduled = curr_version;
        const curr_state = this;
        this.timer_id = setInterval(
            function () {
                clearInterval(curr_state.timer_id);
                if (version_scheduled === curr_state.curr_version) {
                    // No changes to version happened since start of the delay:
                    curr_state.outer_fetch_func();
                } else {
                    // Version has changed since start of the delay - just wait for the next timeout.
                }
            },
            request_delay_ms,
        );
    }

    invalidate_state() {
        throw new Error("it must be overridden")
    }

    outer_fetch_func() {
        if (this.is_synced_state_equal()) {
            this.set_io_state_client_synced()
            return
        }
        switch (this.io_state) {
            case "client_synced":
                // make new request:
                this.set_io_state_pending_response();
                break
            case "pending_request":
                // make new request:
                this.set_io_state_pending_response();
                break
            case "pending_response":
                if (this.is_request_state_equal()) {
                    // wait for response:
                    return
                } else {
                    // invalidate previous request:
                }
                break
            case "request_failed":
                this.set_io_state_request_failed();
                // wait for input
                return
            default:
                console.log(`[${this.state_name}] io_state: ${this.io_state}`)
                console.trace()
                throw new Error("it must be not reachable")
        }
        this.update_request_state();
        this.reset_request_controller();
        this.inner_fetch_func();
    }

    inner_fetch_func() {
        console.log(`[${this.state_name}] starting new request`);
        this
            .create_fetch_promise()
            .then(server_response => {
                if (server_response.ok) {
                    return this
                        .process_response(server_response)
                        .finally(() => {
                            if (this.is_request_state_equal()) {
                                this.update_gui()
                                this.update_synced_state()
                            }
                        })
                } else {
                    this.invalidate_state()
                }
            })
            .catch(error_reason => {
                if (error_reason !== abort_error_reason) {
                    console.log(`[${this.state_name}] failed with error_reason: ${error_reason}`)
                    this.set_io_state_request_failed()
                } else {
                    console.log(`[${this.state_name}] ignored with error_reason: ${error_reason}`)
                }
            })
            // Trigger check if input changed:
            .finally(() => {
                if (this.io_state !== "request_failed") {
                    on_command_line_change()
                }
            })
    }

    create_fetch_promise() {
        throw new Error("it must be overridden")
    }

    map_io_state_to_command_line_input_elem_class(some_io_state) {
        throw new Error("it must be overridden")
    }

    process_response(server_response) {
        throw new Error("it must be overridden")
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// suggest_state

class suggest_state_class extends abstract_state_class {

    create_fetch_promise() {
        return fetch(
            propose_arg_values_url,
            {
                signal: this.request_controller.signal,
                method: "POST",
                headers: {
                    "Accept": "text/plain",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "client_uid": generated_client_uid_value,
                    "client_conf_target": static_client_conf_target,
                    "server_action": "ProposeArgValues",
                    "command_line": this.request_input_line,
                    "cursor_cpos": this.request_cursor_cpos.toString(),
                    "comp_scope": "ScopeInitial",
                    "is_debug_enabled": false,
                }),
            }
        )
    }

    map_io_state_to_gui_state() {
        super.map_io_state_to_gui_state()

        // Set color:
        for (const some_io_state of [
            "client_synced",
            "pending_request",
            "pending_response",
            "request_failed",
        ]) {
            for (const elem_obj of [
                command_line_input_elem,
                outer_spinner_elem,
            ]) {
                if (some_io_state === this.io_state) {
                    elem_obj.classList.add(this.map_io_state_to_command_line_input_elem_class(some_io_state));
                } else {
                    elem_obj.classList.remove(this.map_io_state_to_command_line_input_elem_class(some_io_state));
                }
            }
        }

        if ([
            "pending_request",
        ].includes(this.io_state)) {
            outer_spinner_elem.classList.remove("spinner_paused");
        } else {
            outer_spinner_elem.classList.add("spinner_paused");
        }
        if ([
            "pending_response",
        ].includes(this.io_state)) {
            inner_spinner_elem.classList.remove("spinner_paused");
        } else {
            inner_spinner_elem.classList.add("spinner_paused");
        }
    }

    map_io_state_to_command_line_input_elem_class(some_io_state) {
        switch (some_io_state) {
            case "client_synced":
                return "io_state_client_synced_input"
            case "pending_request":
                return "io_state_pending_request_input"
            case "pending_response":
                return "io_state_pending_response_input"
            case "request_failed":
                return "io_state_request_failed_input"
        }
    }

    invalidate_state() {
        last_suggested_token_list = null;
    }

    update_gui() {
        populate_suggestions()
        scroll_line_to_top()
    }

    process_response(server_response) {
        return server_response
            .text()
            .then(response_text => {
                last_suggested_token_list = response_text
                    .split(/\r?\n/)
                    // Filter empty strings:
                    .filter(suggested_token => suggested_token);
            })
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// search_state

class search_state_class extends abstract_state_class {

    create_fetch_promise() {
        return fetch(
            describe_line_args_url,
            {
                signal: this.request_controller.signal,
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "client_uid": generated_client_uid_value,
                    "client_conf_target": static_client_conf_target,
                    "server_action": "DescribeLineArgs",
                    "command_line": this.request_input_line,
                    "cursor_cpos": this.request_cursor_cpos.toString(),
                    "comp_scope": "ScopeInitial",
                    "is_debug_enabled": false,
                }),
            }
        )
    }

    invalidate_state() {
        last_search_response_json = null;
    }

    update_gui() {
        outline_search_plan()
        scroll_line_to_top()
    }

    process_response(server_response) {
        return server_response
            .json()
            .then(response_json => {
                last_search_response_json = response_json;
            })
    }
}

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

reset_all_elem.addEventListener(
    "click",
    handle_reset_all,
)

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Server requests

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
                "client_uid": generated_client_uid_value,
                "client_conf_target": static_client_conf_target,
                "server_action": "RelayLineArgs",
                "command_line": input_line,
                "cursor_cpos": cursor_cpos.toString(),
                "comp_scope": "ScopeInitial",
                "is_debug_enabled": false,
            }),
        }
    )
        .then(server_response => server_response.json())
        .then(response_json => invocation_output.textContent = JSON.stringify(response_json, null, 4))
        .catch(error_reason => console.log(`error_reason: ${error_reason}`));
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// states

let suggest_state = new suggest_state_class("search_state");
let search_state = new search_state_class("search_state");

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//

function set_clipboard_state() {
    if (typeof (navigator.clipboard) === "undefined") {
        copy_command_elem.title = clipboard_disabled;
        copy_link_elem.title = clipboard_disabled;
        copy_command_elem.classList.add("button_disabled");
        copy_link_elem.classList.add("button_disabled");
    } else {
        copy_command_elem.addEventListener(
            "click",
            handle_copy_command,
        )
        copy_link_elem.addEventListener(
            "click",
            handle_link_command,
        )
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// client_uid

function generate_client_uid() {
    generated_client_uid_value = localStorage.getItem(generated_client_uid_key);
    if (generated_client_uid_value == null) {
        const random_suffix = Math.floor(Math.random() * 1_000_000_000_000).toString().padStart(12, "0");
        generated_client_uid_value = `client_uid_${random_suffix}`;
        localStorage.setItem(generated_client_uid_key, JSON.stringify(generated_client_uid_value));
    } else {
        generated_client_uid_value = JSON.parse(generated_client_uid_value);
    }
}

function handle_reset_all(
    input_event,
) {
    history.replaceState(null, "", argrelay_gui_url);
    command_line_input_elem.value = "";
    invocation_output.textContent = "";
    on_command_line_change();
    command_line_input_elem.focus();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Copy buttons

function handle_copy_command(
    input_event,
) {
    navigator.clipboard.writeText(command_line_input_elem.value);
}

function handle_link_command(
    input_event,
) {
    const next_path = argrelay_gui_url + encodeURI(command_line_input_elem.value.trim());
    const next_link = location.origin + next_path;
    navigator.clipboard.writeText(next_link);
    history.replaceState(null, "", next_path);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Command history

function handle_select_history(
    input_event,
) {
    command_line_input_elem.value = input_event.target.options[input_event.target.selectedIndex].text;
    on_command_line_change();
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
    command_line_text = command_line_text.trim()
    // Remove if existing (to be inserted as head instead):
    const line_index = command_history_list.indexOf(command_line_text);
    if (line_index >= 0) {
        command_history_list.splice(line_index, 1);
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
    console.assert(command_line_input_elem === input_event.target);
    on_command_line_change();
}

function on_command_line_change() {
    const curr_input_line = command_line_input_elem.value;
    const curr_cursor_cpos = command_line_input_elem.selectionStart;
    input_version++;
    suggest_state.schedule_update(input_version, curr_input_line, curr_cursor_cpos);
    // TODO: re-consider: trigger update after suggestion response, not together:
    search_state.schedule_update(input_version, curr_input_line, curr_cursor_cpos);
}

function handle_keydown(
    input_event,
) {
    switch (input_event.key) {
        case "Tab":
            // Prevent Tab from changing focus on another element:
            input_event.preventDefault();
            const replacement_string = (last_suggested_token_list.length === 1 && common_token_prefix.length !== 0)
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

function on_remaining_click(
    input_event,
) {
    const remaining_item_elem = input_event.target;
    use_selected_remaining(remaining_item_elem);
}

function use_selected_suggestion(suggested_item_elem) {
    if (!suggested_item_elem.classList.contains("suggested_item")) {
        // handle by parent:
        use_selected_suggestion(suggested_item_elem.parentNode);
        return
    }

    // Concatenate inner text of all span elements without outer formatting whitespaces:
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

function use_selected_remaining(remaining_item_elem) {

    // Concatenate inner text of all span elements without outer formatting whitespaces:
    const remaining_only = remaining_item_elem.textContent;

    // Selecting exact suggestions always completes token - append space to suggest next:
    const replacement_string = remaining_only + " ";
    complete_curr_token(command_line_input_elem, replacement_string);
}

function populate_suggestions() {
    console.assert(last_suggested_token_list != null);
    // Get common prefix from suggestions:
    common_token_prefix = longest_common_prefix(last_suggested_token_list);

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
    console.log(`input_part_string: "${input_part_string}" ; common_token_prefix: "${common_token_prefix}" ; input_sting: "${input_sting}"[${cursor_ipos_start}:${cursor_ipos_end}] ; token_ipos_start: ${token_ipos_start}`);

    remove_child_elements(suggestion_output_elem);
    // Append new children:
    for (let i = 0; i < last_suggested_token_list.length; i++) {
        const suggested_token_text = last_suggested_token_list[i];
        const suggested_item_elem = suggested_item_temp.content.cloneNode(true).children[0];
        suggested_item_elem.addEventListener(
            "click",
            on_suggestion_click,
        );

        // Remove comment (FS_71_87_33_52 help_hint):
        const space_ipos = suggested_token_text.indexOf(" ");
        const suggestion_only = space_ipos >= 0
            ? suggested_token_text.substring(0, space_ipos)
            : suggested_token_text;
        const comment_part_string = space_ipos >= 0
            ? suggested_token_text.substring(space_ipos)
            : "";

        // What is already typed in:
        const incomplete_part_string = suggestion_only.substring(input_part_string.length, common_token_prefix.length);
        // What is remaining of suggestion (beyond common prefix):
        const unique_part_string = suggestion_only.substring(common_token_prefix.length);

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
    if (suggest_state.io_state !== "client_synced") {
        return;
    }
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

function scroll_line_to_top() {
    command_line_input_elem.scrollIntoView(true);
}

// Equivalent of `ClientResponseHandlerDescribeLineArgs.render_result`:
function outline_search_plan() {
    console.assert(last_search_response_json != null);
    populate_envelope_containers(last_search_response_json);
}

// Equivalent of `ClientResponseHandlerDescribeLineArgs.render_envelope_containers`:
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
        envelope_class_elem.textContent = envelope_container.search_control.collection_name + ": "
        found_count_elem.textContent = envelope_container.found_count

        for (const arg_name_to_prop_name_entry of envelope_container.search_control.arg_name_to_prop_name_map) {

            const arg_name = Object.keys(arg_name_to_prop_name_entry)[0];
            const prop_name = arg_name_to_prop_name_entry[arg_name];

            const arg_container_elem = arg_container_temp.content.cloneNode(true).children[0]

            const prop_name_elem = arg_container_elem.querySelector(".prop_name")
            const prop_value_elem = arg_container_elem.querySelector(".prop_value")
            const value_source_elem = arg_container_elem.querySelector(".value_source")
            const remaining_values_elem = arg_container_elem.querySelector(".remaining_values")

            if (prop_name in envelope_container.assigned_prop_name_to_prop_value) {
                prop_name_elem.textContent = prop_name + ": "
                prop_value_elem.textContent = envelope_container.assigned_prop_name_to_prop_value[prop_name].prop_value
                value_source_elem.textContent = `[${envelope_container.assigned_prop_name_to_prop_value[prop_name].value_source}]`

                if ([
                    "explicit_offered_arg",
                    "explicit_dictated_arg",
                ].includes(envelope_container.assigned_prop_name_to_prop_value[prop_name].value_source)) {
                    arg_container_elem.classList.add("explicit_arg_value");
                } else {
                    arg_container_elem.classList.add("implicit_arg_value");
                }
            } else if (prop_name in envelope_container.remaining_prop_name_to_prop_value) {
                if (!is_first_missing_found) {
                    prop_name_elem.textContent = "*" + prop_name + ": ";
                    is_first_missing_found = true;
                } else {
                    prop_name_elem.textContent = prop_name + ": ";
                }
                prop_value_elem.textContent = "?";
                value_source_elem.textContent = "";
                for (const remaining_value of envelope_container.remaining_prop_name_to_prop_value[prop_name]) {
                    const remaining_item_elem = remaining_item_temp.content.cloneNode(true).children[0];
                    remaining_item_elem.addEventListener(
                        "click",
                        on_remaining_click,
                    );
                    remaining_item_elem.textContent = remaining_value;
                    remaining_values_elem.append(remaining_item_elem);
                }

                prop_name_elem.classList.add("unknown_arg_value");
            } else {
                prop_name_elem.textContent = prop_name + ": ";
                // See: SpecialChar.NoPropValue:
                prop_value_elem.textContent = "~";
                arg_container_elem.classList.add("no_data");
            }

            arg_list_container_elem.append(arg_container_elem)
        }

        describe_output_elem.append(envelope_container_elem)
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Format time to zoned:
// https://stackoverflow.com/a/17415677/441652

function format_time_to_zoned(
    zoned_time,
) {
    // Time offset part of `zoned_time`:
    const offset_mins = - zoned_time.getTimezoneOffset();
    // Date-time part of `zoned_time`:
    const date_time = new Date(zoned_time.getTime() + offset_mins * 60 * 1000);
    const offset_sign = offset_mins >= 0 ? "+" : "-";
    pad = function(num) {
        return (num < 10 ? "0" : "") + num;
    };
    const formatted_zoned_date_time = date_time
        // ISO without sub-seconds and trailing chars:
        .toISOString().split(".")[0]
        // formatted offset:
        + offset_sign
        + pad(Math.floor(Math.abs(offset_mins) / 60))
        + pad(Math.abs(offset_mins) % 60)
    return formatted_zoned_date_time
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Format time to relative:
// https://stackoverflow.com/a/6109105/441652

function format_time_to_relative(
    curr_time,
    prev_time,
) {
    const ms_per_second = 1000;
    const ms_per_minute = ms_per_second * 60;
    const ms_per_hour = ms_per_minute * 60;
    const ms_per_day = ms_per_hour * 24;

    const elapsed_time = curr_time - prev_time;

    if (elapsed_time < ms_per_minute) {
        return Math.round(elapsed_time / ms_per_second) + " seconds ago";
    } else if (elapsed_time < ms_per_hour) {
        return Math.round(elapsed_time / ms_per_minute) + " minutes ago";
    } else if (elapsed_time < ms_per_day) {
        return Math.round(elapsed_time / ms_per_hour) + " hours ago";
    } else {
        return Math.round(elapsed_time / ms_per_day) + " days ago";
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function display_server_start_time() {
    const server_start_time_elem = document.getElementById("server_start_time")
    server_start_time_elem.innerHTML = `<span class="info_label">started:</span> ${format_time_to_relative(new Date(), server_start_time)}`
    server_start_time_elem.setAttribute("title", `server start time: ${format_time_to_zoned(server_start_time)}`);
}

function display_project_git_commit_time() {
    const project_git_commit_time_elem = document.getElementById("project_git_commit_time");
    project_git_commit_time_elem.innerHTML = `<span class="info_label">updated:</span> ${format_time_to_relative(new Date(), project_git_commit_time)}`;
    project_git_commit_time_elem.setAttribute("title", `commit update time: ${format_time_to_zoned(project_git_commit_time)}`);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main

// Set `command_line` to the initial value:
command_line_input_elem.value = command_line

set_clipboard_state();
generate_client_uid();
display_server_start_time();
display_project_git_commit_time();
load_command_history();
on_command_line_change();
command_line_input_elem.focus();

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

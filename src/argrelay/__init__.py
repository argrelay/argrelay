"""
Terminology:

*   char position = cpos: char index within a string
*   index position = ipos: item index within a list
*   token: substring of command line (split by one or more delimiter chars), see usage of `SpecialChar`.
*   argument = arg: one or more command line token interpreted as a function argument, see usage of `TokenType`.
*   curr, prev, next: current, previous, next item during processing.
*   selected = sel: item selected as input for processing (e.g. token selected by cursor).
*   token left part: selected token substring on the left from the cursor.
*   token right part: selected token substring on the right from the cursor.
*   interpreter = interp: see usage of `AbstractInterp`.

*   type: unique (across all interpreters) name for a set of values.
*   key: unique (within current interpreter) alias name for a type.

"""

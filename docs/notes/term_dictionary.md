
TODO: reformat, sort, populate, link to `feature_story`-ies.

*   char position = cpos: char index within a string
*   index position = ipos: item index within a list
*   token: substring of command line (split by one or more delimiter chars), see usage of `SpecialChar`.
*   argument = arg: one or more command line token interpreted as a function argument, see usage of `TokenType`.
*   curr, prev, next: current, previous, next item during processing.
*   tangent = tan: token "touched" by the cursor.
*   token left part: tangent token substring on the left from the cursor.
*   token right part: tangent token substring on the right from the cursor.
*   interpreter = interp: see usage of `AbstractInterp`.

*   type: unique (across all interpreters) name for a set of values.
*   key: unique (within current interpreter) alias name for a type.

*   interrogate (user to specify arg value)
*   suggest (arg values to user (to interrogate the user))

*   arg type = describes arg value, see also: FS_53_81_66_18 # TnC
*   arg value = any string from a value set according to arg type.
*   envelope class = describes `data_envelope` schema, see also: FS_53_81_66_18 # TnC

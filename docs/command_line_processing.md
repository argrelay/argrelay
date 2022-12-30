
# CLI processor: general idea

The target use case is:
>   Quickly typed command line with no cryptic syntax to memorize:
>   *   just positional args
>   *   or, at most, named args

Another point:
>   Argument completion is mostly called for incomplete command line -
>   any complex grammar may be difficult to employ to validate
>   partial input.

Therefore, CLI processor is simplified:
*   no complex expressions,
*   no AST to build,
*   no special characters (almost),
*   no escape sequences,
*   etc.
Just list of strings (tokens).

# Bash context


Obviously, **before** giving a program its remaining command line (arguments) to process,
all complicated contexts it was started from are unwrapped by Bash itself:

```sh
relay_demo list dev upstream
```

```sh
relay_demo list dev upstream                                                       # some comment
```

```sh
                     relay_demo    list    dev    upstream                         # extra whitespaces
```

```sh
                     relay_demo    list    dev    upstream        | grep something # piped chain
```

```sh
echo -e "$(          relay_demo    list    dev    upstream     )" | grep something # sub-shell
```


```sh
echo -e "$( eval "   relay_demo    list    dev    upstream   " )" | grep something # string evaluation
```

Not so obviously, but logically, the same happens with calls from Bash for argument completion.
you will only need to process relevant data:
*   the remaining command line
*   relative cursor position

Note:
*   Do not confuse `InvocationMode` and `CompletionMode` - see `RunMode`.
*   In some complex contexts Bash stops calling for completion (e.g. try with sub-shell or even `eval`).

# Lexer

Produces:
*   list of tokens
*   left and right part of a token pointed by cursor position

Token is any contiguous string of non-whitespace characters.

# Parser

Produces:
*   list of key args
*   list of pos args

Key arg is a pair of tokens:
*   key token
*   val token

A pos arg is expressed by single val token.

# Interpreter

Produces:
*   List type-value pairs.

Note:
*   A key on the command line is not a type, it is a short name (alias) mapped into type.



This doc is supposed to explain idea behind simple multi-word search filter syntax used by `argrelay`.

<a name="argrelay-story"></a>

# Syntax: origin story

When an interface is limited...

You probably heard about research where<br/>
apes were taught to communicate with humans in sign language<br/>
(their vocal apparatus cannot reproduce speech effectively).

Naturally, with limited vocabulary,<br/>
they combined known words to describe unnamed things.

For example,<br/>
to ask for a watermelon (without knowing the exact sign),<br/>
they used combination of known "drink" + "sweet" signs to<br/>
to disambiguate their choice.

Similarly, the default `argrelay` CLI-interpretation logic<br/>
prompts for object properties to disambiguate search results until the single one is found.

<details>
<summary>continue story</summary>

### Narrow down options

Without any context, just two words "drink" + "sweet" leave<br/>
a lot of ambiguity to guess a watermelon (many drinks are sweet).

A more clarified "sentence" could be:
> drink striped red sweet fruit

Each word narrows down matching objects set<br/>
to fewer more specific candidates (including watermelon).

### Avoid strict order

Notice that the word order is not important -<br/>
this reordered line provides (almost) equivalent hints for guessing:
> striped sweet fruit red drink

It is not a valid English grammar, but it somewhat works.

### Use "enum language"

Think of speaking "enum language":
*   Each word is an enum value of some enum type:
    *   Color: red, green, ...
    *   Taste: sweet, salty, ...
    *   Temperature: hot, cold, ...
    *   Action: drink, play, ...
*   Word order is irrelevant because _enum value spaces do not overlap_ (almost).
*   To clarify the object, list more enum values relevant to the object.

Now, imagine the enum types and values are not supposed to be memorized,<br/>
they are proposed to select from (based on the current context of all known objects).

### Match values to enums

*   For humans, it is natural to guess the object by list of characteristics.
*   For machines, it has to be a matching algo which "guess" precisely simulating natural process.

At its core, this algo looks through value sets of each enum and<br/>
matches given values setting and eliminating characteristics one by one.

### Address any object

Suppose enums are binary = having only two values<br/>
(cardinality = 2: black/white, hot/cold, true/false, ...).

In this case, 5 words could slice the object space to<br/>
single out (identify exactly) up to 2^5 = 32 objects.

To "address" larger object spaces,<br/>
larger enum cardinalities or more word places are required.

*   Each enum type ~ a dimension.
*   Each specific enum value ~ a coordinate.
*   Each object fills a slot in such multi-dimensional discrete space.

### Apply to CLI

CLI-s are used to write commands - imperative sentences:<br/>
specific actions on specific objects.

The "enum language" above covers searching both<br/>
an action and any object it requires.

### Suggest contextually

Not every combination of enum values may point to an existing object.

For data with sparse object spaces,<br/>
the CLI-suggestion is affected by possible coordinates applicable only to<br/>
remaining (narrowed down) object sets.

### Differentiate on purpose

All above may be an obvious approach to come up with,<br/>
but it is not ordinary for CLI-s of most common commands<br/>
(due to lack of data and non-trivial logic to implement the "enum language"):

| Common commands (think `ls`, `git`, `ssh`, ...):                            | `argrelay`-wrapped actions:                           |
|:----------------------------------------------------------------------------|:------------------------------------------------------|
| have succinct syntax and prefer<br/> single-char switches (defined by code) | prefer explicit "enum language"<br/> defined by data  |
| rely on humans to memorize syntax<br/> (options, ordering, etc.)            | assume humans have<br/> a loose idea about the syntax |
| auto-complete only for objects<br/> known to the OS (hosts, files, etc.)    | auto-complete from<br/> a domain-specific data        |

<!--
    TODO: Write a tech doc about "How does the search work?" and link it here.
-->

</details>

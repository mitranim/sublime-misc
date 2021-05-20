## Overview

Collection of tiny Sublime Text utilities, fashioned as a single plugin. Mostly undocumented, published as a backup and for easy code sharing.

## Installation

Clone the repo and symlink it to your Sublime packages directory. Example for MacOS:

```sh
git clone https://github.com/mitranim/sublime-misc.git
cd sublime-misc
ln -sf "$(pwd)" "$HOME/Library/Application Support/Sublime Text/Packages/"
```

To find the packages directory on your system, use Sublime Text menu → Preferences → Browse Packages.

## Keymaps

To enable the comment continuation feature, add the following to your keymap:

```json
{
  "keys": ["enter"],
  "command": "run_macro_file",
  "args": {"file": "res://Packages/sublime-misc/continue_line_comment.sublime-macro"},
  "context": [{"key": "selector", "operand": "comment.line - punctuation.definition.comment"}],
},
```

## License

https://unlicense.org

Small pieces of code were ported from ST internals (C++). Samples were courteously provided by ST creator. Different conditions might apply.

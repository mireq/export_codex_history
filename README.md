# export_codex_history

Turn a Codex `.jsonl` history export into a clean standalone HTML transcript.

![Screenshot](https://github.com/user-attachments/assets/eb54cdfd-dd4d-4dba-909d-6a47927d0156)

## What it does

- Reads a Codex history `.jsonl` file
- Builds a polished single-file HTML transcript
- Preserves messages, tool calls, timestamps, and session metadata
- Auto-detects the input file if there is exactly one `.jsonl` file in the current directory

## Requirements

- Python 3.11+
- `jinja2`
- `markdown-it-py`

## Install

```bash
pip install jinja2 markdown-it-py
```

## Usage

Export a specific file:

```bash
python3 export_codex_history.py session.jsonl
```

Let the script auto-detect the only `.jsonl` file in the current directory:

```bash
python3 export_codex_history.py
```

Write to a custom output file and set a title:

```bash
python3 export_codex_history.py session.jsonl -o transcript.html --title "Codex Session"
```

By default, the output file is written next to the input file with the same name and an `.html` extension.

## License

MIT

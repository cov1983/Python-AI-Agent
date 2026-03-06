# AI Agent (Python)

A small command-line coding agent powered by the Gemini API.

The agent accepts a user prompt, lets the model decide when to call tools, executes those tool calls in a sandboxed working directory, and feeds results back to the model until a final answer is produced.

## What This Project Does

- Runs a prompt-driven agent loop with `google-genai`.
- Exposes a safe toolset to the model: `get_files_info`, `get_file_content`, `run_python_file`, `write_file`.
- Restricts file operations to a configured working directory (`./calculator` by default).
- Includes a small calculator app used as the sandboxed file workspace.

## Tech Stack

- Python `>=3.13`
- `google-genai==1.12.1`
- `python-dotenv==1.1.0`

## Project Layout

```text
.
|- main.py                 # Original single-function implementation
|- main-cleaned.py         # Refactored implementation with smaller functions
|- call_function.py        # Tool registry + function dispatcher
|- prompts.py              # System prompt for the coding agent
|- config.py               # Model/config values and working directory
|- functions/
|  |- get_files_info.py
|  |- get_file_content.py
|  |- run_python_file.py
|  |- write_file.py
|- calculator/             # Sandboxed workspace used by tool calls
|- list-models.py          # Utility: list supported Gemini models
|- test_*.py               # Script-style tests for each tool
```

## Configuration

Main runtime configuration is in `config.py`:

- `GEMINI_MODEL = "gemini-2.5-flash-lite"`
- `MAX_ITERATIONS = 20`
- `WORKING_DIR = "./calculator"`
- `MAX_CHARS = 10000` (for `get_file_content`)

Environment variable required:

- `GEMINI_API_KEY`

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Add your Gemini API key to `.env`.

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install google-genai==1.12.1 python-dotenv==1.1.0
```

Create `.env` in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Running The Agent

Use either entrypoint:

- `main.py` (original implementation)
- `main-cleaned.py` (refactored, same behavior)

Run:

```bash
python main-cleaned.py "Summarize the files in this project"
```

Verbose mode:

```bash
python main-cleaned.py "Create a README for calculator" --verbose
```

What happens at runtime:

1. Loads `GEMINI_API_KEY`.
2. Sends your prompt + system instruction to Gemini.
3. Executes model-requested tool calls in `WORKING_DIR`.
4. Returns tool outputs to the model.
5. Repeats until no more function calls or `MAX_ITERATIONS` is reached.

## Tool Behavior Notes

- All tool paths are validated to stay inside `WORKING_DIR`.
- Attempts to escape the sandbox return explicit error strings.
- `get_file_content` truncates output after `MAX_CHARS`.
- `run_python_file` only runs `.py` files and uses a 30s timeout.
- `write_file` creates missing directories and overwrites existing files.

## Utility Scripts

List available models:

```bash
python list-models.py
```

Run tool tests (script-style):

```bash
python test_get_files_info.py
python test_get_file_content.py
python test_run_python_file.py
python test_write_file.py
```

Run calculator unit tests:

```bash
python calculator/tests.py
```

## Known Limitations

- Tools currently return plain text strings rather than structured JSON objects.
- The agent loop exits after a fixed `MAX_ITERATIONS` guard.
- Sandbox scope is tied to a single configured `WORKING_DIR`.

## License

No license file is currently included in this repository.

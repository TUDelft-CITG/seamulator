# SEAMULATOR

Macro-scale maritime traffic simulator with interactive visualization using Dash and Plotly.

## Installation

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/seamulator.git
   cd seamulator
   ```

2. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

4. **Run pre-commit on existing files:**
   ```bash
   uv run pre-commit run --all-files
   ```

## Development

### Pre-commit

This project uses [pre-commit](https://pre-commit.com/) with [ruff](https://github.com/astral-sh/ruff) for linting and formatting. Every `git commit` will automatically:
- Run `ruff check` — fails if linting issues are found
- Run `ruff format` — auto-formats code

**Note:** If `ruff check` finds issues that cannot be auto-fixed, the commit will fail. Fix the issues manually and try again.

To bypass pre-commit (not recommended):
```bash
git commit --no-verify -m "message"
```

### Running the application

```bash
uv run python -m seamulator.visualization.app
```

### Running tests

```bash
uv run pytest tests/ -v
```

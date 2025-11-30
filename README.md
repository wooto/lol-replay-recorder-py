# LoL Replay Recorder

A Python library for recording League of Legends replays programmatically.

[![PyPI version](https://badge.fury.io/py/lol-replay-recorder.svg)](https://badge.fury.io/py/lol-replay-recorder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **League Client API Integration**: Authenticate with the League Client (LCU API)
- **Replay Control**: Programmatic control of replay playback and recording
- **Window Automation**: Automated camera control and UI interaction during replays

## Requirements

- Python >= 3.10
- League of Legends client installed
- Supported OS: Windows, macOS, Linux

## Installation

```bash
pip install lol-replay-recorder
```

## Quick Start

```python
import asyncio
from lol_replay_recorder import LeagueReplayClient

async def record_replay():
    # Initialize replay client
    client = LeagueReplayClient()
    await client.init()
    await client.load()

    # Control replay playback
    await client.play()
    await asyncio.sleep(5)
    await client.pause()

    # Clean up
    await client.exit()

# Run the async function
asyncio.run(record_replay())
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run only unit tests
uv run pytest -m unit

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check src/
```

## License

MIT

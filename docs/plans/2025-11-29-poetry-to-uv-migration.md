# Poetry to uv Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate project from Poetry to uv for full Python tooling (dependencies, venv, Python version management, CI)

**Architecture:** Clean-slate migration removing all Poetry artifacts, using hatchling as build backend, uv for dependency management and Python version control

**Tech Stack:** uv, hatchling, GitHub Actions (astral-sh/setup-uv@v3)

---

### Task 1: Verify uv Installation

**Files:**
- None (verification only)

**Step 1: Check if uv is installed**

Run: `which uv`
Expected: Either path to uv binary or empty (not found)

**Step 2: Install uv if not present**

If not installed, run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Expected: Installation success message, uv added to PATH

**Step 3: Verify uv version**

Run: `uv --version`
Expected: Output showing uv version (e.g., "uv 0.5.x")

---

### Task 2: Create Python Version File

**Files:**
- Create: `.python-version`

**Step 1: Create .python-version file**

Create file at project root with content:
```
3.10
```

**Step 2: Verify file exists**

Run: `cat .python-version`
Expected: Output shows "3.10"

**Step 3: Commit**

```bash
git add .python-version
git commit -m "build: add .python-version for uv Python management"
```

---

### Task 3: Update pyproject.toml Build System

**Files:**
- Modify: `pyproject.toml:28-32`

**Step 1: Replace build-system section**

Replace lines 28-32 in `pyproject.toml`:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Remove the entire `[tool.poetry]` section (lines 31-32).

**Step 2: Verify syntax**

Run: `cat pyproject.toml | grep -A 2 "\[build-system\]"`
Expected: Shows the new hatchling configuration

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "build: replace poetry-core with hatchling"
```

---

### Task 4: Move Dev Dependencies to tool.uv

**Files:**
- Modify: `pyproject.toml:18-26`

**Step 1: Remove [project.optional-dependencies] section**

Delete lines 18-26 from `pyproject.toml`.

**Step 2: Add [tool.uv] section at end of file**

Add to end of `pyproject.toml`:
```toml
[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]
```

**Step 3: Verify changes**

Run: `cat pyproject.toml | grep -A 7 "\[tool.uv\]"`
Expected: Shows the dev-dependencies list

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "build: move dev dependencies to [tool.uv]"
```

---

### Task 5: Remove Poetry Virtual Environment

**Files:**
- Delete: `.venv/` directory

**Step 1: Remove .venv directory**

Run: `rm -rf .venv`
Expected: Directory removed

**Step 2: Verify removal**

Run: `ls -la | grep .venv`
Expected: No output (directory gone)

**Step 3: Check for poetry.lock**

Run: `ls -la | grep poetry.lock`
Expected: No output (file doesn't exist)

Note: No commit needed - .venv is gitignored

---

### Task 6: Initialize uv and Generate Lockfile

**Files:**
- Create: `uv.lock` (generated)
- Create: `.venv/` (generated)

**Step 1: Run uv sync**

Run: `uv sync`
Expected:
- Downloads Python 3.10 if needed
- Creates .venv directory
- Installs all dependencies
- Generates uv.lock file
- Success message

**Step 2: Verify .venv created**

Run: `ls -la .venv`
Expected: Shows virtual environment structure

**Step 3: Verify uv.lock created**

Run: `ls -la uv.lock`
Expected: Shows uv.lock file

**Step 4: Commit uv.lock**

```bash
git add uv.lock
git commit -m "build: add uv.lock for dependency locking"
```

---

### Task 7: Update CI Workflow

**Files:**
- Modify: `.github/workflows/ci.yml:19-27`

**Step 1: Replace Python setup step**

Replace lines 19-22 with:
```yaml
    - name: Set up uv
      uses: astral-sh/setup-uv@v3
```

**Step 2: Replace install dependencies step**

Replace lines 24-27 with:
```yaml
    - name: Install dependencies
      run: uv sync
```

**Step 3: Update test command**

Replace line 30 with:
```yaml
      run: uv run pytest
```

**Step 4: Update type checking command**

Replace line 33 with:
```yaml
      run: uv run mypy src/
```

**Step 5: Update linting command**

Replace line 36 with:
```yaml
      run: uv run ruff check src/
```

**Step 6: Verify complete workflow**

Run: `cat .github/workflows/ci.yml`
Expected: Shows updated workflow with uv commands

**Step 7: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: migrate from pip to uv for dependency installation"
```

---

### Task 8: Update CLAUDE.md Development Commands

**Files:**
- Modify: `CLAUDE.md:18-36`

**Step 1: Replace Development Commands section**

Replace the entire "Development Commands" section (after `## Development Commands` heading) with:

```markdown
## Development Commands

\`\`\`bash
# Install dependencies (creates .venv automatically)
uv sync

# Run all tests
uv run pytest

# Run only unit tests
uv run pytest -m unit

# Run only e2e tests (requires League client)
uv run pytest -m e2e

# Run a single test file
uv run pytest tests/unit/test_utils.py

# Run a specific test
uv run pytest tests/unit/test_utils.py::test_sleep_waits_correct_milliseconds

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv lock --upgrade

# Install specific Python version
uv python install 3.10
\`\`\`
```

**Step 2: Verify changes**

Run: `grep -A 5 "# Install dependencies" CLAUDE.md`
Expected: Shows "uv sync" instead of "poetry install"

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update development commands for uv"
```

---

### Task 9: Verify Migration with Tests

**Files:**
- None (verification only)

**Step 1: Run unit tests**

Run: `uv run pytest -m unit -v`
Expected: All unit tests pass

**Step 2: Run type checking**

Run: `uv run mypy src/`
Expected: No type errors

**Step 3: Run linting**

Run: `uv run ruff check src/`
Expected: No linting errors

**Step 4: Verify imports work**

Run: `uv run python -c "from lol_replay_recorder.controllers import LeagueReplayClient; print('Import successful')"`
Expected: Output shows "Import successful"

---

### Task 10: Update .gitignore (if needed)

**Files:**
- Modify: `.gitignore` (conditionally)

**Step 1: Check if .venv is ignored**

Run: `grep "\.venv" .gitignore`
Expected: Shows .venv in gitignore (should already exist)

**Step 2: Check if uv.lock is NOT ignored**

Run: `grep "uv\.lock" .gitignore`
Expected: No output (uv.lock should be committed, not ignored)

**Step 3: Add uv.lock if it's ignored**

If step 2 shows uv.lock in .gitignore, remove that line.
No commit needed if no changes.

**Step 4: Commit if modified**

If .gitignore was changed:
```bash
git add .gitignore
git commit -m "build: ensure uv.lock is tracked in git"
```

---

### Task 11: Final Verification and Cleanup

**Files:**
- None (verification only)

**Step 1: Check git status**

Run: `git status`
Expected: Working tree clean (all changes committed)

**Step 2: Verify uv.lock is tracked**

Run: `git ls-files | grep uv.lock`
Expected: Shows "uv.lock"

**Step 3: List commits**

Run: `git log --oneline -10`
Expected: Shows all migration commits

**Step 4: Verify CI workflow syntax**

Run: `cat .github/workflows/ci.yml | grep -E "(uses: astral-sh/setup-uv|uv sync|uv run)"`
Expected: Shows uv commands in CI

---

## Post-Migration Notes

**What Changed:**
- Build backend: poetry-core → hatchling
- Dependency manager: Poetry → uv
- Lockfile: poetry.lock → uv.lock
- Python version management: .python-version file
- CI: pip installation → uv sync
- Dev commands: poetry run → uv run

**What Stayed the Same:**
- Package name: lol-replay-recorder
- Import paths: `from lol_replay_recorder import ...`
- Project structure and source code
- All test configurations
- Type checking and linting settings

**Benefits:**
- 10-100x faster dependency resolution and installation
- Unified tooling for Python versions, venvs, and dependencies
- Simpler CI setup with built-in caching
- Cross-platform lockfile

**Potential Issues:**
- First `uv sync` downloads Python 3.10 (one-time cost)
- Platform-specific dependencies (pywin32) should work automatically
- First CI run will be slower (subsequent runs cached)

# Repository Guidelines

## Project Structure & Module Organization
Mininet’s core Python package is in `mininet/`:
- `net.py`, `node.py`, `link.py`, `topo.py`, `topolib.py` implement network orchestration, node/link models, and built-in topologies.
- `cli.py` provides the interactive `mininet>` shell.
- `clean.py` handles cleanup of stale namespaces, links, and processes.

Entry points and support code:
- `bin/mn`: main CLI launcher.
- `examples/`: runnable API examples; `examples/test/` contains example-level tests.
- `mininet/test/`: core test suite.
- `custom/`: local custom topology scripts.
- `util/`: install and maintenance scripts.
- `doc/`: documentation and contributor notes.

## Build, Test, and Development Commands
- `PYTHONPATH=. python3 bin/mn -h`: show CLI options from source tree.
- `sudo PYTHONPATH=. python3 bin/mn --test pingall`: quick runtime sanity test.
- `make mnexec`: build `mnexec` helper binary.
- `make test`: run core Python tests (`mininet/test/test_nets.py`, `test_hifi.py`).
- `make slowtest`: run walkthrough and example tests.
- `make codecheck`: run `pyflakes`, `pylint`, and `pep8` checks.
- `sudo PYTHONPATH=. python3 bin/mn -c`: cleanup before/after experiments.

## Coding Style & Naming Conventions
- Python style is PEP8-oriented, validated via `make codecheck`.
- Keep 4-space indentation; avoid unnecessary comments.
- Follow existing class/function naming patterns:
  - Classes: `CamelCase` (e.g., `OVSSwitch`)
  - Functions/variables: `snake_case`
- New example/test files should match existing naming conventions (e.g., `test_*.py`).

## Testing Guidelines
- Prefer targeted tests while iterating, then run `make test`.
- For topology or CLI changes, include at least one reproducible `mn` command in your PR description.
- Add/extend tests under `mininet/test/` for core behavior changes and `examples/test/` for example scripts.

## Commit & Pull Request Guidelines
- Use concise, imperative commit subjects (e.g., `Fix typo in node.py`), consistent with repository history.
- Keep commits focused; avoid mixing refactors with behavior changes.
- PRs should include:
  - What changed and why
  - How it was tested (exact commands)
  - Any environment assumptions (kernel, OVS/bridge tools, Python version)
  - Linked issue/PR number when applicable

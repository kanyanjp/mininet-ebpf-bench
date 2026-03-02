# Torus Testing Playbook

## Goal

Benchmark Mininet custom **host-only torus** build performance with consistent commands and metrics.

## Files

- Topology: `custom/hostmesh_torus.py`
- Benchmark: `custom/bench_hostmesh_fast_cleanup.py`

## Pre-run

```bash
sudo PYTHONPATH=. python3 bin/mn -c
```

## Benchmark Command

```bash
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x <X> --y <Y>
```

Examples:

```bash
# 500
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x 20 --y 25
# 1000
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x 25 --y 40
# 2000
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x 40 --y 50
# 4000
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x 80 --y 50
```

## Metric Policy

- Primary metric: `build_s`
- Ignore for scaling conclusion: `cleanup_s`, `total_s`

Reason: cleanup strategy can vary (`fast_hosts_only` vs `full_stop`) and skews non-build comparisons.

## Output Artifacts

- Runtime logs: `.codex-logs/`
- Optional profiling/flamegraph outputs: `.codex-logs/*.txt`, `.codex-logs/*.svg`

## eBPF

For kernel hotspot and flamegraph workflow, see:

- `doc/EBPF_SAMPLING_MININET.md`

## Issue Record: Slow End-to-End Runtime For Switch-Only Torus

Problem observed during switch-only built-in torus testing (`n=0`):

- `build_s` was much lower than wall-clock `real` time.
- Example (`x=25,y=40,n=0`): `build_s=61.672s` vs `real=415.06s`.

Root cause:

- `build_s` measures only `net.build()`.
- Wall-clock included global `cleanup()` before/after run.
- `cleanup()` scans and deletes stale links/processes system-wide, which dominates runtime at large scale.

Mitigation implemented:

- Added `custom/bench_builtin_torus_fast_cleanup.py`.
- Added `--shared-netns <name>` mode:
  - create dedicated netns
  - run benchmark entirely inside that netns
  - skip global `cleanup()` in inner run
  - kill pids in that netns and delete netns after run

Result (same scale, switch-only `x=25,y=40,n=0`):

- Shared-netns mode: `build_s=19.213s`, `real=24.97s`.

Command:

```bash
sudo PYTHONPATH=. python3 custom/bench_builtin_torus_fast_cleanup.py \
  --x 25 --y 40 --n 0 --shared-netns mnbench-1k
```

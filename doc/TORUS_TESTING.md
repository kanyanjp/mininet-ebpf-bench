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

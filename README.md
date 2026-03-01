# Torus Topology Benchmark Guide

This repository is currently focused on **torus topology performance testing** in Mininet, especially host-only custom torus workloads and eBPF kernel profiling.

## Scope

- Custom host-only torus topology (no switches): `custom/hostmesh_torus.py`
- Fast build benchmark script: `custom/bench_hostmesh_fast_cleanup.py`
- eBPF sampling guide: `doc/EBPF_SAMPLING_MININET.md`

## Environment

- Linux kernel with netns/veth support
- `sudo` privilege
- `python3`, `bpftrace`
- Optional visualization toolchain:
  - `git clone https://github.com/brendangregg/FlameGraph.git .tools/FlameGraph`

## Quick Start

Clean residual state:

```bash
sudo PYTHONPATH=. python3 bin/mn -c
```

Run build benchmark (fast cleanup mode):

```bash
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x 20 --y 25
```

Interpretation:
- `build_s`: topology build time (main metric)
- `cleanup_s`: teardown time
- `total_s`: build + selected cleanup path

## Standard Sizes

- 500 nodes: `--x 20 --y 25`
- 1000 nodes: `--x 25 --y 40`
- 2000 nodes: `--x 40 --y 50`
- 4000 nodes: `--x 80 --y 50`

## eBPF Sampling

Recommended: process-family filtered sampling (Mininet root process + children) during benchmark.

Reference commands and workflow are documented in:

- `doc/EBPF_SAMPLING_MININET.md`

Generated artifacts are written under:

- `.codex-logs/`

## Notes

- For torus build performance comparison, use **only `build_s`**.
- `mn --test build` includes start/stop and is not equivalent to build-only benchmarking.
- Keep temporary profiling artifacts (`.codex-logs/`, `.tools/`) out of commits unless explicitly needed.

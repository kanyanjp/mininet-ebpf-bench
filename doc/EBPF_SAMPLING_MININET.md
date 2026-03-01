# Mininet eBPF 采样记录

本文档记录在本仓库中对自定义 host-only torus 拓扑进行 eBPF 采样与火焰图生成的方法。

## 1. 前置条件

- 需要 root 权限（`sudo`）。
- 需要 `bpftrace`：
  - 检查：`which bpftrace`
- FlameGraph 工具链（本仓库已放在 `.tools/FlameGraph`）：
  - `flamegraph.pl`
  - `stackcollapse-bpftrace.pl`

## 2. 测试负载

使用脚本：

- `custom/bench_hostmesh_fast_cleanup.py`
- `custom/hostmesh_torus.py`

示例（1000 节点）：

```bash
sudo PYTHONPATH=. python3 custom/bench_hostmesh_fast_cleanup.py --x 25 --y 40
```

## 3. 仅采样 rtnl_newlink（kprobe）

```bash
sudo bpftrace -q -e 'kprobe:rtnl_newlink { @[kstack] = count(); }'
```

建议流程：先后台启动 bpftrace，再运行 benchmark，结束后向 bpftrace 发 `SIGINT` 输出聚合结果。

本仓库相关输出示例：

- `.codex-logs/bpf_rtnl_newlink_500.txt`
- `.codex-logs/rtnl_newlink_500_flame.svg`

## 4. 全内核 profile 采样（不筛选 PID）

```bash
sudo bpftrace -q -e 'profile:hz:199 { @[kstack] = count(); }'
```

说明：

- 这是全系统采样，容易出现大量 `idle` 栈。
- 用于全局视角，不适合直接判断 Mininet 进程热点占比。

本仓库相关输出示例：

- `.codex-logs/kstack_profile_500.txt`
- `.codex-logs/kstack_profile_500_fgtool.svg`

## 5. 仅采样 Mininet 进程族（推荐）

下面脚本思想：

1. 先定位 benchmark 主 PID。
2. 用 `sched_process_fork` 动态追踪子进程，把整个进程族放入 `@tracked`。
3. `profile:hz:199 /@tracked[pid]/` 仅采样该进程族内核栈。

核心 bpftrace 程序：

```bpftrace
BEGIN { @tracked[ROOTPID] = 1; }
tracepoint:sched:sched_process_fork /@tracked[args->parent_pid]/ { @tracked[args->child_pid] = 1; }
tracepoint:sched:sched_process_exit /@tracked[pid]/ { delete(@tracked[pid]); }
profile:hz:199 /@tracked[pid]/ { @[kstack] = count(); }
```

本仓库相关输出示例：

- `.codex-logs/kstack_profile_1000_family.txt`
- `.codex-logs/kstack_profile_1000_family.collapsed`
- `.codex-logs/kstack_profile_1000_family_flame.svg`
- `.codex-logs/kstack_profile_1000_family.meta`

## 6. FlameGraph 生成

先准备工具链（仅首次）：

```bash
git clone https://github.com/brendangregg/FlameGraph.git .tools/FlameGraph
```

从 bpftrace 输出生成火焰图：

```bash
.tools/FlameGraph/stackcollapse-bpftrace.pl INPUT.txt > OUTPUT.collapsed
.tools/FlameGraph/flamegraph.pl --title 'TITLE' OUTPUT.collapsed > OUTPUT.svg
```

## 7. 常见问题

- `Cannot find bpftrace`: 先安装 `bpftrace`。
- 火焰图几乎全是 `idle`: 说明采样范围是全系统，改用“Mininet 进程族采样”。
- 样本数过低：提高负载规模、延长运行时间、或提高 `hz`（注意开销）。

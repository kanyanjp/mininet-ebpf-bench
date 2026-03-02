#!/usr/bin/env python3
"""Benchmark built-in TorusTopo build time with optional fast cleanup."""

import argparse
import os
import subprocess
import sys
import time

from mininet.clean import cleanup
from mininet.net import Mininet
from mininet.nodelib import LinuxBridge
from mininet.topolib import TorusTopo


def fast_stop_torus(net):
    """Fast cleanup path for TorusTopo with LinuxBridge switches."""
    for host in net.hosts:
        host.terminate()

    for switch in net.switches:
        # LinuxBridge.start() is not called in this benchmark path.
        # Try to remove bridge device quickly if it exists.
        switch.cmd('ifconfig', switch, 'down')
        switch.cmd('brctl', 'delbr', switch)
        switch.terminate()


def run_in_shared_netns(args):
    """Run benchmark inside a dedicated netns and remove it afterward."""
    ns = args.shared_netns
    script = os.path.abspath(__file__)
    repo = os.path.dirname(os.path.dirname(script))
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", ".")
    env["PATH"] = repo + ":" + env.get("PATH", "")

    subprocess.run(
        ["ip", "netns", "delete", ns],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(["ip", "netns", "add", ns], check=True)

    inner = [
        "ip",
        "netns",
        "exec",
        ns,
        sys.executable,
        script,
        "--x",
        str(args.x),
        "--y",
        str(args.y),
        "--n",
        str(args.n),
        "--skip-pre-cleanup",
        "--skip-post-cleanup",
        "--_inner-shared-netns",
    ]
    if args.full_stop:
        inner.append("--full-stop")

    try:
        result = subprocess.run(inner, env=env)
    finally:
        pids = subprocess.run(
            ["ip", "netns", "pids", ns],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        ).stdout.split()
        for pid in pids:
            subprocess.run(
                ["kill", "-9", pid],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        subprocess.run(
            ["ip", "netns", "delete", ns],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        exists = subprocess.run(
            ["ip", "netns", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        ).stdout
        if ns in exists.split():
            raise SystemExit(f"failed to delete netns '{ns}'")

    raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Build built-in TorusTopo and use fast cleanup."
    )
    parser.add_argument("--x", type=int, default=25, help="torus x dimension")
    parser.add_argument("--y", type=int, default=40, help="torus y dimension")
    parser.add_argument(
        "--n", type=int, default=1, help="number of hosts per switch"
    )
    parser.add_argument(
        "--skip-pre-cleanup",
        action="store_true",
        help="skip cleanup() before benchmark",
    )
    parser.add_argument(
        "--full-stop",
        action="store_true",
        help="use net.stop() instead of fast host/switch cleanup",
    )
    parser.add_argument(
        "--skip-post-cleanup",
        action="store_true",
        help="skip cleanup() after benchmark",
    )
    parser.add_argument(
        "--shared-netns",
        default="",
        help="run benchmark in this dedicated netns and delete it after run",
    )
    parser.add_argument(
        "--_inner-shared-netns",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    if args.x < 3 or args.y < 3:
        raise SystemExit("x and y must both be >= 3 for built-in TorusTopo")
    if args.n < 0:
        raise SystemExit("n must be >= 0")

    if args.shared_netns and not args._inner_shared_netns:
        run_in_shared_netns(args)

    if not args.skip_pre_cleanup:
        cleanup()

    topo = TorusTopo(x=args.x, y=args.y, n=args.n)
    net = Mininet(
        topo=topo,
        controller=None,
        switch=LinuxBridge,
        build=False
    )

    t0 = time.time()
    net.build()
    t1 = time.time()

    if args.full_stop:
        t2 = time.time()
        net.stop()
        t3 = time.time()
        cleanup_mode = "full_stop"
    else:
        t2 = time.time()
        fast_stop_torus(net)
        t3 = time.time()
        cleanup_mode = "fast_torus"

    if not args.skip_post_cleanup:
        cleanup()

    hosts = args.x * args.y * args.n
    switches = args.x * args.y
    links = args.x * args.y * (args.n + 2)
    print(
        f"hosts={hosts} switches={switches} links={links} mode={cleanup_mode} "
        f"build_s={t1 - t0:.3f} cleanup_s={t3 - t2:.3f} total_s={t3 - t0:.3f}"
    )


if __name__ == "__main__":
    main()

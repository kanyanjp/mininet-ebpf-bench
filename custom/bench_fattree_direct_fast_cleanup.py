#!/usr/bin/env python3
"""Benchmark direct-mode fat-tree build time with fast cleanup."""

import argparse
import os
import subprocess
import sys
import time

from mininet.clean import cleanup
from mininet.cmdprofile import reset as profile_reset
from mininet.cmdprofile import set_enabled as profile_set_enabled
from mininet.cmdprofile import snapshot as profile_snapshot
from mininet.net import Mininet

from custom.fattree_direct import FatTreeDirectTopo


def fast_stop_hosts_only(net):
    """Fast cleanup path: terminate host namespaces/processes only."""
    for host in net.hosts:
        host.terminate()


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
        "--k",
        str(args.k),
        "--skip-pre-cleanup",
        "--skip-post-cleanup",
        "--_inner-shared-netns",
    ]
    if args.full_stop:
        inner.append("--full-stop")
    if args.disable_cmd_profile:
        inner.append("--disable-cmd-profile")

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
        description="Build direct-mode fat-tree and use fast cleanup."
    )
    parser.add_argument(
        "--k",
        type=int,
        default=8,
        help="fat-tree k (even and >= 4)",
    )
    parser.add_argument(
        "--skip-pre-cleanup",
        action="store_true",
        help="skip cleanup() before benchmark",
    )
    parser.add_argument(
        "--full-stop",
        action="store_true",
        help="use net.stop() instead of fast host-only cleanup",
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
        "--disable-cmd-profile",
        action="store_true",
        help="disable Mininet command timing profile during build",
    )
    parser.add_argument(
        "--_inner-shared-netns",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    if args.k < 4 or (args.k % 2) != 0:
        raise SystemExit("k must be even and >= 4")

    if args.shared_netns and not args._inner_shared_netns:
        run_in_shared_netns(args)

    if not args.skip_pre_cleanup:
        cleanup()

    half = args.k // 2
    hosts = (5 * args.k * args.k) // 4 + (args.k * args.k * args.k) // 4
    links = (3 * args.k * args.k * args.k) // 4
    topo = FatTreeDirectTopo(k=args.k)
    net = Mininet(topo=topo, controller=None, build=False)

    profile_enabled = not args.disable_cmd_profile
    profile_set_enabled(profile_enabled)
    if profile_enabled:
        profile_reset()

    t0 = time.time()
    net.build()
    t1 = time.time()
    prof = profile_snapshot() if profile_enabled else None

    if args.full_stop:
        t2 = time.time()
        net.stop()
        t3 = time.time()
        cleanup_mode = "full_stop"
    else:
        t2 = time.time()
        fast_stop_hosts_only(net)
        t3 = time.time()
        cleanup_mode = "fast_hosts_only"

    if not args.skip_post_cleanup:
        cleanup()

    total_ms = int(round((t1 - t0) * 1000.0))
    extra_metrics = ""
    if profile_enabled:
        netlink_ack_ms = int(round(prof["ip_link_s"] * 1000.0))
        ack_pct = (100.0 * netlink_ack_ms / total_ms) if total_ms > 0 else 0.0
        node_ms = max(0, total_ms - netlink_ack_ms)
        extra_metrics = (
            f" total_ms={total_ms} netlink_ack_ms={netlink_ack_ms} "
            f"ack_pct={ack_pct:.2f}% node_ms={node_ms}"
        )
    else:
        extra_metrics = f" total_ms={total_ms}"

    print(
        f"k={args.k} hosts={hosts} links={links} "
        f"pod_count={args.k} nodes_per_pod={args.k * half} "
        f"mode={cleanup_mode} "
        f"build_s={t1 - t0:.3f} cleanup_s={t3 - t2:.3f} total_s={t3 - t0:.3f}"
        f"{extra_metrics}"
    )


if __name__ == "__main__":
    main()

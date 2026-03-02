#!/usr/bin/env python3
"""Benchmark Linux-bridge torus build time with fast cleanup."""

import argparse
import time

from mininet.clean import cleanup
from mininet.net import Mininet

from custom.hostmesh_torus_lxbr import HostMeshTorusLinuxBridgeTopo


def fast_stop_hosts_only(net):
    """Fast cleanup path: terminate host namespaces/processes only."""
    for host in net.hosts:
        host.terminate()


def main():
    parser = argparse.ArgumentParser(
        description="Build Linux-bridge torus and use fast cleanup."
    )
    parser.add_argument("--x", type=int, default=20, help="torus x dimension")
    parser.add_argument("--y", type=int, default=25, help="torus y dimension")
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
    args = parser.parse_args()

    if args.x < 2 or args.y < 2:
        raise SystemExit("x and y must both be >= 2")

    if not args.skip_pre_cleanup:
        cleanup()

    topo = HostMeshTorusLinuxBridgeTopo(x=args.x, y=args.y)
    net = Mininet(topo=topo, controller=None, build=False)

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
        fast_stop_hosts_only(net)
        t3 = time.time()
        cleanup_mode = "fast_hosts_only"

    if not args.skip_post_cleanup:
        cleanup()

    hosts = args.x * args.y
    bridges = 2 * hosts
    links = 4 * hosts
    print(
        f"hosts={hosts} bridges={bridges} links={links} mode={cleanup_mode} "
        f"build_s={t1 - t0:.3f} cleanup_s={t3 - t2:.3f} total_s={t3 - t0:.3f}"
    )


if __name__ == "__main__":
    main()

"""Parameterized direct-mode fat-tree topology (host-to-host links only)."""

from mininet.topo import Topo


class FatTreeDirectTopo(Topo):
    """k-ary fat-tree where all nodes are modeled as hosts."""

    def build(self, k=8):
        k = int(k)
        if k < 4 or (k % 2) != 0:
            raise Exception("k must be even and >= 4")

        half = k // 2
        cores = {}
        aggs = {}
        edges = {}
        hosts = {}

        # Core layer: half groups, half nodes per group.
        for group in range(half):
            for idx in range(half):
                name = f"c{group + 1}x{idx + 1}"
                cores[(group, idx)] = self.addHost(name)

        # Pod-local aggregation and edge layers.
        for pod in range(k):
            for idx in range(half):
                aggs[(pod, idx)] = self.addHost(f"p{pod + 1}a{idx + 1}")
                edges[(pod, idx)] = self.addHost(f"p{pod + 1}e{idx + 1}")

        # Hosts under each edge node.
        for pod in range(k):
            for edge_idx in range(half):
                for host_idx in range(half):
                    name = f"p{pod + 1}e{edge_idx + 1}h{host_idx + 1}"
                    hosts[(pod, edge_idx, host_idx)] = self.addHost(name)

        # Host <-> edge links.
        for pod in range(k):
            for edge_idx in range(half):
                edge = edges[(pod, edge_idx)]
                for host_idx in range(half):
                    self.addLink(hosts[(pod, edge_idx, host_idx)], edge)

        # Edge <-> aggregation links inside each pod (full bipartite).
        for pod in range(k):
            for edge_idx in range(half):
                for agg_idx in range(half):
                    self.addLink(edges[(pod, edge_idx)], aggs[(pod, agg_idx)])

        # Aggregation <-> core links:
        # aggregation i connects to all cores in core-group i.
        for pod in range(k):
            for agg_idx in range(half):
                agg = aggs[(pod, agg_idx)]
                for core_idx in range(half):
                    self.addLink(agg, cores[(agg_idx, core_idx)])


topos = {
    "fattree_direct": (lambda k=8: FatTreeDirectTopo(k=k))
}

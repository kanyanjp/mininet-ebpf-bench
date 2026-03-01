"""Custom 10x10 host-only torus-like mesh (no switches)."""

from mininet.topo import Topo


class HostMesh10x10Topo(Topo):
    """100 hosts, each connected to right and down neighbors with wrap-around."""

    def build(self):
        x = 10
        y = 10

        hosts = {}
        for i in range(x):
            for j in range(y):
                name = f"h{i+1}x{j+1}"
                hosts[(i, j)] = self.addHost(name)

        # Add undirected links once: right + down edges per node
        for i in range(x):
            for j in range(y):
                h = hosts[(i, j)]
                h_right = hosts[(i, (j + 1) % y)]
                h_down = hosts[((i + 1) % x, j)]
                self.addLink(h, h_right)
                self.addLink(h, h_down)


topos = {
    'hostmesh10x10': (lambda: HostMesh10x10Topo())
}

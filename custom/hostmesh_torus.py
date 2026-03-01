"""Parameterized host-only torus mesh topology (no switches)."""

from mininet.topo import Topo


class HostMeshTorusTopo(Topo):
    """x*y hosts in a 2D torus, host-to-host links only."""

    def build(self, x=10, y=10):
        x = int(x)
        y = int(y)
        if x < 2 or y < 2:
            raise Exception('x and y must both be >= 2')

        hosts = {}
        for i in range(x):
            for j in range(y):
                name = f"h{i+1}x{j+1}"
                hosts[(i, j)] = self.addHost(name)

        # Add each undirected edge once (right and down per node)
        for i in range(x):
            for j in range(y):
                h = hosts[(i, j)]
                h_right = hosts[(i, (j + 1) % y)]
                h_down = hosts[((i + 1) % x, j)]
                self.addLink(h, h_right)
                self.addLink(h, h_down)


topos = {
    'hostmesh': (lambda x=10, y=10: HostMeshTorusTopo(x=x, y=y))
}

"""Parameterized host-only torus with Linux bridges inserted per edge."""

from mininet.nodelib import LinuxBridge
from mininet.topo import Topo


class HostMeshTorusLinuxBridgeTopo(Topo):
    """x*y hosts in a 2D torus, each edge is host-bridge-host."""

    def build(self, x=10, y=10):
        x = int(x)
        y = int(y)
        if x < 2 or y < 2:
            raise Exception('x and y must both be >= 2')

        hosts = {}
        for i in range(x):
            for j in range(y):
                hosts[(i, j)] = self.addHost(f"h{i + 1}x{j + 1}")

        # For each torus edge, insert one Linux bridge:
        # host A -- veth -- bridge -- veth -- host B
        bridge_id = 1
        for i in range(x):
            for j in range(y):
                h = hosts[(i, j)]
                h_right = hosts[(i, (j + 1) % y)]
                h_down = hosts[((i + 1) % x, j)]

                br_right = self.addSwitch(f"b{bridge_id}", cls=LinuxBridge)
                bridge_id += 1
                self.addLink(h, br_right)
                self.addLink(h_right, br_right)

                br_down = self.addSwitch(f"b{bridge_id}", cls=LinuxBridge)
                bridge_id += 1
                self.addLink(h, br_down)
                self.addLink(h_down, br_down)


topos = {
    'hostmesh_lxbr': (lambda x=10, y=10: HostMeshTorusLinuxBridgeTopo(x=x, y=y))
}

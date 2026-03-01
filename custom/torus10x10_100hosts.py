"""Custom 10x10 torus topology with 100 hosts (1 host per switch)."""

from mininet.topo import Topo


class Torus10x10HostTopo(Topo):
    """10x10 torus switches, each switch attaches one host."""

    def build(self):
        x = 10
        y = 10

        switches = {}

        # Create switches and one host per switch
        for i in range(x):
            for j in range(y):
                si = i + 1
                sj = j + 1
                loc = f"{si}x{sj}"
                dpid = si * 256 + sj
                s = self.addSwitch(f"s{loc}", dpid=f"{dpid:x}")
                h = self.addHost(f"h{loc}")
                self.addLink(h, s)
                switches[(i, j)] = s

        # Torus connections: right and down neighbors with wrap-around
        for i in range(x):
            for j in range(y):
                s1 = switches[(i, j)]
                s_right = switches[(i, (j + 1) % y)]
                s_down = switches[((i + 1) % x, j)]
                self.addLink(s1, s_right)
                self.addLink(s1, s_down)


topos = {
    'torus10x10h1': (lambda: Torus10x10HostTopo())
}

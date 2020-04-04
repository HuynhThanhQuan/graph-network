class Walk:
    pass


class Trail(Walk):
    pass


class OpenedTrail(Trail):
    pass


class ClosedTrail(Trail):
    pass


class Circuit(Trail):
    pass


class OpenedCircuit(OpenedTrail):
    pass


class ClosedCircuit(ClosedTrail):
    pass


class Path(Trail):
    pass


class Cycle(Path):
    pass


# Special paths
class EulerPath(Path):
    pass


class HamiltonianPath(Path):
    pass

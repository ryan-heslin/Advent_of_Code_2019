from operator import attrgetter

real = attrgetter("real")
imag = attrgetter("imag")


def split_lines(file):
    with open(file) as f:
        return f.read().splitlines()


def split_commas(file):
    with open(file) as f:
        return f.read().rstrip("\n").split(",")


def xmin(coords):
    return int(min(coords, key=real).real)


def xmax(coords):
    return int(max(coords, key=real).real)


def ymin(coords):
    return int(min(coords, key=imag).imag)


def ymax(coords):
    return int(max(coords, key=imag).imag)


def display(coords, xmin=None, xmax=None, ymin=None, ymax=None, reverse=False):
    if xmin is None:
        xmin = int(min(coords, key=real).real)
    if xmax is None:
        xmax = int(max(coords, key=real).real)
    if ymin is None:
        ymin = int(min(coords, key=imag).imag)
    if ymax is None:
        ymax = int(max(coords, key=imag).imag)
    xes = range(xmin, xmax + 1)
    if reverse:
        xes = reversed(xes)

    return "\n".join(
        "".join("#" if complex(x, y) in coords else " " for x in xes)
        for y in range(ymin, ymax + 1)
    )

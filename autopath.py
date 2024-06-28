class AutoPathFactory(pya.PluginFactory):
    def __init__(self):
        super(AutoPathFactory, self).__init__()
        self.register(-1000, "autopath", "Auto Path")

    def create_plugin(self, manager, root, view):
        return AutoPath()

    instance = None


class AutoPath(pya.Plugin):
    def __init__(self):
        super(AutoPath, self).__init__()
        self.window = pya.MainWindow.instance()
        self.layers = [0, 1, 2]
        self.p1 = None
        self.margin = 100
        self.layout = pya.CellView.active().cell.layout()

    def activated(self):
        self.window.message("Click on point to set the origin", 10000)

    def deactivated(self):
        self.window.instance().message("", 0)

    def mouse_click_event(self, p, buttons, prio):
        if prio:
            grid = self.window.grid_micron()
            p = pya.DPoint(grid * round(p.x / grid), grid * round(p.y / grid))
            self.cell = pya.CellView.active().cell
            self.layers = [0, 1, 2]
            if self.p1 is not None:
                print("second")
                p2 = p
                path = self.find_path(
                    (self.p1.x, self.p1.y), (p2.x, p2.y), self.margin, grid, set()
                )
                if path is not None:
                    path = [pya.DPoint(p[0], p[1]) for p in path]
                    self.cell.shapes(0).insert(pya.Path(path, 100))
                self.p1 = None
            else:
                print("first")
                self.p1 = p
            print(self.window.grid_micron())
            return True
        return False

    def find_path(self, p, end, margin, step, d):
        print(p, end)
        if p in d:
            return None

        d.add(p)

        for i in self.layers:
            box = pya.DBox(p[0] - margin, p[1] - margin, p[0] + margin, p[1] + margin)
            it = self.cell.begin_shapes_rec_overlapping(i, box)
            if not it.at_end():
                return None

        if (p[0] == end[0]) and (p[1] == end[1]):
            return [p]

        y_offset = step if p[1] < end[1] else -step
        if p[0] == end[0]:
            offsets = [(0, y_offset), (step, 0)]
        elif p[0] < end[0]:
            offsets = [(step, 0), (0, y_offset)]
        else:
            offsets = [(-step, 0), (0, y_offset)]

        for offset in offsets:
            path = self.find_path(
                (p[0] + offset[0], p[1] + offset[1]), end, margin, step, d
            )
            if path is not None:
                return [p] + path

        for offset in offsets:
            path = self.find_path(
                (p[0] - offset[0], p[1] - offset[1]), end, margin, step, d
            )
            if path is not None:
                return [p] + path

        return None


# Create and store the singleton instance
AutoPathFactory.instance = AutoPathFactory()

import pya


class MicrofluidicsLib(pya.Library):
    def __init__(self):
        self.description = "Microfluidic components."
        self.layout().register_pcell("Tree", Tree())
        self.register("Microfluidics")


class Tree(pya.PCellDeclarationHelper):
    def __init__(self):
        super(Tree, self).__init__()

        # declare the parameters
        self.param("flow", self.TypeLayer, "Flow Layer", default=pya.LayerInfo(1, 0))
        self.param("control", self.TypeLayer, "Control Layer")
        self.param("flow_width", self.TypeDouble, "Flow Channel Width", default=100)
        self.param(
            "control_width", self.TypeDouble, "Control Channel Width", default=100
        )
        self.param("num_levels", self.TypeInt, "Number of Levels", default=3)
        self.param("leaf_gap", self.TypeDouble, "Leaf Node Gap", default=400)
        self.param(
            "horizontal_gap",
            self.TypeDouble,
            "Horizontal Flow-Control Gap",
            default=100,
        )
        self.param(
            "vertical_gap", self.TypeDouble, "Vertical Flow-Control Gap", default=200
        )
        self.param(
            "control_gap", self.TypeDouble, "Vertical Control-Control Gap", default=200
        )

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return f"Tree(L={self.flow}, N={self.num_levels})"

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        if self.num_levels < 1:
            self.num_levels = 1

        num_leaves = 2**self.num_levels
        width = num_leaves * (self.flow_width + self.leaf_gap)
        height = (
            self.num_levels
            * (self.flow_width + 2 * self.control_width + 2 * self.vertical_gap)
            + (self.num_levels - 1) * self.control_gap
        )
        self.make_tree(
            top=height / 2, left=-width / 2, right=width / 2, level=self.num_levels
        )

    def make_tree(self, top, left, right, level):
        control_shapes = self.cell.shapes(self.control_layer)
        flow_shapes = self.cell.shapes(self.flow_layer)
        mid = (left + right) / 2
        q1 = 0.75 * left + 0.25 * right
        q3 = 0.25 * left + 0.75 * right
        root_left = mid - self.flow_width / 2
        root_right = mid + self.flow_width / 2
        root_top = top
        if level == 0:
            flow_shapes.insert(
                pya.DBox(
                    root_left,
                    root_top
                    - self.flow_width
                    - self.vertical_gap
                    - self.control_width,
                    root_right,
                    root_top,
                )
            )
            return
        else:
            root_bottom = (
                root_top
                - 2 * self.flow_width
                - 2 * self.vertical_gap
                - 2 * self.control_width
                - self.control_gap
            )
            flow_shapes.insert(
                pya.DBox(
                    root_left,
                    root_bottom,
                    root_right,
                    root_top,
                )
            )
            flow_shapes.insert(
                pya.DBox(
                    q1 - self.flow_width / 2,
                    root_bottom,
                    q3 + self.flow_width / 2,
                    root_bottom + self.flow_width,
                )
            )
            control_shapes.insert(
                pya.DBox(
                    root_left - self.horizontal_gap - self.control_width,
                    root_bottom - self.vertical_gap / 2,
                    root_left - self.horizontal_gap,
                    root_bottom + self.flow_width + self.vertical_gap + self.control_width,
                )
                                )
            control_shapes.insert(
                pya.DBox(
                    root_right + self.horizontal_gap,
                    root_bottom - self.vertical_gap - self.control_width,
                    root_right + self.horizontal_gap + self.control_width,
                    root_bottom + self.flow_width + self.vertical_gap / 2,
                )
                                )
            self.make_tree(
                top=root_bottom + self.flow_width,
                left=left,
                right=mid,
                level=level - 1,
            )
            self.make_tree(
                top=root_bottom + self.flow_width,
                left=mid,
                right=right,
                level=level - 1,
            )


MicrofluidicsLib()

import pya


class MicrofluidicsLib(pya.Library):
    def __init__(self):
        self.description = "Microfluidic components."
        self.layout().register_pcell("Tree", Tree())
        self.register("Microfluidics")


class Tree(pya.PCellDeclarationHelper):
    def __init__(self):
        super(Tree, self).__init__()

        self.param(
            "square", self.TypeLayer, "Flow Square Layer", default=pya.LayerInfo(1, 0)
        )
        self.param("round", self.TypeLayer, "Flow Round Layer")
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
        self.param(
            "bidirectional",
            self.TypeBoolean,
            "Control Spans Left-to-Right",
            default=True,
        )

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return f"Tree(N={self.num_levels})"

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
        bounds = self.make_tree(
            top=height / 2,
            left=-width / 2,
            right=width / 2,
            top_offset=0,
            level=self.num_levels,
        )

        for bound in bounds:
            self.cell.shapes(self.control_layer).insert(
                pya.DBox(
                    -width / 2 if self.bidirectional else bound[1],
                    bound[0] - self.control_width,
                    width / 2,
                    bound[0],
                )
            )

    def make_tree(self, top, left, right, top_offset, level):
        control_shapes = self.cell.shapes(self.control_layer)
        flow_square_shapes = self.cell.shapes(self.square_layer)
        flow_round_shapes = self.cell.shapes(self.round_layer)
        mid = (left + right) / 2
        if level == 0:
            flow_square_shapes.insert(
                pya.DBox(
                    mid - self.flow_width / 2,
                    top
                    - 2 * self.flow_width
                    - 1.5 * self.vertical_gap
                    - self.control_width,
                    mid + self.flow_width / 2,
                    top - top_offset,
                )
            )
            return []
        else:
            root = pya.DBox(
                mid - self.flow_width / 2,
                top
                - 2 * self.flow_width
                - 2 * self.vertical_gap
                - 2 * self.control_width
                - self.control_gap,
                mid + self.flow_width / 2,
                top - top_offset,
            )
            flow_square_shapes.insert(root)

            left_control = pya.DBox(
                root.left - self.horizontal_gap - self.control_width,
                root.bottom - self.vertical_gap / 2,
                root.left - self.horizontal_gap,
                root.bottom + self.flow_width + self.vertical_gap + self.control_width,
            )
            control_shapes.insert(left_control)
            right_control = pya.DBox(
                root.right + self.horizontal_gap,
                root.bottom - self.vertical_gap - self.control_width,
                root.right + self.horizontal_gap + self.control_width,
                root.bottom + self.flow_width + self.vertical_gap / 2,
            )
            control_shapes.insert(right_control)

            offset = 0
            q1 = 0.75 * left + 0.25 * right
            q3 = 0.25 * left + 0.75 * right
            split = pya.DBox(
                q1 - self.flow_width / 2,
                root.bottom,
                q3 + self.flow_width / 2,
                root.bottom + self.flow_width,
            )

            if split.left + self.flow_width + self.horizontal_gap > left_control.left:
                offset = split.top - (right_control.bottom - self.vertical_gap / 2)
                split.left = max(
                    left, left_control.left - self.horizontal_gap - self.flow_width
                )
                split.right = min(
                    right, right_control.right + self.horizontal_gap + self.flow_width
                )
                left_flow = pya.DBox(
                    split.left,
                    right_control.bottom - self.vertical_gap / 2 - self.flow_width,
                    split.left + self.flow_width,
                    split.top,
                )
                flow_square_shapes.insert(left_flow)

                right_flow = pya.DBox(
                    split.right,
                    right_control.bottom - self.vertical_gap / 2 - self.flow_width,
                    split.right - self.flow_width,
                    split.top,
                )
                flow_square_shapes.insert(right_flow)

                flow_square_shapes.insert(
                    pya.DBox(
                        q3 - self.flow_width / 2,
                        right_flow.bottom,
                        right_flow.right,
                        right_flow.bottom + self.flow_width,
                    )
                )
                flow_square_shapes.insert(
                    pya.DBox(
                        left_flow.left,
                        left_flow.bottom,
                        q1 + self.flow_width / 2,
                        left_flow.bottom + self.flow_width,
                    )
                )
            else:
                offset = 0

            split_round = pya.DBox(
                max(
                    left_control.left - self.horizontal_gap,
                    split.left + self.flow_width,
                ),
                split.bottom,
                min(
                    right_control.right + self.horizontal_gap,
                    split.right - self.flow_width,
                ),
                split.top,
            )
            split_square = pya.Region(split.to_itype(self.layout.dbu)) - pya.Region(
                split_round.to_itype(self.layout.dbu)
            )
            flow_square_shapes.insert(split_square)
            split_round.left -= self.flow_width
            split_round.right += self.flow_width
            flow_round_shapes.insert(split_round)
            bounds = self.make_tree(
                top=root.bottom + self.flow_width,
                left=left,
                right=mid,
                top_offset=offset,
                level=level - 1,
            )
            self.make_tree(
                top=root.bottom + self.flow_width,
                left=mid,
                right=right,
                top_offset=offset,
                level=level - 1,
            )
            return bounds + [
                (left_control.top, left_control.left),
                (right_control.bottom + self.control_width, right_control.left),
            ]


MicrofluidicsLib()

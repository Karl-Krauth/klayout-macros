class Tree(pya.PCellDeclarationHelper):
    def __init__(self):
        super(Tree, self).__init__()

        # declare the parameters
        self.param("flow", self.TypeLayer, "Flow Layer", default=pya.LayerInfo(1, 0))
        self.param("control", self.TypeLayer, "Control Layer")
        self.param("flow_width", self.TypeDouble, "Flow Channel Width", default=1)
        self.param("control_width", self.TypeDouble, "Control Channel Width", default=1)
        self.param("num_levels", self.TypeInt, "Number of Levels", default=3)
        self.param("height", self.TypeDouble, "Tree Height", default=10)
        self.param("width", self.TypeDouble, "Tree Width", default=20)
        self.param("spacing", self.TypeDouble, "Flow Control Spacing", default=1)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return f"Tree(L={self.flow}, N={self.num_levels})"

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        if self.num_levels < 1:
            self.num_levels = 1

        width = self.width / self.layout.dbu
        height = self.height / self.layout.dbu
        flow_width = self.flow_width / self.layout.dbu
        control_width = self.control_width / self.layout.dbu
        spacing = self.spacing / self.layout.dbu

        level_height = height / self.num_levels
        for i in range(self.num_levels):
            subtree_offset = width / (2**i)
            left = subtree_offset / 2
            top = -i * level_height
            bottom = top - level_height
            right = width
            for j in range(2**i):
                x = j * subtree_offset + left
                y = top
                self.cell.shapes(self.flow_layer).insert(pya.DBox(x, y - level_height, x + flow_width, y))
                if i != self.num_levels - 1:
                    self.cell.shapes(self.flow_layer).insert(pya.DBox(x - subtree_offset / 4, y - level_height, x + flow_width + subtree_offset / 4, y - level_height + flow_width))
            if i != self.num_levels - 1:
                self.cell.shapes(self.control_layer).insert(pya.DBox(left - spacing - control_width, bottom + spacing + flow_width, right, bottom + spacing + flow_width + control_width))
                self.cell.shapes(self.control_layer).insert(pya.DBox(left - spacing - control_width, bottom - spacing / 2, left - spacing, bottom + spacing + flow_width + control_width))
                self.cell.shapes(self.control_layer).insert(pya.DBox(left + flow_width + spacing, bottom - spacing - control_width, right, bottom - spacing))
                self.cell.shapes(self.control_layer).insert(pya.DBox(left + flow_width + spacing, bottom - spacing - control_width, left + flow_width + spacing + control_width, bottom + flow_width + spacing / 2))


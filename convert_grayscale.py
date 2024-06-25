import math
import pya


layout = pya.CellView.active().layout()
h = 15
round_layer = 2
square_layer = 1
for i in range(5):
     print(i, layout.get_info(i))

layer_ids = {}
for cell_name in ["device", "chamber"]:
    square_region = pya.Region(layout.cell(cell_name).shapes(square_layer))
    cell = layout.cell(cell_name)
    for shape in cell.shapes(round_layer):
        box = shape.bbox().to_dtype(layout.dbu)
        if box.width == box.height:
            raise ValueError("Script does not support square boxes.")
        elif box.width() > box.height():
            w = box.height()
            change_horizontal = False
        else:
            w = box.width()
            change_horizontal = True
        r = h / 2 + w ** 2 / (8 * h)
        inc = 1
        bound = math.ceil(w / 2 + inc / 2)
        curr_y = None
        for i in range(inc, bound, inc):
            y = (round(255 * (r - math.sqrt(r ** 2 - i ** 2)) / h))
            if y == curr_y:
                upper = i + inc / 2
                continue
            if curr_y is not None:
                outer_box = box.enlarged(
                    min(0, upper - bound + inc) if change_horizontal else 0,
                    0 if change_horizontal else min(0, upper - bound + inc)
                ).to_itype(layout.dbu)
                inner_box = box.enlarged(
                    min(0, lower - bound + inc) if change_horizontal else 0,
                    0 if change_horizontal else min(0, lower - bound + inc)
                ).to_itype(layout.dbu)
                if curr_y not in layer_ids:
                    layer_ids[curr_y] = layout.layer(str(curr_y))
                for shape in (pya.Region(outer_box) - pya.Region(inner_box)).each():
                    cell.shapes(layer_ids[curr_y]).insert(shape.bbox())
            curr_y = y
            upper = i + inc / 2
            lower = i - inc / 2
        outer_box = box.enlarged(
            min(0, upper - bound + inc) if change_horizontal else 0,
            0 if change_horizontal else min(0, upper - bound + inc)
        ).to_itype(layout.dbu)
        inner_box = box.enlarged(
            min(0, lower - bound + inc) if change_horizontal else 0,
            0 if change_horizontal else min(0, lower - bound + inc)
        ).to_itype(layout.dbu)
        if curr_y not in layer_ids:
            layer_ids[curr_y] = layout.layer(str(curr_y))
        for shape in (pya.Region(outer_box) - pya.Region(inner_box)).each():
            cell.shapes(layer_ids[curr_y]).insert(shape.bbox())
        

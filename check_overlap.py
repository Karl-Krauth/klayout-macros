import pya

layout = pya.CellView.active().layout()
cell = layout.cell("device")
print(layout.get_info(0))
flow_region = pya.Region(cell.shapes(0))
control_region = pya.Region(cell.shapes(3))
outer_offset = 50
inner_offset = 25
holes = pya.Region()
for overlap in (flow_region & control_region).each():
    if not overlap.is_box():
        raise ValueError("This script only allows rectangular overlaps.")

    box = overlap.bbox().to_dtype(layout.dbu)
    hbox = pya.DBox(
        box.left - outer_offset,
        box.bottom + inner_offset,
        box.right + outer_offset,
        box.top - inner_offset,
    ).to_itype(layout.dbu)

    vbox = pya.DBox(
        box.left + inner_offset,
        box.bottom - outer_offset,
        box.right - inner_offset,
        box.top + outer_offset,
    ).to_itype(layout.dbu)

    if not control_region.covering(hbox).is_empty():
        holes.insert(hbox)
    elif not control_region.covering(vbox).is_empty():
        holes.insert(vbox)
    else:
        raise ValueError(
            "Found overlapping region which couldn't fit a horizontal or vertical hole."
        )

cell.shapes(3).clear()
cell.shapes(3).insert(control_region - holes)

from matplotlib import pyplot as plt
from pygments.lexers import go
from make_json_ordered_parts import ordered_part
from plotly.colors import qualitative
#todo under development by Job
def build_part_color_map(all_parts_import):
    all_parts = [part for part in all_parts_import if part.endswith("01")]
    colours = qualitative.Plotly
    color_map = {}
    for i, route in enumerate(all_parts):
        color_map[route] = colours[i % len(colours)]

    return color_map

def plot_different_properties(properties, units):
    x_property = properties[0]
    y_property = properties[1]

    x_values = getattr(ordered_part, x_property)
    y_values = getattr(ordered_part, y_property)
    part_numbers = ordered_part.part_id

    color_map = build_part_color_map(ordered_part.part_id)

    combined = list(zip(y_values, x_values, part_numbers))

    # sort by part number or time
    combined.sort(reverse=False, key=lambda x: x[0])
    y_values, x_values, part_numbers = zip(*combined)
    color_values = [None]*len(part_numbers)
    print(color_map)
    j = 0
    for i, part_id in enumerate(part_numbers):
        if part_id.endswith("01"):
            color_values[i] = color_map[part_id]
            j+=1
        else:
            color_values[i] = color_map[part_numbers[0]]

    plt.figure()
    plt.bar(x_values, y_values, color=color_values)
    plt.xlabel(x_property + " [" + units[0] + "]")
    plt.ylabel(y_property + " [" + units[1] + "]")
    plt.title(f"{y_property} per {x_property}")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


properties = [["part_id", "total_quantity"],
              ["part_id", "total_time_all_parts"]]
units = [["-", "-"],
         ["-", "hours"]]
for i, property in enumerate(properties):
    plot_different_properties(property, units[i])
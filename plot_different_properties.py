from matplotlib import pyplot as plt
from make_json_ordered_parts import ordered_part
from plotly.colors import qualitative

def build_route_color_map(all_routes_import):
    all_routes= []
    for route in all_routes_import:
            if route not in all_routes:
                all_routes.append(route)

    colours = qualitative.Plotly
    color_map = {}
    for i, route in enumerate(all_routes):
        color_map[route] = colours[i % len(colours)]

    return color_map

def plot_different_properties(properties, units):
    x_property = properties[0]
    y_property = properties[1]

    x_values = getattr(ordered_part, x_property)
    y_values = getattr(ordered_part, y_property)
    route_numbers = ordered_part.route_number

    color_map = build_route_color_map(route_numbers)

    combined = list(zip(route_numbers, y_values, x_values))

    # sort by production line
    combined.sort(reverse=False, key=lambda x: x[0])
    route_numbers, y_values, x_values = zip(*combined)
    color_values = [color_map[number] for number in route_numbers]

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
from matplotlib import pyplot as plt
from pygments.lexers import go
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

def plot_different_production_lines(properties, units):
    x_property = properties[0]
    y_property = properties[1]

    x_values = getattr(ordered_part, x_property)
    y_values = getattr(ordered_part, y_property)
    route_numbers = ordered_part.route_number

    production_lines_x = [None] * (max(route_numbers)+1)
    production_lines_y = [None] * (max(route_numbers)+1)
    route_numbers_2 = range(len(production_lines_x))
    for i in route_numbers_2:
        x = []
        y = []
        for j in range(len(ordered_part.part_id)):
            if ordered_part.route_number[j] == i:
                y.append(y_values[j])
        production_lines_x[i] = "production line "+str(i)
        production_lines_y[i] = sum(y)

    color_map = build_route_color_map(route_numbers_2)

    combined = list(zip(route_numbers_2, production_lines_y, production_lines_x))

    # sort by production line
    combined.sort(reverse=False, key=lambda x: x[0])
    route_numbers, y_values, x_values = zip(*combined)
    color_values = [color_map[number] for number in route_numbers]

    plt.figure()
    plt.bar(x_values, y_values, color=color_values)
    plt.xlabel("production line [" + units[0] + "]")
    plt.ylabel(y_property + " [" + units[1] + "]")
    plt.title(f"{y_property} per production line")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

properties = [["part_id", "total_quantity"],
              ["part_id", "total_time_all_parts"]]
units = [["-", "-"],
         ["-", "hours"]]
for i, property in enumerate(properties):
    plot_different_properties(property, units[i])
    plot_different_production_lines(property, units[i])
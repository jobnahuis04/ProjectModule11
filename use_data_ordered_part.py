from make_json_ordered_parts import ordered_part
import plotly.graph_objects as go
from plotly.colors import n_colors, qualitative


def count_unique_paths_with_indices():
    route_to_indices = {}

    for i, route in enumerate(ordered_part.route):
        key = tuple(route)
        if key not in route_to_indices:
            route_to_indices[key] = []
        route_to_indices[key].append(i)

    unique_routes = []
    indices_per_route = []
    total_times_per_route = []

    for route_tuple, indices in route_to_indices.items():
        route = list(route_tuple)
        unique_routes.append(route)
        indices_per_route.append(indices)

        # initialize totals per machine step
        n = len(route)
        totals = [0.0] * n

        # sum times for all parts following this route
        for idx in indices:
            times = ordered_part.total_machine_time_all_parts[idx]
            for j in range(n):
                totals[j] += times[j]

        total_times_per_route.append(totals)

    print(f"{len(unique_routes)} unique paths total")

    return unique_routes, indices_per_route, total_times_per_route

unique_routes, corresponding_indices, total_times_per_route = count_unique_paths_with_indices()
print(total_times_per_route)

def build_global_machine_color_map(all_routes):
    # collect all unique machines across all routes
    all_machines = []
    for route in all_routes:
        for machine in route:
            if machine not in all_machines:
                all_machines.append(machine)

    palette = qualitative.Plotly

    color_map = {}
    for i, machine in enumerate(all_machines):
        color_map[machine] = palette[i % len(palette)]

    return color_map

def make_sankey_for_one_route(unique_route, total_time, title, color_map):
    node_colors = [color_map[m] for m in unique_route]
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = unique_route,
          color = node_colors
        ),
        link = dict(
            source=list(range(len(unique_route) - 1)),
            target = list(range(1, len(unique_route))),
            value = total_time
      ))])

    fig.update_layout(title_text="Production line "+str(title), font_size=10)
    fig.show()
color_map = build_global_machine_color_map(unique_routes)
for i, route in enumerate(unique_routes):
    make_sankey_for_one_route(route ,total_times_per_route[i],i,color_map)
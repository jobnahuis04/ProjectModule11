from make_json_ordered_parts import ordered_part
import plotly.graph_objects as go
from plotly.colors import n_colors


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


def make_sankey_for_one_route(unique_route,total_time,title):
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = unique_route,
          color = "blue"
        ),
        link = dict(
            source=list(range(len(unique_route) - 1)),
            target = list(range(1, len(unique_route))),
            value = total_time
      ))])

    fig.update_layout(title_text="Production line "+str(title), font_size=10)
    fig.show()
for i, route in enumerate(unique_routes):
    make_sankey_for_one_route(route ,total_times_per_route[i],i)
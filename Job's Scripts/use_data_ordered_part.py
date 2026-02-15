from make_json_ordered_parts import ordered_part
import plotly.graph_objects as go
from plotly.colors import qualitative
from plotly.subplots import make_subplots

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

        n = len(route)
        totals = [0.0] * n

        for idx in indices:
            times = ordered_part.total_machine_time_all_parts[idx]
            for j in range(n):
                totals[j] += times[j]

        total_times_per_route.append(totals)

    print(f"{len(unique_routes)} unique paths total")
    for i, route in enumerate(unique_routes):
        route.append("Done")
        total_times_per_route[i].append(0)

    return unique_routes, indices_per_route, total_times_per_route

def build_global_machine_color_map(all_routes):
    all_machines = []
    for route in all_routes:
        for machine in route:
            if machine not in all_machines:
                all_machines.append(machine)

    colours = qualitative.Plotly

    color_map = {}
    for i, machine in enumerate(all_machines):
        color_map[machine] = colours[i % len(colours)]

    return color_map

def make_all_sankeys_on_page(unique_routes, total_times_per_route, color_map):
    n_routes = len(unique_routes)
    rows = (n_routes + 2) // 2  # 2 columns per row
    cols = min(2, n_routes)

    fig = make_subplots(
        rows=rows,
        cols=cols,
        specs=[[{"type": "domain"}]*cols for _ in range(rows)],
        subplot_titles=[f"Route {i}" for i in range(n_routes)]
    )

    for i, route in enumerate(unique_routes):
        row = i // 2 + 1
        col = i % 2 + 1

        n = len(route)
        source = list(range(n-1))
        target = list(range(1, n))
        values = total_times_per_route[i]

        node_colors = [color_map[m] for m in route]
        node_labels = [f"{m}<br>{values[j]:.1f} h" for j, m in enumerate(route)]

        sankey = go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=node_labels,
                color=node_colors
            ),
            link=dict(
                source=source,
                target=target,
                value=values,
                customdata=values
            )
        )

        fig.add_trace(sankey, row=row, col=col)

    fig.update_layout(
        height=rows*400,
        width=2000,
        title_text="All Production Routes",
        font_size=10
    )

    fig.show()
unique_routes, corresponding_indices, total_times_per_route = count_unique_paths_with_indices()
color_map = build_global_machine_color_map(unique_routes)
make_all_sankeys_on_page(unique_routes, total_times_per_route, color_map)

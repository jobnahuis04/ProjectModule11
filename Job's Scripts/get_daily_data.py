from matplotlib.style.core import available

from make_json_ordered_parts import ordered_part
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def flatten(x):
    if isinstance(x, list):
        result = []
        for item in x:
            result.extend(flatten(item))
        return result
    else:
        return [x]
df = pd.read_csv("../data/Order pattern.csv")

df["Order date"] = pd.to_datetime(df["Order date"])
df["Desired delivery date"] = pd.to_datetime(df["Desired delivery date"])

start_date = df["Order date"].min()
end_date = df["Desired delivery date"].max()

class Planning:
    def __init__(self):
        self.day = []
        self.part_numbers = []
        self.part_quantities = []
        self.part_times = []
        self.setup_times = []
        self.route = []
        self.route_time = []
        self.machine_quantity = []


planning = Planning()

planning.machine_quantity = [
    [2,2,2,2,1,2], # route 0 / SM,TM,MM,GM,CMM,A
    [2,0.75,0.5,1], # route 1 / MC,GM,CMM,A
    [1,2,1.5,1], # route 2 / SM,MM,DM,CMM
    [1,2,1,0.75,0.75], # route 3 / SM,MC,GM,CMM,A
    [0.5,0.25,0.5,0.5,0.5,0.5,0.25,0.25], # route 4 / SM,TM,MM,TM,GM,DM,CMM,A
    [0.5,0.1,0.25,0.5,0.2,0.25,0.2], # route 5 / TM,CMM,TM,GM,CMM,MM,CMM
    [0.33], # route 6 / A
    [0.1,0.2,0.3,0.25,0.1], # route 7 / SM,TM,MM,GM,CMM
    [0.1,0.1,0.1], # route 8 / SM,TM,MM
    [0.2,0.4,0.4] # route 9 / SM,MM,DM
    ]

flat_order_dates = []
flat_delivery_dates = []
flat_part_ids = []
flat_quantities = []

for i, part_id in enumerate(ordered_part.part_id):
    order_dates = flatten(ordered_part.orders.order_date[i])
    delivery_dates = flatten(ordered_part.orders.delivery_date[i])
    quantities = flatten(ordered_part.orders.parts_per_day[i])

    for od, dd, q in zip(order_dates, delivery_dates, quantities):
        flat_part_ids.append(part_id)
        flat_order_dates.append(od)
        flat_delivery_dates.append(dd)
        flat_quantities.append(q)

df_clean = pd.DataFrame({
    "part_id": flat_part_ids,
    "order_date": pd.to_datetime(flat_order_dates),
    "delivery_date": pd.to_datetime(flat_delivery_dates),
    "quantity": flat_quantities
})
part_index_map = {p: i for i, p in enumerate(ordered_part.part_id)}
seen = set()
unique_route_numbers = []
part_routes = []
for i, rn in enumerate(ordered_part.route_number):
    if rn not in seen:
        seen.add(rn)
        unique_route_numbers.append(rn)
        part_routes.append(ordered_part.route[i])

for i, day in enumerate(pd.date_range(start=start_date, end=end_date)):
    active = df_clean[
        (df_clean["order_date"] < day) & (df_clean["delivery_date"] > day)
    ]

    grouped = active.groupby("part_id")["quantity"].sum()
    planning.day.append(day.date())
    planning.part_numbers.append(grouped.index.tolist())
    planning.part_quantities.append(grouped.values.tolist())

    planning.route_time.append([])

    for j, route in enumerate(part_routes):
        planning.route_time[i].append([0] * len(route))

    for p, part_number in enumerate(planning.part_numbers[i]):
        idx = part_index_map[part_number]
        route_number = ordered_part.route_number[idx]

        # add setup time ONCE
        for l in range(len(ordered_part.setup_time[idx])):
            mq = planning.machine_quantity[route_number][l]
            planning.route_time[i][route_number][l] += ordered_part.setup_time[idx][l]/mq

        # add production time
        for j in range(len(ordered_part.avg_idle_time[idx])):
            mq = planning.machine_quantity[route_number][j]
            machine_time = (
                        (ordered_part.avg_idle_time[idx][j] + ordered_part.process_time[idx][j])
                        * planning.part_quantities[i][p]
                        / mq
            )
            planning.route_time[i][route_number][j] += machine_time


for j in unique_route_numbers:
    plt.figure()

    for k, machine in enumerate(part_routes[j]):
        y = [
            planning.route_time[i][j][k] for i in range(len(planning.day))
        ]

        line, = plt.plot(
            planning.day,
            y,
            label=f"step {k+1}: {machine}({planning.machine_quantity[j][k]}x)"
        )
        plt.axhline(
            np.mean(y),
            linestyle="--",
            color=line.get_color(),
            label="_nolegend_"  # <-- key trick
        )
    plt.axhline(16, linestyle="-", color="k", label="hours in a day")
    plt.xlabel("Day")
    plt.ylabel("Total machine time per day [h]")
    plt.title(f"Production line {j}")
    plt.legend(loc="upper right")
    plt.ylim(0, 40)
    plt.xlim(start_date, end_date)
    plt.xticks(rotation=45)
    plt.savefig(f"{j}.png")


# for j in unique_route_numbers[5::]:
#     plt.figure()
#     for k, machine in enumerate(part_routes[j]):
#         y = [
#             planning.route_time[i][j][k] for i in range(len(planning.day))
#          ]
#         plt.plot(planning.day, y, label= f"step {k+1}: {machine}({planning.machine_quantity[j][k]}x)")
#
#     plt.xlabel("Day")
#     plt.ylabel("Total machine time per day [h]")
#     plt.title(f"Production line {j}")
#     plt.legend(loc="upper right")
#     plt.ylim(0, 40)
#     plt.xlim(start_date, end_date)
#     plt.xticks(rotation=45)
#     plt.savefig(f"{j}.png")
plt.show()


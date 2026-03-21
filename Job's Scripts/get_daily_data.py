from make_json_ordered_parts import ordered_part
import pandas as pd
import matplotlib.pyplot as plt

def flatten(x):
    if isinstance(x, list):
        result = []
        for item in x:
            result.extend(flatten(item))
        return result
    else:
        return [x]

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
    [1,1,1,1,1,1], # route 0
    [1,1,1,1], # route 1
    [1,1,1,1], # route 2
    [1,1,1,1,1], # route 3
    [1,1,1,1,1,1,1,1], # route 4
    [1,1,1,1,1,1,1], # route 5
    [1], # route 6
    [1,1,1,1,1], # route 7
    [1,1,1], # route 8
    [1,2,1] # route 9
    ]

df = pd.read_csv("../data/Order pattern.csv")

df["Order date"] = pd.to_datetime(df["Order date"])
df["Desired delivery date"] = pd.to_datetime(df["Desired delivery date"])

start_date = df["Order date"].min()
end_date = df["Desired delivery date"].max()

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
    planning.route.append([]*len(set(ordered_part.route_number)))
    #planning.route_time.append([]*len(set(ordered_part.route_number)))
    #part_routes = list({tuple(r) for r in ordered_part.route})

    planning.route_time.append([])

    for j, route in enumerate(part_routes):
        planning.route_time[i].append([0] * len(route))

    for p, part_number in enumerate(planning.part_numbers[i]):
        idx = ordered_part.part_id.index(part_number)
        route_number = ordered_part.route_number[idx]
        machine_time = [
            (ordered_part.avg_idle_time[idx][j] + ordered_part.process_time[idx][j]) * planning.part_quantities[i][p]
            / planning.machine_quantity[route_number][j]
            for j in range(len(ordered_part.avg_idle_time[idx]))
        ]
        for l in range(len(machine_time)):
            planning.route_time[i][route_number][l] += machine_time[l] + ordered_part.setup_time[idx][l]*planning.machine_quantity[route_number][l] # setup time doubles with 2 machines.


for j in unique_route_numbers:
    plt.figure()
    for k, machine in enumerate(part_routes[j]):
        y = [
            planning.route_time[i][j][k] for i in range(len(planning.day))
         ]
        plt.plot(planning.day, y, label= f"step {k+1}: {machine}")

    plt.xlabel("Day")
    plt.ylabel("Total machine time per day")
    plt.title(f"Production line {j}")
    plt.legend(loc="upper right")
    plt.xticks(rotation=45)
plt.show()


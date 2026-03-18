from make_json_ordered_parts import ordered_part
import pandas as pd

class Planning:
    def __init__(self):
        self.day = []
        self.part_numbers = []
        self.part_quantities = []
        self.part_times = []
        self.setup_times = []

df = pd.read_csv("../data/Order pattern.csv")
order_date = pd.to_datetime(df["Order date"].tolist())
delivery_date = pd.to_datetime(df["Desired delivery date"].tolist())

order_date_sorted = order_date.sort_values()
delivery_date_sorted = delivery_date.sort_values()
start_date = order_date_sorted[0]
end_date = delivery_date_sorted[-1]
end_date = order_date_sorted[10]

planning = Planning()
for index, day in enumerate(pd.date_range(start=start_date, end=end_date)):
    planning.day.append(day.date)
    planning.part_numbers.append([])
    planning.part_quantities.append([])
    for i,part_id in enumerate(ordered_part.part_id):
        for j,ordered_date in enumerate(ordered_part.orders.order_date[i]):
            if isinstance(ordered_date, str):
                if pd.to_datetime(ordered_date) < day and pd.to_datetime(ordered_part.orders.delivery_date[i][j]) > day:
                    if part_id not in planning.part_numbers:
                        planning.part_numbers[index].append(part_id)
                        planning.part_quantities[index].append(ordered_part.orders.parts_per_day[i][j])
                    else:
                        pass
                else:
                    pass
            else:
                pass





print("hey")
import pandas as pd
from make_json_ordered_parts import *

df = pd.read_csv("../data/Order pattern.csv")

df["Order date"] = pd.to_datetime(df["Order date"])
df["Desired delivery date"] = pd.to_datetime(df["Desired delivery date"])

start_date = df["Order date"].min()
end_date = df["Desired delivery date"].max()

class Available_machines:
    def __init__(self,start_date,end_date):
        self.machine_id =           ["SM", "TM", "MM", "MC", "DM", "GM", "CMM", "A"]
        shifts = 2
        hours = 8
        days = len(pd.date_range(start=start_date, end=end_date))
        self.total_time = shifts * hours * days
        print(self.total_time)

        self.old_machine_quantity = dict(zip(self.machine_id, [5, 4, 5, 5, 2, 4, 4, 2]))
        #self.new_machine_quantity = dict(zip(self.machine_id, [5, 4, 6, 4, 3, 5, 4, 5])) to match planning
        #self.new_machine_quantity = dict(zip(self.machine_id, [6, 3, 7, 3, 4, 5, 3, 5])) to match OEE calc
        # [1.1, -0.8, 1.55, -1, 1.6, 0, -1.1, 0.67]

        self.new_machine_quantity = dict(zip(self.machine_id, [5, 4, 7, 4, 3, 5, 4, 5])) #CMM and TM have very high setup times so one machine more
                                                            # [0, 0, 0, 0, 0, 0, 0, 0]

        self.process_time_old = dict.fromkeys(self.machine_id, 0)
        self.process_time_new = dict.fromkeys(self.machine_id, 0)

        self.OEE_old = dict.fromkeys(self.machine_id, 0)
        self.OEE_new = dict.fromkeys(self.machine_id, 0)

        self.total_machine_time_old = dict.fromkeys(self.machine_id, 0)
        self.total_machine_time_new = dict.fromkeys(self.machine_id, 0)

    def calc_new_values1(self):
        for m in self.machine_id:
            self.total_machine_time_old[m] = self.old_machine_quantity[m]*self.total_time
            self.total_machine_time_new[m] = self.new_machine_quantity[m]*self.total_time

            self.OEE_old[m] = self.process_time_old[m]/self.total_machine_time_old[m]
            self.OEE_new[m] = self.process_time_new[m]/self.total_machine_time_new[m]

available_machines = Available_machines(start_date,end_date)

for j in range(len(ordered_part.process_time)):
    for k, time in enumerate(ordered_part.process_time[j]):
        machine = ordered_part.route[j][k]
        n = ordered_part.total_quantity[j]
        total_time = time * n
        available_machines.process_time_old[machine] += total_time
        available_machines.process_time_new[machine] += total_time
available_machines.calc_new_values1()
print(available_machines.OEE_old)
print(available_machines.OEE_new)
print(available_machines.new_machine_quantity)
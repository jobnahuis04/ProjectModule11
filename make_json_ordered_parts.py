from Classes_setup import *
import pandas as pd
import numpy as np

df = pd.read_csv("./data/Product portfolio.csv")

all_routes = df["Machine routing"]
all_setup_time = df["Setup time (h)"]
all_process_time = df["Process time (h)"]
all_max_transport_batch = df["Max transport batch size (pieces) "]

part_numbers = df["Part number"]
stock_size = df["Size (indicative)"]
price = df["Price per part (€) "]

# start class
ordered_part = OrderedPart()

# simple parameters
ordered_part.part_id = part_numbers.dropna().tolist()
ordered_part.stock_size = stock_size.dropna().tolist()
ordered_part.prize = price.dropna().tolist()

# finding all rows that correspond to a part
index_start_part = [None]*len(ordered_part.part_id)
index_end_part = [None]*len(ordered_part.part_id)

for i in range(1,len(ordered_part.part_id)):
    index_start_part[i-1] = part_numbers[part_numbers == ordered_part.part_id[i-1]].index[0]
    index_end_part[i-1] = part_numbers[part_numbers == ordered_part.part_id[i]].index[0]-1
index_start_part[-1] = part_numbers[part_numbers == ordered_part.part_id[-1]].index[0]
index_end_part[-1] = len(part_numbers)-1

# saving data in class
def save_machining_info_to_class(all_data, class_variable):
    for i in range(len(ordered_part.part_id)):
        data = all_data[index_start_part[i]:index_end_part[i]]
        getattr(ordered_part, class_variable).append(data)
save_machining_info_to_class(all_routes, "route")
save_machining_info_to_class(all_setup_time, "setup_time")
save_machining_info_to_class(all_process_time, "process_time")

def save_first_attribute_to_class(all_data, class_variable):
    for i in range(len(ordered_part.part_id)):
        data = all_data[index_start_part[i]]
        getattr(ordered_part, class_variable).append(data)
save_first_attribute_to_class(all_max_transport_batch, "max_transport_batch")
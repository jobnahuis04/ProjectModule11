from Classes_setup import *
import pandas as pd
import json
from datetime import datetime
import numpy as np

df = pd.read_csv("./data/Product portfolio.csv")

all_routes = df["Machine routing"].tolist()
all_setup_time = df["Setup time (h)"].tolist()
all_process_time = df["Process time (h)"].tolist()
all_max_transport_batch = df["Max transport batch size (pieces) "].tolist()
all_sub_part_id = df["Sub assy number"].tolist()
all_quantity_of_sub_parts = df["Number of sub assy's"].tolist()

part_id = df["Part number"]
stock_size = df["Size (indicative)"]
price = df["Price per part (€) "]

# start class
ordered_part = OrderedPart()

# simple parameters
ordered_part.part_id = part_id.dropna().tolist()
ordered_part.stock_size = stock_size.dropna().tolist()
ordered_part.prize = price.dropna().tolist()

# finding all rows that correspond to a part
index_start_part = [None]*len(ordered_part.part_id)
index_end_part = [None]*len(ordered_part.part_id)

for i in range(1,len(ordered_part.part_id)):
    index_start_part[i-1] = part_id[part_id == ordered_part.part_id[i-1]].index[0]
    index_end_part[i-1] = part_id[part_id == ordered_part.part_id[i]].index[0]
index_start_part[-1] = part_id[part_id == ordered_part.part_id[-1]].index[0]
index_end_part[-1] = len(part_id)

# saving data in class
def save_machining_info_to_class(all_data, class_variable):
    for i in range(len(ordered_part.part_id)):
        data = all_data[index_start_part[i]:index_end_part[i]]
        getattr(ordered_part, class_variable).append(data)
        setattr(ordered_part, class_variable, [[x for x in inner if not pd.isna(x)] for inner in getattr(ordered_part, class_variable)]) # here im removing the NaN, panda's worked nicely


save_machining_info_to_class(all_routes, "route")
save_machining_info_to_class(all_setup_time, "setup_time")
save_machining_info_to_class(all_process_time, "process_time")

def save_first_attribute_to_class(all_data, class_variable):
    for i in range(len(ordered_part.part_id)):
        data = all_data[index_start_part[i]]
        getattr(ordered_part, class_variable).append(data)
save_first_attribute_to_class(all_max_transport_batch, "max_transport_batch")

df_order = pd.read_csv("./data/Order pattern.csv")
order_part_id = df_order["Part number"].tolist()
order_number = df_order["Order number"].tolist()
quantity = df_order["Number of parts"].tolist()
order_date = df_order["Order date"].tolist()
delivery_date = df_order["Desired delivery date"].tolist()

def write_assembly_data_to_class():
    ordered_part.is_main_assembly = [False]*len(ordered_part.part_id)
    ordered_part.is_main_assembly = [p_id.endswith("01") for p_id in ordered_part.part_id]
    save_machining_info_to_class(all_sub_part_id,"sub_part_id")
write_assembly_data_to_class()
print(all_sub_part_id)
def write_order_to_class():
    for part_id in ordered_part.part_id:
        indices_parts = [i for i, x in enumerate(order_part_id) if x == part_id] # finding the indices in the order pattern
        ordered_part.orders.number_of_orders.append(len(indices_parts))

        ordered_part.orders.order_number.append([order_number[i] for i in indices_parts])
        ordered_part.orders.quantity.append([quantity[i] for i in indices_parts])

        matching_quantities = [q for q, s in zip(all_quantity_of_sub_parts, all_sub_part_id) if s == part_id] # comparing the iterating id to the id's in the product portfolio
        ordered_part.orders.quantity_in_assemblies.append(sum(matching_quantities))

        ordered_part.orders.total_quantity.append(sum([quantity[i] for i in indices_parts])+int(sum(matching_quantities)))
        ordered_part.orders.order_date.append([order_date[i] for i in indices_parts])
        ordered_part.orders.delivery_date.append([delivery_date[i] for i in indices_parts])
write_order_to_class()



# --------------------------------------------------------------------------------ChatGPT below
# Recursive converter
def class_to_dict(obj):
    if hasattr(obj, "__dict__"):
        return {k: class_to_dict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, list):
        return [class_to_dict(i) for i in obj]
    else:
        return obj

data_dict = class_to_dict(ordered_part)
#----------------------------------------------------------------------------------------------
with open("./data/ordered_part.json", "w") as f:
    json.dump(data_dict, f, indent=4)

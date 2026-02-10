class Orders:
    def __init__(self):
        self.number_of_orders = []      # done
        self.order_number = []          # done
        self.status = []
        self.order_date = []            # done
        self.delivery_date = []         # done
        self.quantity = []              # done
#        self.used_in_assembly_id = []
class OrderedPart:
    def __init__(self):
        self.part_id = []               # done
        self.price = []                 # done
        self.route = []                 # done
        self.max_transport_batch = []   # done
        self.setup_time = []            # done
        self.process_time = []          # done
        self.idle_time = []             # done
        self.total_machine_time_all_parts = []
        self.stock_size = []            # done
        self.total_quantity = []        # done
        self.total_sub_part_quantity = [] # done
        self.is_main_assembly = []      # done
        self.sub_part_id = []           # done
        self.max_assembly_batch = []
        self.quantity_of_sub_part = []  # done

        self.orders = Orders()

class Machine:
    def __init__(self):
        self.type_of_machine = []
        self.machine_id = []
        self.active_part_id = []
        self.idle_time = []
        self.purchase_cost = []



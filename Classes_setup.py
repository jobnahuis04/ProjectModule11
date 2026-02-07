class Orders:
    def __init__(self):
        self.order_number = []
        self.status = []
        self.order_date = []
        self.delivery_date = []
        self.quantity = []

class OrderedPart:
    def __init__(self):
        self.part_id = []               # done
        self.price = []                 # done
        self.route = []                 # done
        self.max_transport_batch = []   # done
        self.setup_time = []            # done
        self.process_time = []          # done
        self.stock_size = []            # done

        self.is_main_assembly = True
        self.sub_parts_id = []
        self.max_assembly_batch = []
        self.orders = Orders()

    class Machine:
        def __init__(self):
            self.type_of_machine = []
            self.machine_id = []
            self.active_part_id = []
            self.idle_time = []
            self.purchase_cost = []



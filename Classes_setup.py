class OrderedPart:
    def __init__(self):
        self.part_id = []
        self.price = []
        self.route = []
        self.status = []
        self.order_date = []
        self.delivery_date = []
        self.quantity = []
        self.max_transport_batch = []
        self.setup_time = []
        self.process_time = []
        self.stock = []
        self.is_main_assembly = True
        self.sub_parts_id = []

    class Machine:
        def __init__(self):
            self.type_of_machine = []
            self.machine_id = []
            self.active_part_id = []
            self.idle_time = []


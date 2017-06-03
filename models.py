import aerospik


class DataModel:
    def __init__(self, *args, **kwargs):
        self.namespace = kwargs['db_name']
        self.method_meta_set = kwargs['method_meta_set_name']
        self.client = self.create_client()

    def create_client(self):
        try:
            config = {
                'hosts': [('127.0.0.1', 3000)]
            }
            client = aerospike.client(config).connect()
        except Exception as e:
            print("error: {0}".format(e), file=sys.stderr)
            sys.exit(1)
        else:
            return client

    def update_method(self, parent_type, parent_id, method_name, new_data):
        key = (self.namespace, parent_type, parent_id)
        data = self.get_method(parent_type, parent_id, method_name)
        data.update(new_data)
        self.client.put(key, data)

    def insert_method(self, parent_type, parent_id, data):
        key = (self.namespace, parent_type, parent_id)
        self.client.put(key, data)

    def get_method(self, parent_type, parent_id, method_name):
        query = self.client.query(self.namespace, parent_type)
        query.where(predicates.equals('id', parent_id),
                    predicates.equals('method_name', method_name))
        return query.results()

    def get_method_meta(self):
        all_objects = self.client.scan(self.namespace, self.method_meta_set)
        data = all_objects.results()
        return data

import aerospike
import json


class Initializer:
    def __init__(self, *args, **kwargs):
        self.method_path = kwargs['method_path']
        self.award_path = kwargs['award_path']
        self.namespace = kwargs['db_name']
        self.award_key = (self.namespace, 'awards')
        self.method_key = (self.namespace, 'methods')
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

    def run(self):
        raw_awards = self.read_awards()
        raw_methods = self.read_methods()

        for award in raw_awards:
            self.client.put(self.award_key + (award['id'], ), award)
        for method in raw_methods:
            self.client.put(self.method_key + (method['id'], ), method)

    def read_awards(self): 
        with open(self.award_path) as f:
            raw_awards = json.load(f)
        return raw_awards

    def read_methods(self):
        with open(self.method_path) as f:
            raw_methods = json.load(f)
        return raw_methods

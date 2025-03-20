from prometheus_client import start_http_server, Gauge
import psycopg2
import time
import os
import json

class DatabaseConnection:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    def query(self, query):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchone()[0]
        except Exception as e:
            print(f"Database query failed: {e}")
            return None

class Metric:
    def __init__(self, name, description, query, db_connection):
        self.gauge = Gauge(name, description)
        self.query = query
        self.db_connection = db_connection

    def update(self):
        result = self.db_connection.query(self.query)
        if result is not None:
            self.gauge.set(result)
            print(f"Updated {self.gauge._name}: {result}")

class PrometheusExporter:
    def __init__(self, db_connection, metrics=None, port=8000):
        self.db_connection = db_connection
        self.metrics = metrics or []
        self.port = port

    def add_metric(self, name, description, query):
        self.metrics.append(Metric(name, description, query, self.db_connection))

    def load_metrics_from_config(self, config_path):
        try:
            with open(config_path, 'r') as file:
                metrics_config = json.load(file)
                for metric in metrics_config.get('metrics', []):
                    self.add_metric(metric['name'], metric['description'], metric['query'])
                print(f"Loaded {len(metrics_config.get('metrics', []))} metrics from config.")
        except Exception as e:
            print(f"Failed to load metrics from config: {e}")

    def start(self):
        start_http_server(self.port)
        print(f"Prometheus Exporter running on port {self.port}")
        while True:
            for metric in self.metrics:
                metric.update()
            time.sleep(10)

if __name__ == "__main__":
    db_connection = DatabaseConnection(
        dbname=os.environ.get('DB_NAME', 'your_db_name'),
        user=os.environ.get('DB_USER', 'your_username'),
        password=os.environ.get('DB_PASSWORD', 'your_password'),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 5432))
    )

    exporter = PrometheusExporter(db_connection, port=int(os.environ.get('EXPORTER_PORT', 8000)))

    # Load metrics from configmap or file
    config_path = os.environ.get('METRIC_CONFIG_PATH', '/config/metrics.json')
    exporter.load_metrics_from_config(config_path)

    exporter.start()
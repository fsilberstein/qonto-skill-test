import logging

from app import kafka_to_dwh

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    kafka_to_dwh.run()

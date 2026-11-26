import threading
from .train import train_ml_model


def train_async():
    thread = threading.Thread(target=train_ml_model)
    thread.daemon = True
    thread.start()

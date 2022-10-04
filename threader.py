"""
Threading wrapper function to be used as decorator.
"""
import threading


def in_thread(fun):
    """
    Decorator function to run a callable in a thread
    """
    def wrapper(*args, **kwargs):
        t1 = threading.Thread(target=fun, args=args, kwargs=kwargs)
        t1.start()

    return wrapper

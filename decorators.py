import functools
import time

def timer(function):
    """
    Decorator used to print the runtime of a function in seconds.
    To use simply place "@timer" above a function declaration.
    For nanoseconds use perf_counter_ns for start and end times.
    For seconds use perf_counter for start and end times.

    Args:
        function: the name of the function to time
    
    Returns:
        The result of the function the decorator is called on
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        function_value = function(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"{function.__name__} ran in {run_time} seconds")
        return function_value
    return wrapper

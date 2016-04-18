from datetime import datetime


def timed(func):
    """Timing decorator, prints out function name and execution time."""
    def timed_func(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        finish = datetime.now()
        diff = finish - start
        print '\n{0} call took {1} seconds.\n'.format(func.__name__, diff.total_seconds())
        return result
    return timed_func

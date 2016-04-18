from datetime import datetime


def timeit(func):
    """Timing decorator, prints out function name and execution time."""
    def timed(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        finish = datetime.now()
        diff = finish - start
        print '\n', func.__name__, 'call took', diff.total_seconds(), 'seconds.'
        return result
    return timed

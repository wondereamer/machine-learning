
def cached_func(function):
    """ 参数为key，返回为value。 """
    cache = {}
    def wrapper(*args, **kwargs):
        key = args + (kwd_mark,) + tuple(sorted(kwargs.items()))
        if key in cache:
            return cache[key]
        else:
            result = function(*args, **kwargs)
            cache[key] = result
            return result
    return wrapper
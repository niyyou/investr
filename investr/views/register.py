from functools import wraps

register = {}


def declare_view(name):
    def outer_wrapper(func):
        assert name not in register, "The view name exists already."
        register[name] = func

        @wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return outer_wrapper

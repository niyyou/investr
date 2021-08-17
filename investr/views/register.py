from functools import wraps

register = {}


def declare_view(name):
    def outer_wrapper(func):
        assert (
            name not in register
        ), f"The view name exists already. Register: {register}"
        register[name] = func

        @wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return outer_wrapper

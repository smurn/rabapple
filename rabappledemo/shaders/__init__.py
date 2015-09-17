import pkgutil

def load_code(name):
    data = pkgutil.get_data("rabappledemo.shaders", name)
    if data is None:
        raise ValueError("Failed to load %r." % name)
    return data.decode().replace("\r\n", "\n")

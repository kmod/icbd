import functools

registrations = []
loaded = []
modules = {}

def try_load(e, i):
    if loaded[i]:
        return

    f, names = registrations[i]
    args = []
    for module_name, n in names:
        u = modules[module_name].get_name(n)
        if u is None or not u.types():
            return
        args.append(u.types()[0])

    loaded[i] = True
    f(e, *args)

def register(e, f, *names):
    i = len(registrations)
    registrations.append((f, names))
    loaded.append(False)

    for module_name, n in names:
        if module_name not in modules:
            loaded_modules = e.load_modules(module_name, e.python_path)
            assert len(loaded_modules) == len(module_name.split('.'))
            m = loaded_modules[-1]
            modules[module_name] = m
        else:
            m = modules[module_name]

        m.add_name_listener(n, functools.partial(try_load, e, i))

import importlib
import collections
import inspect
import types


Declaration = collections.namedtuple("Declaration", ["name", "value"])


def load_module(pathname: str) -> types.ModuleType:
    try:
        mod_name = inspect.getmodulename(pathname)
        mod = importlib.import_module(mod_name)
    except Exception as e:
        raise ValueError(f'couldn\'t load module at "{pathname}" (reason: "{e}")')
    return mod


def get_top_levels(mod: types.ModuleType) -> list[Declaration]:
    return [
        Declaration(name=tld, value=getattr(mod, tld))
        for tld in mod.__dict__.keys()
        if (tld not in __builtins__.__dict__ and not tld.startswith("_"))
    ]

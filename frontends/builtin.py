import types
import typing
import collections
import inspect
import hawkdoc.doc_entry
import unittest
import importlib
import pprint


def list_callable(c: typing.Callable):
    name = c.__qualname__
    args = []
    sig = inspect.signature(c)
    for param in sig.parameters.values():
        args.append(
            hawkdoc.doc_entry.FieldEntry(
                name=param.name,
                short_desc=None,
                typename=param.annotation.__qualname__
                if param.annotation != inspect.Parameter.empty
                and isinstance(param.annotation, type)
                else None,
            )
        )
    if inspect.isgenerator(c):
        return hawkdoc.doc_entry.GeneratorEntry(
            name=name,
            short_desc=None,
            long_desc=None,
            arguments=args,
            raises=None,
            yields=None,
        )
    else:
        return hawkdoc.doc_entry.FunctionEntry(
            name=name,
            short_desc=None,
            long_desc=None,
            arguments=args,
            raises=None,
            returns=None,
        )


def list_type(t: type):
    static_vars = [
        list_vardecl(getattr(t, name), name)
        for name in dir(t)
        if name[0] != "_"
        and not (
            inspect.ismethod(getattr(t, name))
            or inspect.ismethoddescriptor(getattr(t, name))
        )
    ]
    methods = [
        list_callable(getattr(t, name))
        for name in dir(t)
        if name[0] != "_"
        and (
            inspect.ismethod(getattr(t, name))
            or inspect.ismethoddescriptor(getattr(t, name))
        )
    ]
    return hawkdoc.doc_entry.ClassEntry(
        name=t.__qualname__,
        short_desc=None,
        long_desc=None,
        instance_vars=None,
        static_vars=static_vars,
        methods=methods,
    )


def list_vardecl(o: typing.Any, name: str):
    return hawkdoc.doc_entry.VariableEntry(
        name=name, short_desc=None, value=repr(o), typename=type(o).__qualname__
    )


def gen_listing(mod: types.ModuleType) -> hawkdoc.doc_entry.ModuleEntry:
    tl_names = dir(mod)
    contents = []
    for name in tl_names:
        if name[0] == "_":
            continue
        match getattr(mod, name):
            case type():
                contents.append(list_type(getattr(mod, name)))
            case collections.abc.Callable():
                contents.append(list_callable(getattr(mod, name)))
            case types.ModuleType():
                pass
            case _:
                contents.append(list_vardecl(getattr(mod, name), name))
    return hawkdoc.doc_entry.ModuleEntry(
        name=mod.__name__, short_desc=None, long_desc=None, contents=contents
    )


class TestAll(unittest.TestCase):
    def setUp(self):
        self.mod = importlib.import_module("hawkdoc.frontends.testbed")
        self.listing = gen_listing(self.mod)

    def test_mod_name(self):
        self.assertEqual(self.listing.name, "hawkdoc.frontends.testbed")

    def test_mod_contents(self):
        for tld in self.listing.contents:
            match tld.name:
                case "Declaration":
                    pass
                case "load_module":
                    self.assertEqual(len(tld.arguments), 1)
                    self.assertEqual(tld.arguments[0].name, "pathname")
                    self.assertEqual(tld.arguments[0].typename, "str")
                case "get_top_levels":
                    self.assertEqual(len(tld.arguments), 1)
                    self.assertEqual(tld.arguments[0].name, "mod")
                    self.assertEqual(tld.arguments[0].typename, "module")
                case _:
                    self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()

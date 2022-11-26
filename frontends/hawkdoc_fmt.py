import types
import unittest
import hawkdoc.docstring
import hawkdoc.module


def parse_module_docstring(doc: str) -> tuple[str, str]:
    doc = hawkdoc.docstring.trim(doc).splitlines()
    short_desc = doc[0]
    if len(doc) > 1:
        long_desc = " ".join(doc[1:]).strip()
        return short_desc, long_desc
    else:
        return short_desc, None


def var_decl(
    decl: hawkdoc.module.Declaration, short_desc: str = None
) -> hawkdoc.doc_entry.VariableEntry:
    return hawkdoc.doc_entry.VariableEntry(
        name=decl.name,
        typename=repr(type(decl.value)),
        value=repr(decl.value),
        short_desc=short_desc,
    )


def parse_field(field_desc: str) -> hawkdoc.doc_entry.Field:
    # do some field stripping nyehehehehe
    field_desc = field_desc.strip()
    name, desc = field_desc.split(":", 1)
    desc = desc.replace("\n    ", " ").strip()
    return hawkdoc.doc_entry.Field(name=name, desc=desc, typename=None)


def parse_fields(fields: str) -> list[hawkdoc.doc_entry.Field]:
    result = []
    lines = fields.splitlines()
    cur_field = lines[0]
    for line in lines[1:]:
        if line.startswith("    "):
            cur_field += f"\n{line}"
        elif cur_field:
            result.append(parse_field(cur_field))
            cur_field = line
    if cur_field:
        result.append(parse_field(cur_field))
    return result


def parse_function_docstring(doc: str) -> hawkdoc.doc_entry.FunctionEntry:
    doc = hawkdoc.docstring.trim(doc)
    lines = doc.splitlines()
    short_desc = lines[0]
    lines.pop(0)
    while len(lines) > 0 and not (lines[0] == "" or lines[0].isspace()):
        short_desc += f" {lines[0]}"
        lines.pop(0)

    sections = {
        "LongDesc:": None,
        "Args:": None,
        "Raises:": None,
        "Returns:": None,
    }
    current = "LongDesc:"
    sections[current] = ""
    for line in lines:
        if line in sections:
            sections[current] = hawkdoc.docstring.trim(sections[current])
            sections[line] = ""
            current = line
        else:
            if (line == "" or line.isspace()) and not sections[current].endswith("\n"):
                # coalesce blank lines into a single newline
                sections[current] += "\n"
            elif current == "LongDesc:":
                # don't preserve newlines for the long description
                sections[current] += f" {line}"
            else:
                sections[current] += f"\n{line}"

    # coalesce Nones
    long_desc = sections["LongDesc:"].strip() if sections["LongDesc:"] else None
    args = parse_fields(sections["Args:"]) if sections["Args:"] else None
    raises = parse_fields(sections["Raises:"]) if sections["Raises:"] else None
    returns = (
        sections["Returns:"].strip().replace("\n", " ").replace("\n", "")
        if sections["Returns:"]
        else None
    )

    return hawkdoc.doc_entry.FunctionEntry(
        short_desc=short_desc,
        long_desc=long_desc,
        arguments=args,
        raises=raises,
        returns=returns,
        name=None,
    )


# def callable_decl(decl: hawkdoc.module.Declaration) -> hawkdoc.doc_entry.CallableEntry:
#     sig = inspect.signature(decl)
#     args = set(sig.parameters)


def gen_listing(mod: types.ModuleType) -> hawkdoc.doc_entry.ModuleEntry:
    name = mod.__name__
    if mod.__doc__:
        short_desc, long_desc = parse_module_docstring(mod.__doc__)
    else:
        short_desc, long_desc = None, None

    contents = []
    for tld in hawkdoc.module.get_top_levels(mod):
        if isinstance(tld.value, type):
            pass
            # contents.append(class_decl(tld))
        elif callable(tld.value):
            pass
            # contents.append(callable_decl(tld))
        else:
            contents.append(var_decl(tld))

    return hawkdoc.doc_entry.ModuleEntry(
        name=name, short_desc=short_desc, long_desc=long_desc, contents=contents
    )


# TESTS


class FieldParseTest(unittest.TestCase):
    def test_parse_field(self):
        inputs = [
            "foo: does a thingymadoo",
            "bar: does another thingymadoodle,\n    sorta",
            "hyonk: does yet another thingadoo,\nsorta",
        ]
        expected_outputs = [
            hawkdoc.doc_entry.Field(
                name="foo", typename=None, desc="does a thingymadoo"
            ),
            hawkdoc.doc_entry.Field(
                name="bar", typename=None, desc="does another thingymadoodle, sorta"
            ),
            hawkdoc.doc_entry.Field(
                name="hyonk", typename=None, desc="does yet another thingadoo,\nsorta"
            ),
        ]
        self.assertEqual([parse_field(f) for f in inputs], expected_outputs)

    def test_parse_fields(self):
        input = parse_fields(
            hawkdoc.docstring.trim(
                """
        foo: does a thingymadoo
        baxter: does lots of things
        bar: does another thingymadoodle,
            sorta
        hyonk:
            does yet another thingadoo,
            sorta
        """
            )
        )
        expected_outputs = [
            hawkdoc.doc_entry.Field(
                name="foo", typename=None, desc="does a thingymadoo"
            ),
            hawkdoc.doc_entry.Field(
                name="baxter", typename=None, desc="does lots of things"
            ),
            hawkdoc.doc_entry.Field(
                name="bar", typename=None, desc="does another thingymadoodle, sorta"
            ),
            hawkdoc.doc_entry.Field(
                name="hyonk", typename=None, desc="does yet another thingadoo, sorta"
            ),
        ]
        self.assertEqual(input, expected_outputs)


class FunctionParseTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        def test_example(foo: str, bar: int) -> bool:
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua.

            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua. Fermentum dui faucibus in ornare quam.
            Tempus imperdiet nulla malesuada pellentesque elit eget gravida cum. In nibh mauris
            cursus mattis molestie a. Tincidunt augue interdum velit euismod in pellentesque
            massa placerat. Ipsum suspendisse ultrices gravida dictum fusce ut placerat. Facilisi
            nullam vehicula ipsum a arcu. Eget est lorem ipsum dolor sit amet consectetur
            adipiscing. Curabitur vitae nunc sed velit dignissim. Amet cursus sit amet dictum sit
            amet justo. Sagittis eu volutpat odio facilisis. Donec enim diam vulputate ut pharetra
            sit amet aliquam. Scelerisque varius morbi enim nunc faucibus a pellentesque. Pulvinar
            elementum integer enim neque. Nisi scelerisque eu ultrices vitae auctor eu. Ut eu sem
            integer vitae. Facilisi etiam dignissim diam quis. Porttitor massa id neque aliquam
            vestibulum morbi. Sed lectus vestibulum mattis ullamcorper.

            Args:
                foo: does the thing
                bar: does NOT do the thing
            Returns:
                whether or not the thing was done uwu
            """
            return foo is not None

        self.func = test_example
        self.parsed = parse_function_docstring(
            hawkdoc.docstring.trim(self.func.__doc__)
        )
        self.expected_short_desc = hawkdoc.docstring.trim(
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua."""
        ).replace("\n", " ")
        self.expected_long_desc = hawkdoc.docstring.trim(
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua. Fermentum dui faucibus in ornare quam.
            Tempus imperdiet nulla malesuada pellentesque elit eget gravida cum. In nibh mauris
            cursus mattis molestie a. Tincidunt augue interdum velit euismod in pellentesque
            massa placerat. Ipsum suspendisse ultrices gravida dictum fusce ut placerat. Facilisi
            nullam vehicula ipsum a arcu. Eget est lorem ipsum dolor sit amet consectetur
            adipiscing. Curabitur vitae nunc sed velit dignissim. Amet cursus sit amet dictum sit
            amet justo. Sagittis eu volutpat odio facilisis. Donec enim diam vulputate ut pharetra
            sit amet aliquam. Scelerisque varius morbi enim nunc faucibus a pellentesque. Pulvinar
            elementum integer enim neque. Nisi scelerisque eu ultrices vitae auctor eu. Ut eu sem
            integer vitae. Facilisi etiam dignissim diam quis. Porttitor massa id neque aliquam
            vestibulum morbi. Sed lectus vestibulum mattis ullamcorper."""
        ).replace("\n", " ")
        self.expected_args = [
            hawkdoc.doc_entry.Field(name="foo", desc="does the thing", typename=None),
            hawkdoc.doc_entry.Field(
                name="bar", desc="does NOT do the thing", typename=None
            ),
        ]
        self.expected_returns = "whether or not the thing was done uwu"

    def test_short_desc(self):
        self.assertEqual(self.parsed.short_desc, self.expected_short_desc)

    def test_long_desc(self):
        self.assertEqual(self.parsed.long_desc, self.expected_long_desc)

    def test_args(self):
        self.assertEqual(self.parsed.arguments, self.expected_args)

    def test_returns(self):
        self.assertEqual(self.parsed.returns, self.expected_returns)


if __name__ == "__main__":
    unittest.main()

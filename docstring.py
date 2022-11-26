import sys
import typing


def has_docstring(obj: typing.Any) -> bool:
    return hasattr(obj, "__doc__") and obj.__doc__ is not None


def trim(docstring: str) -> str:
    """Trim docstring, preserving relative indentation

    Normalizes docstrings using code reproduced exactly (save minor formatting differences)
    from the description of docstring indentation handling in PEP 257.

    Args:
        docstring: docstring to be trimmed

    Returns:
        `docstring` normalized according to PEP 257

    References:
        @techreport{pep257,
            author = {David Goodger and Guido van Rossum},
            title  = {Docstring Conventions},
            year   = {2001},
            type   = {PEP},
            number = {257},
            url    = {https://peps.python.org/pep-0257/}
        }
    """
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs(4).splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return "\n".join(trimmed)

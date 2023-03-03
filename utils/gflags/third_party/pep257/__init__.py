#!/usr/bin/env python

def trim(docstring):
    """Removes indentation from triple-quoted strings.

    This is the function specified in PEP 257 to handle docstrings:
        http://www.python.org/dev/peps/pep-0257/
    """
    if not docstring:
        return ''

    # Since Python 3 does not support sys.maxint so we use and arbitrary
    # large integer instead.
    maxint = 1 << 32

    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()

    # Determine minimum indentation (first line doesn't count):
    indent = maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

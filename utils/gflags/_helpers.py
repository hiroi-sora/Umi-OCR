#!/usr/bin/env python
# Copyright 2002 Google Inc. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Helper functions for //gflags."""

import collections
import os
import re
import struct
import sys
import textwrap
try:
    import fcntl  # pylint: disable=g-import-not-at-top
except ImportError:
    fcntl = None
try:
    # Importing termios will fail on non-unix platforms.
    import termios  # pylint: disable=g-import-not-at-top
except ImportError:
    termios = None

# pylint: disable=g-import-not-at-top
import utils.gflags.third_party.pep257 as pep257
import six


_DEFAULT_HELP_WIDTH = 80  # Default width of help output.
_MIN_HELP_WIDTH = 40  # Minimal "sane" width of help output. We assume that any
# value below 40 is unreasonable.

# Define the allowed error rate in an input string to get suggestions.
#
# We lean towards a high threshold because we tend to be matching a phrase,
# and the simple algorithm used here is geared towards correcting word
# spellings.
#
# For manual testing, consider "<command> --list" which produced a large number
# of spurious suggestions when we used "least_errors > 0.5" instead of
# "least_erros >= 0.5".
_SUGGESTION_ERROR_RATE_THRESHOLD = 0.50

# Characters that cannot appear or are highly discouraged in an XML 1.0
# document. (See http://www.w3.org/TR/REC-xml/#charsets or
# https://en.wikipedia.org/wiki/Valid_characters_in_XML#XML_1.0)
_ILLEGAL_XML_CHARS_REGEX = re.compile(
    u'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f\ud800-\udfff\ufffe\uffff]')

# This is a set of module ids for the modules that disclaim key flags.
# This module is explicitly added to this set so that we never consider it to
# define key flag.
disclaim_module_ids = set([id(sys.modules[__name__])])


# Define special flags here so that help may be generated for them.
# NOTE: Please do NOT use SPECIAL_FLAGS from outside flags module.
# Initialized inside flagvalues.py.
SPECIAL_FLAGS = None


class _ModuleObjectAndName(
        collections.namedtuple('_ModuleObjectAndName', 'module module_name')):
    """Module object and name.

    Fields:
    - module: object, module object.
    - module_name: str, module name.
    """


def GetModuleObjectAndName(globals_dict):
    """Returns the module that defines a global environment, and its name.

    Args:
      globals_dict: A dictionary that should correspond to an environment
        providing the values of the globals.

    Returns:
      _ModuleObjectAndName - pair of module object & module name.
      Returns (None, None) if the module could not be identified.
    """
    name = globals_dict.get('__name__', None)
    module = sys.modules.get(name, None)
    # Pick a more informative name for the main module.
    return _ModuleObjectAndName(module,
                                (sys.argv[0] if name == '__main__' else name))


def GetCallingModuleObjectAndName():
    """Returns the module that's calling into this module.

    We generally use this function to get the name of the module calling a
    DEFINE_foo... function.

    Returns:
      The module object that called into this one.

    Raises:
      AssertionError: if no calling module could be identified.
    """
    range_func = range if sys.version_info[0] >= 3 else xrange
    for depth in range_func(1, sys.getrecursionlimit()):
        # sys._getframe is the right thing to use here, as it's the best
        # way to walk up the call stack.
        globals_for_frame = sys._getframe(
            depth).f_globals  # pylint: disable=protected-access
        module, module_name = GetModuleObjectAndName(globals_for_frame)
        if id(module) not in disclaim_module_ids and module_name is not None:
            return _ModuleObjectAndName(module, module_name)
    raise AssertionError('No module was found')


def GetCallingModule():
    """Returns the name of the module that's calling into this module."""
    return GetCallingModuleObjectAndName().module_name


def StrOrUnicode(value):
    """Converts a value to a python string.

    Behavior of this function is intentionally different in Python2/3.

    In Python2, the given value is attempted to convert to a str (byte string).
    If it contains non-ASCII characters, it is converted to a unicode instead.

    In Python3, the given value is always converted to a str (unicode string).

    This behavior reflects the (bad) practice in Python2 to try to represent
    a string as str as long as it contains ASCII characters only.

    Args:
      value: An object to be converted to a string.

    Returns:
      A string representation of the given value. See the description above
      for its type.
    """
    try:
        return str(value)
    except UnicodeEncodeError:
        return unicode(value)  # Python3 should never come here


def CreateXMLDOMElement(doc, name, value):
    """Returns an XML DOM element with name and text value.

    Args:
      doc: A minidom.Document, the DOM document it should create nodes from.
      name: A string, the tag of XML element.
      value: A Python object, whose string representation will be used
        as the value of the XML element. Illegal or highly discouraged xml 1.0
        characters are stripped.

    Returns:
      An instance of minidom.Element.
    """
    s = StrOrUnicode(value)
    if six.PY2 and not isinstance(s, unicode):
        # Get a valid unicode string.
        s = s.decode('utf-8', 'ignore')
    if isinstance(value, bool):
        # Display boolean values as the C++ flag library does: no caps.
        s = s.lower()
    # Remove illegal xml characters.
    s = _ILLEGAL_XML_CHARS_REGEX.sub(u'', s)

    e = doc.createElement(name)
    e.appendChild(doc.createTextNode(s))
    return e


def GetHelpWidth():
    """Returns: an integer, the width of help lines that is used in TextWrap."""
    if not sys.stdout.isatty() or termios is None or fcntl is None:
        return _DEFAULT_HELP_WIDTH
    try:
        data = fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234')
        columns = struct.unpack('hh', data)[1]
        # Emacs mode returns 0.
        # Here we assume that any value below 40 is unreasonable.
        if columns >= _MIN_HELP_WIDTH:
            return columns
        # Returning an int as default is fine, int(int) just return the int.
        return int(os.getenv('COLUMNS', _DEFAULT_HELP_WIDTH))

    except (TypeError, IOError, struct.error):
        return _DEFAULT_HELP_WIDTH


def GetFlagSuggestions(attempt, longopt_list):
    """Get helpful similar matches for an invalid flag."""
    # Don't suggest on very short strings, or if no longopts are specified.
    if len(attempt) <= 2 or not longopt_list:
        return []

    option_names = [v.split('=')[0] for v in longopt_list]

    # Find close approximations in flag prefixes.
    # This also handles the case where the flag is spelled right but ambiguous.
    distances = [(_DamerauLevenshtein(attempt, option[0:len(attempt)]), option)
                 for option in option_names]
    distances.sort(key=lambda t: t[0])

    least_errors, _ = distances[0]
    # Don't suggest excessively bad matches.
    if least_errors >= _SUGGESTION_ERROR_RATE_THRESHOLD * len(attempt):
        return []

    suggestions = []
    for errors, name in distances:
        if errors == least_errors:
            suggestions.append(name)
        else:
            break
    return suggestions


def _DamerauLevenshtein(a, b):
    """Damerau-Levenshtein edit distance from a to b."""
    memo = {}

    def Distance(x, y):
        """Recursively defined string distance with memoization."""
        if (x, y) in memo:
            return memo[x, y]
        if not x:
            d = len(y)
        elif not y:
            d = len(x)
        else:
            d = min(
                Distance(x[1:], y) + 1,  # correct an insertion error
                Distance(x, y[1:]) + 1,  # correct a deletion error
                Distance(x[1:], y[1:]) + (x[0] != y[0]))  # correct a wrong character
            if len(x) >= 2 and len(y) >= 2 and x[0] == y[1] and x[1] == y[0]:
                # Correct a transposition.
                t = Distance(x[2:], y[2:]) + 1
                if d > t:
                    d = t

        memo[x, y] = d
        return d
    return Distance(a, b)


def TextWrap(text, length=None, indent='', firstline_indent=None):
    """Wraps a given text to a maximum line length and returns it.

    It turns lines that only contain whitespace into empty lines, keeps new lines,
    and expands tabs using 4 spaces.

    Args:
      text:             str, Text to wrap.
      length:           int, Maximum length of a line, includes indentation.
                        If this is None then use GetHelpWidth()
      indent:           str, Indent for all but first line.
      firstline_indent: str, Indent for first line; if None, fall back to indent.

    Returns:
      Wrapped text.

    Raises:
      ValueError: if indent or firstline_indent not shorter than length.
    """
    # Get defaults where callee used None
    if length is None:
        length = GetHelpWidth()
    if indent is None:
        indent = ''
    if firstline_indent is None:
        firstline_indent = indent

    if len(indent) >= length:
        raise ValueError('Length of indent exceeds length')
    if len(firstline_indent) >= length:
        raise ValueError('Length of first line indent exceeds length')

    text = text.expandtabs(4)

    result = []
    # Create one wrapper for the first paragraph and one for subsequent
    # paragraphs that does not have the initial wrapping.
    wrapper = textwrap.TextWrapper(
        width=length, initial_indent=firstline_indent, subsequent_indent=indent)
    subsequent_wrapper = textwrap.TextWrapper(
        width=length, initial_indent=indent, subsequent_indent=indent)

    # textwrap does not have any special treatment for newlines. From the docs:
    # "...newlines may appear in the middle of a line and cause strange output.
    # For this reason, text should be split into paragraphs (using
    # str.splitlines() or similar) which are wrapped separately."
    for paragraph in (p.strip() for p in text.splitlines()):
        if paragraph:
            result.extend(wrapper.wrap(paragraph))
        else:
            result.append('')  # Keep empty lines.
        # Replace initial wrapper with wrapper for subsequent paragraphs.
        wrapper = subsequent_wrapper

    return '\n'.join(result)


def FlagDictToArgs(flag_map):
    """Convert a dict of values into process call parameters.

    This method is used to convert a dictionary into a sequence of parameters
    for a binary that parses arguments using this module.

    Args:
      flag_map: a mapping where the keys are flag names (strings).
        values are treated according to their type:
        * If value is None, then only the name is emitted.
        * If value is True, then only the name is emitted.
        * If value is False, then only the name prepended with 'no' is emitted.
        * If value is a string then --name=value is emitted.
        * If value is a collection, this will emit --name=value1,value2,value3.
        * Everything else is converted to string an passed as such.
    Yields:
      sequence of string suitable for a subprocess execution.
    """
    for key, value in six.iteritems(flag_map):
        if value is None:
            yield '--%s' % key
        elif isinstance(value, bool):
            if value:
                yield '--%s' % key
            else:
                yield '--no%s' % key
        elif isinstance(value, (bytes, type(u''))):
            # We don't want strings to be handled like python collections.
            yield '--%s=%s' % (key, value)
        else:
            # Now we attempt to deal with collections.
            try:
                yield '--%s=%s' % (key, ','.join(str(item) for item in value))
            except TypeError:
                # Default case.
                yield '--%s=%s' % (key, value)


def DocToHelp(doc):
    """Takes a __doc__ string and reformats it as help."""

    # Get rid of starting and ending white space. Using lstrip() or even
    # strip() could drop more than maximum of first line and right space
    # of last line.
    doc = doc.strip()

    # Get rid of all empty lines.
    whitespace_only_line = re.compile('^[ \t]+$', re.M)
    doc = whitespace_only_line.sub('', doc)

    # Cut out common space at line beginnings.
    doc = pep257.trim(doc)

    # Just like this module's comment, comments tend to be aligned somehow.
    # In other words they all start with the same amount of white space.
    # 1) keep double new lines;
    # 2) keep ws after new lines if not empty line;
    # 3) all other new lines shall be changed to a space;
    # Solution: Match new lines between non white space and replace with space.
    doc = re.sub(r'(?<=\S)\n(?=\S)', ' ', doc, flags=re.M)

    return doc


def IsRunningTest():
    """Tries to detect whether we are inside of the test."""
    modules = set(sys.modules)
    test_modules = {
        'unittest',
        'unittest2',
        'pytest',
    }
    return bool(test_modules & modules)


# TODO(b/31830082): Migrate all users to PEP8-style methods and remove this.
def define_both_methods(class_name, class_dict, old_name, new_name):  # pylint: disable=invalid-name
    """Function to help CamelCase to PEP8 style class methods migration.

    For any class definition:
        1. Assert it does not define both old and new methods,
           otherwise it does not work.
        2. If it defines the old method, create the same new method.
        3. If it defines the new method, create the same old method.

    Args:
      class_name: the class name.
      class_dict: the class dictionary.
      old_name: old method's name.
      new_name: new method's name.

    Raises:
      AssertionError: raised when the class defines both the old_name and
          new_name.
    """
    assert old_name not in class_dict or new_name not in class_dict, (
        'Class "{}" cannot define both "{}" and "{}" methods.'.format(
            class_name, old_name, new_name))
    if old_name in class_dict:
        class_dict[new_name] = class_dict[old_name]
    elif new_name in class_dict:
        class_dict[old_name] = class_dict[new_name]

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


"""Contains base classes used to parse and convert arguments.

Instead of importing this module directly, it's preferable to import the
flags package and use the aliases defined at the package level.
"""

import csv
import io
import string

import six

from utils.gflags import _helpers


class _ArgumentParserCache(type):
    """Metaclass used to cache and share argument parsers among flags."""

    _instances = {}

    def __new__(mcs, name, bases, dct):
        _helpers.define_both_methods(name, dct, 'Parse', 'parse')
        _helpers.define_both_methods(name, dct, 'Type', 'flag_type')
        _helpers.define_both_methods(name, dct, 'Convert', 'convert')
        return type.__new__(mcs, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        """Returns an instance of the argument parser cls.

        This method overrides behavior of the __new__ methods in
        all subclasses of ArgumentParser (inclusive). If an instance
        for cls with the same set of arguments exists, this instance is
        returned, otherwise a new instance is created.

        If any keyword arguments are defined, or the values in args
        are not hashable, this method always returns a new instance of
        cls.

        Args:
          *args: Positional initializer arguments.
          **kwargs: Initializer keyword arguments.

        Returns:
          An instance of cls, shared or new.
        """
        if kwargs:
            return type.__call__(cls, *args, **kwargs)
        else:
            instances = cls._instances
            key = (cls,) + tuple(args)
            try:
                return instances[key]
            except KeyError:
                # No cache entry for key exists, create a new one.
                return instances.setdefault(key, type.__call__(cls, *args))
            except TypeError:
                # An object in args cannot be hashed, always return
                # a new instance.
                return type.__call__(cls, *args)


class ArgumentParser(six.with_metaclass(_ArgumentParserCache, object)):
    """Base class used to parse and convert arguments.

    The parse() method checks to make sure that the string argument is a
    legal value and convert it to a native type.  If the value cannot be
    converted, it should throw a 'ValueError' exception with a human
    readable explanation of why the value is illegal.

    Subclasses should also define a syntactic_help string which may be
    presented to the user to describe the form of the legal values.

    Argument parser classes must be stateless, since instances are cached
    and shared between flags. Initializer arguments are allowed, but all
    member variables must be derived from initializer arguments only.
    """

    syntactic_help = ''

    def parse(self, argument):
        """Parses the string argument and returns the native value.

        By default it returns its argument unmodified.

        Args:
          argument: string argument passed in the commandline.

        Raises:
          ValueError: Raised when it fails to parse the argument.

        Returns:
          The parsed value in native type.
        """
        return argument

    def flag_type(self):
        """Returns a string representing the type of the flag."""
        return 'string'

    def _custom_xml_dom_elements(self, doc):  # pylint: disable=unused-argument
        """Returns a list of XML DOM elements to add additional flag information.

        Args:
          doc: A minidom.Document, the DOM document it should create nodes from.

        Returns:
          A list of minidom.Element.
        """
        return []


class _ArgumentSerializerMeta(type):

    def __new__(mcs, name, bases, dct):
        _helpers.define_both_methods(name, dct, 'Serialize', 'serialize')
        return type.__new__(mcs, name, bases, dct)


class ArgumentSerializer(six.with_metaclass(_ArgumentSerializerMeta, object)):
    """Base class for generating string representations of a flag value."""

    def serialize(self, value):
        return _helpers.StrOrUnicode(value)


class NumericParser(ArgumentParser):
    """Parser of numeric values.

    Parsed value may be bounded to a given upper and lower bound.
    """

    def is_outside_bounds(self, val):
        return ((self.lower_bound is not None and val < self.lower_bound) or
                (self.upper_bound is not None and val > self.upper_bound))

    def parse(self, argument):
        val = self.convert(argument)
        if self.is_outside_bounds(val):
            raise ValueError('%s is not %s' % (val, self.syntactic_help))
        return val

    def _custom_xml_dom_elements(self, doc):
        elements = []
        if self.lower_bound is not None:
            elements.append(_helpers.CreateXMLDOMElement(
                doc, 'lower_bound', self.lower_bound))
        if self.upper_bound is not None:
            elements.append(_helpers.CreateXMLDOMElement(
                doc, 'upper_bound', self.upper_bound))
        return elements

    def convert(self, argument):
        """Default implementation: always returns its argument unmodified."""
        return argument


class FloatParser(NumericParser):
    """Parser of floating point values.

    Parsed value may be bounded to a given upper and lower bound.
    """
    number_article = 'a'
    number_name = 'number'
    syntactic_help = ' '.join((number_article, number_name))

    def __init__(self, lower_bound=None, upper_bound=None):
        super(FloatParser, self).__init__()
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        sh = self.syntactic_help
        if lower_bound is not None and upper_bound is not None:
            sh = ('%s in the range [%s, %s]' % (sh, lower_bound, upper_bound))
        elif lower_bound == 0:
            sh = 'a non-negative %s' % self.number_name
        elif upper_bound == 0:
            sh = 'a non-positive %s' % self.number_name
        elif upper_bound is not None:
            sh = '%s <= %s' % (self.number_name, upper_bound)
        elif lower_bound is not None:
            sh = '%s >= %s' % (self.number_name, lower_bound)
        self.syntactic_help = sh

    def convert(self, argument):
        """Converts argument to a float; raises ValueError on errors."""
        return float(argument)

    def flag_type(self):
        return 'float'


class IntegerParser(NumericParser):
    """Parser of an integer value.

    Parsed value may be bounded to a given upper and lower bound.
    """
    number_article = 'an'
    number_name = 'integer'
    syntactic_help = ' '.join((number_article, number_name))

    def __init__(self, lower_bound=None, upper_bound=None):
        super(IntegerParser, self).__init__()
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        sh = self.syntactic_help
        if lower_bound is not None and upper_bound is not None:
            sh = ('%s in the range [%s, %s]' % (sh, lower_bound, upper_bound))
        elif lower_bound == 1:
            sh = 'a positive %s' % self.number_name
        elif upper_bound == -1:
            sh = 'a negative %s' % self.number_name
        elif lower_bound == 0:
            sh = 'a non-negative %s' % self.number_name
        elif upper_bound == 0:
            sh = 'a non-positive %s' % self.number_name
        elif upper_bound is not None:
            sh = '%s <= %s' % (self.number_name, upper_bound)
        elif lower_bound is not None:
            sh = '%s >= %s' % (self.number_name, lower_bound)
        self.syntactic_help = sh

    def convert(self, argument):
        if isinstance(argument, str):
            base = 10
            if len(argument) > 2 and argument[0] == '0':
                if argument[1] == 'o':
                    base = 8
                elif argument[1] == 'x':
                    base = 16
            return int(argument, base)
        else:
            return int(argument)

    def flag_type(self):
        return 'int'


class BooleanParser(ArgumentParser):
    """Parser of boolean values."""

    def convert(self, argument):
        """Converts the argument to a boolean; raise ValueError on errors."""
        if isinstance(argument, str):
            if argument.lower() in ['true', 't', '1']:
                return True
            elif argument.lower() in ['false', 'f', '0']:
                return False

        bool_argument = bool(argument)
        if argument == bool_argument:
            # The argument is a valid boolean (True, False, 0, or 1), and not just
            # something that always converts to bool (list, string, int, etc.).
            return bool_argument

        raise ValueError('Non-boolean argument to boolean flag', argument)

    def parse(self, argument):
        val = self.convert(argument)
        return val

    def flag_type(self):
        return 'bool'


class EnumParser(ArgumentParser):
    """Parser of a string enum value (a string value from a given set).

    If enum_values (see below) is not specified, any string is allowed.
    """

    def __init__(self, enum_values=None, case_sensitive=True):
        """Initialize EnumParser.

        Args:
          enum_values: Array of values in the enum.
          case_sensitive: Whether or not the enum is to be case-sensitive.
        """
        super(EnumParser, self).__init__()
        self.enum_values = enum_values
        self.case_sensitive = case_sensitive

    def parse(self, argument):
        """Determine validity of argument and return the correct element of enum.

        If self.enum_values is empty, then all arguments are valid and argument
        will be returned.

        Otherwise, if argument matches an element in enum, then the first
        matching element will be returned.

        Args:
          argument: The supplied flag value.

        Returns:
          The matching element from enum_values, or argument if enum_values is
          empty.

        Raises:
          ValueError: enum_values was non-empty, but argument didn't match
            anything in enum.
        """
        if not self.enum_values:
            return argument
        elif self.case_sensitive:
            if argument not in self.enum_values:
                raise ValueError('value should be one of <%s>' %
                                 '|'.join(self.enum_values))
            else:
                return argument
        else:
            if argument.upper() not in [value.upper() for value in self.enum_values]:
                raise ValueError('value should be one of <%s>' %
                                 '|'.join(self.enum_values))
            else:
                return [value for value in self.enum_values
                        if value.upper() == argument.upper()][0]

    def flag_type(self):
        return 'string enum'


class ListSerializer(ArgumentSerializer):

    def __init__(self, list_sep):
        self.list_sep = list_sep

    def serialize(self, value):
        return self.list_sep.join([_helpers.StrOrUnicode(x) for x in value])


class CsvListSerializer(ArgumentSerializer):

    def __init__(self, list_sep):
        self.list_sep = list_sep

    def serialize(self, value):
        """Serialize a list as a string, if possible, or as a unicode string."""
        if six.PY2:
            # In Python2 csv.writer doesn't accept unicode, so we convert to UTF-8.
            output = io.BytesIO()
            csv.writer(output).writerow(
                [unicode(x).encode('utf-8') for x in value])
            serialized_value = output.getvalue().decode('utf-8').strip()
        else:
            # In Python3 csv.writer expects a text stream.
            output = io.StringIO()
            csv.writer(output).writerow([str(x) for x in value])
            serialized_value = output.getvalue().strip()

        # We need the returned value to be pure ascii or Unicodes so that
        # when the xml help is generated they are usefully encodable.
        return _helpers.StrOrUnicode(serialized_value)


class BaseListParser(ArgumentParser):
    """Base class for a parser of lists of strings.

    To extend, inherit from this class; from the subclass __init__, call

      BaseListParser.__init__(self, token, name)

    where token is a character used to tokenize, and name is a description
    of the separator.
    """

    def __init__(self, token=None, name=None):
        assert name
        super(BaseListParser, self).__init__()
        self._token = token
        self._name = name
        self.syntactic_help = 'a %s separated list' % self._name

    def parse(self, argument):
        if isinstance(argument, list):
            return argument
        elif not argument:
            return []
        else:
            return [s.strip() for s in argument.split(self._token)]

    def flag_type(self):
        return '%s separated list of strings' % self._name


class ListParser(BaseListParser):
    """Parser for a comma-separated list of strings."""

    def __init__(self):
        BaseListParser.__init__(self, ',', 'comma')

    def parse(self, argument):
        """Override to support full CSV syntax."""
        if isinstance(argument, list):
            return argument
        elif not argument:
            return []
        else:
            try:
                return [s.strip() for s in list(csv.reader([argument], strict=True))[0]]
            except csv.Error as e:
                # Provide a helpful report for case like
                #   --listflag="$(printf 'hello,\nworld')"
                # IOW, list flag values containing naked newlines.  This error
                # was previously "reported" by allowing csv.Error to
                # propagate.
                raise ValueError('Unable to parse the value %r as a %s: %s'
                                 % (argument, self.flag_type(), e))

    def _custom_xml_dom_elements(self, doc):
        elements = super(ListParser, self)._custom_xml_dom_elements(doc)
        elements.append(_helpers.CreateXMLDOMElement(
            doc, 'list_separator', repr(',')))
        return elements


class WhitespaceSeparatedListParser(BaseListParser):
    """Parser for a whitespace-separated list of strings."""

    def __init__(self, comma_compat=False):
        """Initializer.

        Args:
          comma_compat: bool - Whether to support comma as an additional separator.
              If false then only whitespace is supported.  This is intended only for
              backwards compatibility with flags that used to be comma-separated.
        """
        self._comma_compat = comma_compat
        name = 'whitespace or comma' if self._comma_compat else 'whitespace'
        BaseListParser.__init__(self, None, name)

    def parse(self, argument):
        """Override to support comma compatibility."""
        if isinstance(argument, list):
            return argument
        elif not argument:
            return []
        else:
            if self._comma_compat:
                argument = argument.replace(',', ' ')
            return argument.split()

    def _custom_xml_dom_elements(self, doc):
        elements = super(WhitespaceSeparatedListParser, self
                         )._custom_xml_dom_elements(doc)
        separators = list(string.whitespace)
        if self._comma_compat:
            separators.append(',')
        separators.sort()
        for sep_char in separators:
            elements.append(_helpers.CreateXMLDOMElement(
                doc, 'list_separator', repr(sep_char)))
        return elements

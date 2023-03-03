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
#
# ---
# Author: Chad Lester
# Contributions by:
#   Amit Patel, Bogdan Cocosel, Daniel Dulitz, Eric Tiedemann,
#   Eric Veach, Laurence Gonsalves, Matthew Springer, Craig Silverstein,
#   Vladimir Rusinov

"""This package is used to define and parse command line flags.

This package defines a *distributed* flag-definition policy: rather than
an application having to define all flags in or near main(), each python
module defines flags that are useful to it.  When one python module
imports another, it gains access to the other's flags.  (This is
implemented by having all modules share a common, global registry object
containing all the flag information.)

Flags are defined through the use of one of the DEFINE_xxx functions.
The specific function used determines how the flag is parsed, checked,
and optionally type-converted, when it's seen on the command line.
"""

import getopt
import os
import re
import sys
import types
import warnings

import six

from utils.gflags import _helpers
from utils.gflags import argument_parser
from utils.gflags import exceptions
# _flag alias is to avoid 'redefined outer name' warnings.
from utils.gflags import flag as _flag
from utils.gflags import flagvalues
from utils.gflags import validators as gflags_validators


# Add current module to disclaimed module ids.
_helpers.disclaim_module_ids.add(id(sys.modules[__name__]))

# Function/class aliases. Lint complains about invalid-name for many of them,
# suppress warning for whole block:
# pylint: disable=invalid-name

# Module exceptions:
# TODO(vrusinov): these should all be renamed to *Error, e.g. IllegalFlagValue
# should be removed in favour of IllegalFlagValueError.
FlagsError = exceptions.Error
Error = exceptions.Error
CantOpenFlagFileError = exceptions.CantOpenFlagFileError
DuplicateFlagError = exceptions.DuplicateFlagError
DuplicateFlagCannotPropagateNoneToSwig = (
    exceptions.DuplicateFlagCannotPropagateNoneToSwig)
IllegalFlagValue = exceptions.IllegalFlagValueError
IllegalFlagValueError = exceptions.IllegalFlagValueError
UnrecognizedFlagError = exceptions.UnrecognizedFlagError
ValidationError = exceptions.ValidationError

# Public functions:
GetHelpWidth = _helpers.GetHelpWidth
TextWrap = _helpers.TextWrap
FlagDictToArgs = _helpers.FlagDictToArgs
DocToHelp = _helpers.DocToHelp

# Public classes:
Flag = _flag.Flag
BooleanFlag = _flag.BooleanFlag
EnumFlag = _flag.EnumFlag
MultiFlag = _flag.MultiFlag

FlagValues = flagvalues.FlagValues
ArgumentParser = argument_parser.ArgumentParser
BooleanParser = argument_parser.BooleanParser
EnumParser = argument_parser.EnumParser
ArgumentSerializer = argument_parser.ArgumentSerializer
FloatParser = argument_parser.FloatParser
IntegerParser = argument_parser.IntegerParser
BaseListParser = argument_parser.BaseListParser
ListParser = argument_parser.ListParser
ListSerializer = argument_parser.ListSerializer
CsvListSerializer = argument_parser.CsvListSerializer
WhitespaceSeparatedListParser = argument_parser.WhitespaceSeparatedListParser

# pylint: enable=invalid-name


# The global FlagValues instance
FLAGS = FlagValues()


# Flags validators


def register_validator(flag_name,
                       checker,
                       message='Flag validation failed',
                       flag_values=FLAGS):
    """Adds a constraint, which will be enforced during program execution.

    The constraint is validated when flags are initially parsed, and after each
    change of the corresponding flag's value.
    Args:
      flag_name: str, Name of the flag to be checked.
      checker: callable, A function to validate the flag.
        input - A single positional argument: The value of the corresponding
          flag (string, boolean, etc.  This value will be passed to checker
          by the library).
        output - Boolean.
          Must return True if validator constraint is satisfied.
          If constraint is not satisfied, it should either return False or
            raise gflags.ValidationError(desired_error_message).
      message: Error text to be shown to the user if checker returns False.
        If checker raises gflags.ValidationError, message from the raised
          Error will be shown.
      flag_values: An optional FlagValues instance to validate against.
    Raises:
      AttributeError: If flag_name is not registered as a valid flag name.
    """
    v = gflags_validators.SingleFlagValidator(flag_name, checker, message)
    _add_validator(flag_values, v)


def validator(flag_name, message='Flag validation failed', flag_values=FLAGS):
    """A function decorator for defining a flag validator.

    Registers the decorated function as a validator for flag_name, e.g.

    @gflags.validator('foo')
    def _CheckFoo(foo):
      ...

    See register_validator() for the specification of checker function.

    Args:
      flag_name: string, name of the flag to be checked.
      message: error text to be shown to the user if checker returns False.
        If checker raises gflags.ValidationError, message from the raised
          Error will be shown.
      flag_values: FlagValues
    Returns:
      A function decorator that registers its function argument as a validator.
    Raises:
      AttributeError: if flag_name is not registered as a valid flag name.
    """

    def decorate(function):
        register_validator(flag_name, function,
                           message=message,
                           flag_values=flag_values)
        return function
    return decorate


def register_multi_flags_validator(flag_names,
                                   multi_flags_checker,
                                   message='Flags validation failed',
                                   flag_values=FLAGS):
    """Adds a constraint to multiple flags.

    The constraint is validated when flags are initially parsed, and after each
    change of the corresponding flag's value.

    Args:
      flag_names: [str], a list of the flag names to be checked.
      multi_flags_checker: callable, a function to validate the flag.
          input - dictionary, with keys() being flag_names, and value for each key
              being the value of the corresponding flag (string, boolean, etc).
          output - Boolean. Must return True if validator constraint is satisfied.
              If constraint is not satisfied, it should either return False or
              raise gflags.ValidationError.
      message: Error text to be shown to the user if checker returns False.
          If checker raises gflags.ValidationError, message from the raised error
          will be shown.
      flag_values: An optional FlagValues instance to validate against.

    Raises:
      AttributeError: If a flag is not registered as a valid flag name.
    """
    v = gflags_validators.MultiFlagsValidator(
        flag_names, multi_flags_checker, message)
    _add_validator(flag_values, v)


def multi_flags_validator(flag_names,
                          message='Flag validation failed',
                          flag_values=FLAGS):
    """A function decorator for defining a multi-flag validator.

    Registers the decorated function as a validator for flag_names, e.g.

    @gflags.multi_flags_validator(['foo', 'bar'])
    def _CheckFooBar(flags_dict):
      ...

    See register_multi_flags_validator() for the specification of checker
    function.

    Args:
      flag_names: [str], a list of the flag names to be checked.
      message: error text to be shown to the user if checker returns False.
          If checker raises ValidationError, message from the raised
          error will be shown.
      flag_values: An optional FlagValues instance to validate against.

    Returns:
      A function decorator that registers its function argument as a validator.

    Raises:
      AttributeError: If a flag is not registered as a valid flag name.
    """

    def decorate(function):
        register_multi_flags_validator(flag_names,
                                       function,
                                       message=message,
                                       flag_values=flag_values)
        return function

    return decorate


def mark_flag_as_required(flag_name, flag_values=FLAGS):
    """Ensures that flag is not None during program execution.

    Registers a flag validator, which will follow usual validator rules.
    Important note: validator will pass for any non-None value, such as False,
    0 (zero), '' (empty string) and so on.

    It is recommended to call this method like this:

      if __name__ == '__main__':
        gflags.mark_flag_as_required('your_flag_name')
        app.run()

    Because validation happens at app.run() we want to ensure required-ness
    is enforced at that time.  However, you generally do not want to force
    users who import your code to have additional required flags for their
    own binaries or tests.

    Args:
      flag_name: string, name of the flag
      flag_values: FlagValues
    Raises:
      AttributeError: if flag_name is not registered as a valid flag name.
    """
    if flag_values[flag_name].default is not None:
        # TODO(vrusinov): Turn this warning into an exception.
        warnings.warn(
            'Flag %s has a non-None default value; therefore, '
            'mark_flag_as_required will pass even if flag is not specified in the '
            'command line!' % flag_name)
    register_validator(flag_name,
                       lambda value: value is not None,
                       message='Flag --%s must be specified.' % flag_name,
                       flag_values=flag_values)


def mark_flags_as_required(flag_names, flag_values=FLAGS):
    """Ensures that flags are not None during program execution.

    Recommended usage:

      if __name__ == '__main__':
        gflags.mark_flags_as_required(['flag1', 'flag2', 'flag3'])
        app.run()

    Args:
      flag_names: list/tuple, names of the flags.
      flag_values: FlagValues
    Raises:
      AttributeError: If any of flag name has not already been defined as a flag.
    """
    for flag_name in flag_names:
        mark_flag_as_required(flag_name, flag_values)


def mark_flags_as_mutual_exclusive(flag_names, required=False,
                                   flag_values=FLAGS):
    """Ensures that only one flag among flag_names is set.

    Args:
      flag_names: [str], a list of the flag names to be checked.
      required: Boolean, if set, exactly one of the flags must be set.
          Otherwise, it is also valid for none of the flags to be set.
      flag_values: An optional FlagValues instance to validate against.
    """

    def validate_mutual_exclusion(flags_dict):
        flag_count = sum(1 for val in flags_dict.values() if val is not None)
        if flag_count == 1 or (not required and flag_count == 0):
            return True
        message = ('%s one of (%s) must be specified.' %
                   ('Exactly' if required else 'At most', ', '.join(flag_names)))
        raise ValidationError(message)

    register_multi_flags_validator(
        flag_names, validate_mutual_exclusion, flag_values=flag_values)


def _add_validator(fv, validator_instance):
    """Register new flags validator to be checked.

    Args:
      fv: flagvalues.FlagValues
      validator_instance: validators.Validator
    Raises:
      KeyError: if validators work with a non-existing flag.
    """
    for flag_name in validator_instance.get_flags_names():
        fv[flag_name].validators.append(validator_instance)


def _register_bounds_validator_if_needed(parser, name, flag_values):
    """Enforces lower and upper bounds for numeric flags.

    Args:
      parser: NumericParser (either FloatParser or IntegerParser). Provides lower
        and upper bounds, and help text to display.
      name: string, name of the flag
      flag_values: FlagValues
    """
    if parser.lower_bound is not None or parser.upper_bound is not None:

        def checker(value):
            if value is not None and parser.is_outside_bounds(value):
                message = '%s is not %s' % (value, parser.syntactic_help)
                raise ValidationError(message)
            return True

        register_validator(name, checker, flag_values=flag_values)


# The DEFINE functions are explained in more details in the module doc string.


def DEFINE(parser, name, default, help, flag_values=FLAGS, serializer=None,  # pylint: disable=redefined-builtin,invalid-name
           module_name=None, **args):
    """Registers a generic Flag object.

    NOTE: in the docstrings of all DEFINE* functions, "registers" is short
    for "creates a new flag and registers it".

    Auxiliary function: clients should use the specialized DEFINE_<type>
    function instead.

    Args:
      parser: ArgumentParser that is used to parse the flag arguments.
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      serializer: ArgumentSerializer that serializes the flag value.
      module_name: A string, the name of the Python module declaring this flag.
          If not provided, it will be computed using the stack trace of this call.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    DEFINE_flag(Flag(parser, serializer, name, default, help, **args),
                flag_values, module_name)


def DEFINE_flag(flag, flag_values=FLAGS, module_name=None):  # pylint: disable=g-bad-name
    """Registers a 'Flag' object with a 'FlagValues' object.

    By default, the global FLAGS 'FlagValue' object is used.

    Typical users will use one of the more specialized DEFINE_xxx
    functions, such as DEFINE_string or DEFINE_integer.  But developers
    who need to create Flag objects themselves should use this function
    to register their flags.

    Args:
      flag: A Flag object, a flag that is key to the module.
      flag_values: FlagValues object with which the flag will be registered.
      module_name: A string, the name of the Python module declaring this flag.
          If not provided, it will be computed using the stack trace of this call.
    """
    # copying the reference to flag_values prevents pychecker warnings
    fv = flag_values
    fv[flag.name] = flag
    # Tell flag_values who's defining the flag.
    if isinstance(flag_values, FlagValues):
        # Regarding the above isinstance test: some users pass funny
        # values of flag_values (e.g., {}) in order to avoid the flag
        # registration (in the past, there used to be a flag_values ==
        # FLAGS test here) and redefine flags with the same name (e.g.,
        # debug).  To avoid breaking their code, we perform the
        # registration only if flag_values is a real FlagValues object.
        if module_name:
            module = sys.modules.get(module_name)
        else:
            module, module_name = _helpers.GetCallingModuleObjectAndName()
        # TODO(vrusinov): _RegisterFlagByModule* should be public.
        # pylint: disable=protected-access
        flag_values._RegisterFlagByModule(module_name, flag)
        flag_values._RegisterFlagByModuleId(id(module), flag)
        # pylint: enable=protected-access


def _internal_declare_key_flags(flag_names,
                                flag_values=FLAGS, key_flag_values=None):
    """Declares a flag as key for the calling module.

    Internal function.  User code should call DECLARE_key_flag or
    ADOPT_module_key_flags instead.

    Args:
      flag_names: A list of strings that are names of already-registered
        Flag objects.
      flag_values: A FlagValues object that the flags listed in
        flag_names have registered with (the value of the flag_values
        argument from the DEFINE_* calls that defined those flags).
        This should almost never need to be overridden.
      key_flag_values: A FlagValues object that (among possibly many
        other things) keeps track of the key flags for each module.
        Default None means "same as flag_values".  This should almost
        never need to be overridden.

    Raises:
      UnrecognizedFlagError: when we refer to a flag that was not
        defined yet.
    """
    key_flag_values = key_flag_values or flag_values

    module = _helpers.GetCallingModule()

    for flag_name in flag_names:
        flag = flag_values.GetFlag(flag_name)
        # TODO(vrusinov): _RegisterKeyFlagForModule should be public.
        key_flag_values._RegisterKeyFlagForModule(
            module, flag)  # pylint: disable=protected-access


def DECLARE_key_flag(  # pylint: disable=g-bad-name
        flag_name, flag_values=FLAGS):
    """Declares one flag as key to the current module.

    Key flags are flags that are deemed really important for a module.
    They are important when listing help messages; e.g., if the
    --helpshort command-line flag is used, then only the key flags of the
    main module are listed (instead of all flags, as in the case of
    --helpfull).

    Sample usage:

      gflags.DECLARE_key_flag('flag_1')

    Args:
      flag_name: A string, the name of an already declared flag.
        (Redeclaring flags as key, including flags implicitly key
        because they were declared in this module, is a no-op.)
      flag_values: A FlagValues object.  This should almost never
        need to be overridden.
    """
    if flag_name in _helpers.SPECIAL_FLAGS:
        # Take care of the special flags, e.g., --flagfile, --undefok.
        # These flags are defined in _SPECIAL_FLAGS, and are treated
        # specially during flag parsing, taking precedence over the
        # user-defined flags.
        _internal_declare_key_flags([flag_name],
                                    flag_values=_helpers.SPECIAL_FLAGS,
                                    key_flag_values=flag_values)
        return
    _internal_declare_key_flags([flag_name], flag_values=flag_values)


def ADOPT_module_key_flags(  # pylint: disable=g-bad-name
        module, flag_values=FLAGS):
    """Declares that all flags key to a module are key to the current module.

    Args:
      module: A module object.
      flag_values: A FlagValues object.  This should almost never need
        to be overridden.

    Raises:
      Error: When given an argument that is a module name (a
      string), instead of a module object.
    """
    if not isinstance(module, types.ModuleType):
        raise Error('Expected a module object, not %r.' % (module,))
    # TODO(vrusinov): _GetKeyFlagsForModule should be public.
    _internal_declare_key_flags(
        [f.name for f in flag_values._GetKeyFlagsForModule(
            module.__name__)],  # pylint: disable=protected-access
        flag_values=flag_values)
    # If module is this flag module, take _helpers._SPECIAL_FLAGS into account.
    if module == _helpers.GetModuleObjectAndName(globals())[0]:
        _internal_declare_key_flags(
            # As we associate flags with _GetCallingModuleObjectAndName(), the
            # special flags defined in this module are incorrectly registered with
            # a different module.  So, we can't use _GetKeyFlagsForModule.
            # Instead, we take all flags from _helpers._SPECIAL_FLAGS (a private
            # FlagValues, where no other module should register flags).
            [f.name for f in six.itervalues(
                _helpers.SPECIAL_FLAGS.FlagDict())],
            flag_values=_helpers.SPECIAL_FLAGS,
            key_flag_values=flag_values)


def DISCLAIM_key_flags():  # pylint: disable=g-bad-name
    """Declares that the current module will not define any more key flags.

    Normally, the module that calls the DEFINE_xxx functions claims the
    flag to be its key flag.  This is undesirable for modules that
    define additional DEFINE_yyy functions with its own flag parsers and
    serializers, since that module will accidentally claim flags defined
    by DEFINE_yyy as its key flags.  After calling this function, the
    module disclaims flag definitions thereafter, so the key flags will
    be correctly attributed to the caller of DEFINE_yyy.

    After calling this function, the module will not be able to define
    any more flags.  This function will affect all FlagValues objects.
    """
    globals_for_caller = sys._getframe(
        1).f_globals  # pylint: disable=protected-access
    module, _ = _helpers.GetModuleObjectAndName(globals_for_caller)
    _helpers.disclaim_module_ids.add(id(module))


#
# STRING FLAGS
#


def DEFINE_string(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, flag_values=FLAGS, **args):
    """Registers a flag whose value can be any string."""
    parser = ArgumentParser()
    serializer = ArgumentSerializer()
    DEFINE(parser, name, default, help, flag_values, serializer, **args)


def DEFINE_boolean(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, flag_values=FLAGS, module_name=None, **args):
    """Registers a boolean flag.

    Such a boolean flag does not take an argument.  If a user wants to
    specify a false value explicitly, the long option beginning with 'no'
    must be used: i.e. --noflag

    This flag will have a value of None, True or False.  None is possible
    if default=None and the user does not specify the flag on the command
    line.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      module_name: A string, the name of the Python module declaring this flag.
          If not provided, it will be computed using the stack trace of this call.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    DEFINE_flag(BooleanFlag(name, default, help, **args),
                flag_values, module_name)


# Match C++ API to unconfuse C++ people.
DEFINE_bool = DEFINE_boolean  # pylint: disable=g-bad-name


def DEFINE_float(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, lower_bound=None, upper_bound=None,
        flag_values=FLAGS, **args):   # pylint: disable=g-bad-name
    """Registers a flag whose value must be a float.

    If lower_bound or upper_bound are set, then this flag must be
    within the given range.

    Args:
      name: str, flag name.
      default: float, default flag value.
      help: str, help message.
      lower_bound: float, min value of the flag.
      upper_bound: float, max value of the flag.
      flag_values: FlagValues object with which the flag will be registered.
      **args: additional arguments to pass to DEFINE.
    """
    parser = FloatParser(lower_bound, upper_bound)
    serializer = ArgumentSerializer()
    DEFINE(parser, name, default, help, flag_values, serializer, **args)
    _register_bounds_validator_if_needed(parser, name, flag_values=flag_values)


def DEFINE_integer(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, lower_bound=None, upper_bound=None,
        flag_values=FLAGS, **args):
    """Registers a flag whose value must be an integer.

    If lower_bound, or upper_bound are set, then this flag must be
    within the given range.

    Args:
      name: str, flag name.
      default: int, default flag value.
      help: str, help message.
      lower_bound: int, min value of the flag.
      upper_bound: int, max value of the flag.
      flag_values: FlagValues object with which the flag will be registered.
      **args: additional arguments to pass to DEFINE.
    """
    parser = IntegerParser(lower_bound, upper_bound)
    serializer = ArgumentSerializer()
    DEFINE(parser, name, default, help, flag_values, serializer, **args)
    _register_bounds_validator_if_needed(parser, name, flag_values=flag_values)


def DEFINE_enum(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, enum_values, help, flag_values=FLAGS, module_name=None,
        **args):
    """Registers a flag whose value can be any string from enum_values.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      enum_values: A list of strings with the possible values for the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      module_name: A string, the name of the Python module declaring this flag.
          If not provided, it will be computed using the stack trace of this call.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    DEFINE_flag(EnumFlag(name, default, help, enum_values, ** args),
                flag_values, module_name)


def DEFINE_list(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, flag_values=FLAGS, **args):
    """Registers a flag whose value is a comma-separated list of strings.

    The flag value is parsed with a CSV parser.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    parser = ListParser()
    serializer = CsvListSerializer(',')
    DEFINE(parser, name, default, help, flag_values, serializer, **args)


def DEFINE_spaceseplist(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, comma_compat=False, flag_values=FLAGS, **args):
    """Registers a flag whose value is a whitespace-separated list of strings.

    Any whitespace can be used as a separator.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      comma_compat: bool - Whether to support comma as an additional separator.
          If false then only whitespace is supported.  This is intended only for
          backwards compatibility with flags that used to be comma-separated.
      flag_values: FlagValues object with which the flag will be registered.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    parser = WhitespaceSeparatedListParser(comma_compat=comma_compat)
    serializer = ListSerializer(' ')
    DEFINE(parser, name, default, help, flag_values, serializer, **args)


def DEFINE_multi(  # pylint: disable=g-bad-name,redefined-builtin
        parser, serializer, name, default, help, flag_values=FLAGS,
        module_name=None, **args):
    """Registers a generic MultiFlag that parses its args with a given parser.

    Auxiliary function.  Normal users should NOT use it directly.

    Developers who need to create their own 'Parser' classes for options
    which can appear multiple times can call this module function to
    register their flags.

    Args:
      parser: ArgumentParser that is used to parse the flag arguments.
      serializer: ArgumentSerializer that serializes the flag value.
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      module_name: A string, the name of the Python module declaring this flag.
          If not provided, it will be computed using the stack trace of this call.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    DEFINE_flag(MultiFlag(parser, serializer, name, default, help, **args),
                flag_values, module_name)


def DEFINE_multistring(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, flag_values=FLAGS, **args):
    """Registers a flag whose value can be a list of any strings.

    Use the flag on the command line multiple times to place multiple
    string values into the list.  The 'default' may be a single string
    (which will be converted into a single-element list) or a list of
    strings.


    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    parser = ArgumentParser()
    serializer = ArgumentSerializer()
    DEFINE_multi(parser, serializer, name, default, help, flag_values, **args)


def DEFINE_multi_int(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, lower_bound=None, upper_bound=None,
        flag_values=FLAGS, **args):
    """Registers a flag whose value can be a list of arbitrary integers.

    Use the flag on the command line multiple times to place multiple
    integer values into the list.  The 'default' may be a single integer
    (which will be converted into a single-element list) or a list of
    integers.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      lower_bound: int, min values of the flag.
      upper_bound: int, max values of the flag.
      flag_values: FlagValues object with which the flag will be registered.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    parser = IntegerParser(lower_bound, upper_bound)
    serializer = ArgumentSerializer()
    DEFINE_multi(parser, serializer, name, default, help, flag_values, **args)


def DEFINE_multi_float(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, help, lower_bound=None, upper_bound=None,
        flag_values=FLAGS, **args):
    """Registers a flag whose value can be a list of arbitrary floats.

    Use the flag on the command line multiple times to place multiple
    float values into the list.  The 'default' may be a single float
    (which will be converted into a single-element list) or a list of
    floats.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      help: A help string.
      lower_bound: float, min values of the flag.
      upper_bound: float, max values of the flag.
      flag_values: FlagValues object with which the flag will be registered.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    parser = FloatParser(lower_bound, upper_bound)
    serializer = ArgumentSerializer()
    DEFINE_multi(parser, serializer, name, default, help, flag_values, **args)


def DEFINE_multi_enum(  # pylint: disable=g-bad-name,redefined-builtin
        name, default, enum_values, help, flag_values=FLAGS, case_sensitive=True,
        **args):
    """Registers a flag whose value can be a list strings from enum_values.

    Use the flag on the command line multiple times to place multiple
    enum values into the list.  The 'default' may be a single string
    (which will be converted into a single-element list) or a list of
    strings.

    Args:
      name: A string, the flag name.
      default: The default value of the flag.
      enum_values: A list of strings with the possible values for the flag.
      help: A help string.
      flag_values: FlagValues object with which the flag will be registered.
      case_sensitive: Whether or not the enum is to be case-sensitive.
      **args: Dictionary with extra keyword args that are passed to the
          Flag __init__.
    """
    parser = EnumParser(enum_values, case_sensitive)
    serializer = ArgumentSerializer()
    DEFINE_multi(parser, serializer, name, default, help, flag_values, **args)


def DEFINE_alias(name, original_name, flag_values=FLAGS, module_name=None):  # pylint: disable=g-bad-name
    """Defines an alias flag for an existing one.

    Args:
      name: A string, name of the alias flag.
      original_name: A string, name of the original flag.
      flag_values: FlagValues object with which the flag will be registered.
      module_name: A string, the name of the module that defines this flag.

    Raises:
      gflags.FlagError:
        UnrecognizedFlagError: if the referenced flag doesn't exist.
        DuplicateFlagError: if the alias name has been used by some existing flag.
    """
    if original_name not in flag_values:
        raise UnrecognizedFlagError(original_name)
    flag = flag_values[original_name]

    class _Parser(ArgumentParser):
        """The parser for the alias flag calls the original flag parser."""

        def parse(self, argument):
            flag.parse(argument)
            return flag.value

    class _FlagAlias(Flag):
        """Overrides Flag class so alias value is copy of original flag value."""

        @property
        def value(self):
            return flag.value

        @value.setter
        def value(self, value):
            flag.value = value

    help_msg = 'Alias for --%s.' % flag.name
    # If alias_name has been used, gflags.DuplicatedFlag will be raised.
    DEFINE_flag(_FlagAlias(_Parser(), flag.serializer, name, flag.default,
                           help_msg, boolean=flag.boolean),
                flag_values, module_name)


DEFINE_string(
    'flagfile', '',
    'Insert flag definitions from the given file into the command line.',
    _helpers.SPECIAL_FLAGS)

DEFINE_string(
    'undefok', '',
    'comma-separated list of flag names that it is okay to specify '
    'on the command line even if the program does not define a flag '
    'with that name.  IMPORTANT: flags in this list that have '
    'arguments MUST use the --flag=value format.', _helpers.SPECIAL_FLAGS)


# Old CamelCase functions. It's OK to use them, but those use cases will be
# migrated to PEP8 style functions in the future.
# pylint: disable=invalid-name
RegisterValidator = register_validator
Validator = validator
RegisterMultiFlagsValidator = register_multi_flags_validator
MultiFlagsValidator = multi_flags_validator
MarkFlagAsRequired = mark_flag_as_required
MarkFlagsAsRequired = mark_flags_as_required
MarkFlagsAsMutualExclusive = mark_flags_as_mutual_exclusive
# pylint: enable=invalid-name

# New PEP8 style functions.
get_help_width = GetHelpWidth
text_wrap = TextWrap
flag_dict_to_args = FlagDictToArgs
doc_to_help = DocToHelp
declare_key_flag = DECLARE_key_flag
adopt_module_key_flags = ADOPT_module_key_flags
disclaim_key_flags = DISCLAIM_key_flags

# New API names, they are more consistent with each other.
DEFINE_multi_string = DEFINE_multistring
DEFINE_multi_integer = DEFINE_multi_int

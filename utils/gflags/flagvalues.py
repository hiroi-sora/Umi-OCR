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

"""Flagvalues module - Registry of 'Flag' objects.

Instead of importing this module directly, it's preferable to import the
flags package and use the aliases defined at the package level.
"""

import hashlib
import logging
import os
import struct
import sys
import traceback
import warnings
from xml.dom import minidom

import six

from utils.gflags import _helpers
from utils.gflags import exceptions
from utils.gflags import flag as _flag

# Add flagvalues module to disclaimed module ids.
_helpers.disclaim_module_ids.add(id(sys.modules[__name__]))

# The MOE directives in this file cause the docstring indentation
# linter to go nuts.
# pylint: disable=g-doc-bad-indent

# Environment variable that controls whether to allow unparsed flag access.
# Do not rely on, it will be removed later.
_UNPARSED_FLAG_ACCESS_ENV_NAME = 'GFLAGS_ALLOW_UNPARSED_FLAG_ACCESS'

# Percentage of the flag names for which unparsed flag access will fail by
# default.
_UNPARSED_ACCESS_DISABLED_PERCENT = 0

# b/32278439 will change flag parsing to use GNU-style scanning by default.
# This environment variable allows users to force setting the default parsing
# style. Do NOT rely on it. It will be removed as part of b/32278439.
_USE_GNU_GET_OPT_ENV_NAME = 'GFLAGS_USE_GNU_GET_OPT'


class FlagValues(object):
    """Registry of 'Flag' objects.

    A 'FlagValues' can then scan command line arguments, passing flag
    arguments through to the 'Flag' objects that it owns.  It also
    provides easy access to the flag values.  Typically only one
    'FlagValues' object is needed by an application: gflags.FLAGS

    This class is heavily overloaded:

    'Flag' objects are registered via __setitem__:
         FLAGS['longname'] = x   # register a new flag

    The .value attribute of the registered 'Flag' objects can be accessed
    as attributes of this 'FlagValues' object, through __getattr__.  Both
    the long and short name of the original 'Flag' objects can be used to
    access its value:
         FLAGS.longname          # parsed flag value
         FLAGS.x                 # parsed flag value (short name)

    Command line arguments are scanned and passed to the registered 'Flag'
    objects through the __call__ method.  Unparsed arguments, including
    argv[0] (e.g. the program name) are returned.
         argv = FLAGS(sys.argv)  # scan command line arguments

    The original registered Flag objects can be retrieved through the use
    of the dictionary-like operator, __getitem__:
         x = FLAGS['longname']   # access the registered Flag object

    The str() operator of a 'FlagValues' object provides help for all of
    the registered 'Flag' objects.
    """

    def __init__(self):
        # Since everything in this class is so heavily overloaded, the only
        # way of defining and using fields is to access __dict__ directly.

        # Dictionary: flag name (string) -> Flag object.
        self.__dict__['__flags'] = {}

        # Set: name of hidden flag (string).
        # Holds flags that should not be directly accessible from Python.
        self.__dict__['__hiddenflags'] = set()

        # Dictionary: module name (string) -> list of Flag objects that are defined
        # by that module.
        self.__dict__['__flags_by_module'] = {}
        # Dictionary: module id (int) -> list of Flag objects that are defined by
        # that module.
        self.__dict__['__flags_by_module_id'] = {}
        # Dictionary: module name (string) -> list of Flag objects that are
        # key for that module.
        self.__dict__['__key_flags_by_module'] = {}

        # Bool: True if flags were parsed.
        self.__dict__['__flags_parsed'] = False

        # Bool: True if Reset() was called.
        self.__dict__['__reset_called'] = False

        # None or Method(name, value) to call from __setattr__ for an unknown flag.
        self.__dict__['__set_unknown'] = None

        if _USE_GNU_GET_OPT_ENV_NAME in os.environ:
            self.__dict__['__use_gnu_getopt'] = (
                os.environ[_USE_GNU_GET_OPT_ENV_NAME] == '1')
        else:
            # By default don't use the GNU-style scanning when parsing the args.
            self.__dict__['__use_gnu_getopt'] = False

    def UseGnuGetOpt(self, use_gnu_getopt=True):
        """Use GNU-style scanning. Allows mixing of flag and non-flag arguments.

        See http://docs.python.org/library/getopt.html#getopt.gnu_getopt

        Args:
          use_gnu_getopt: wether or not to use GNU style scanning.
        """
        self.__dict__['__use_gnu_getopt'] = use_gnu_getopt

    def IsGnuGetOpt(self):
        return self.__dict__['__use_gnu_getopt']

    def FlagDict(self):
        return self.__dict__['__flags']

    def FlagsByModuleDict(self):
        """Returns the dictionary of module_name -> list of defined flags.

        Returns:
          A dictionary.  Its keys are module names (strings).  Its values
          are lists of Flag objects.
        """
        return self.__dict__['__flags_by_module']

    def FlagsByModuleIdDict(self):
        """Returns the dictionary of module_id -> list of defined flags.

        Returns:
          A dictionary.  Its keys are module IDs (ints).  Its values
          are lists of Flag objects.
        """
        return self.__dict__['__flags_by_module_id']

    def KeyFlagsByModuleDict(self):
        """Returns the dictionary of module_name -> list of key flags.

        Returns:
          A dictionary.  Its keys are module names (strings).  Its values
          are lists of Flag objects.
        """
        return self.__dict__['__key_flags_by_module']

    def _RegisterFlagByModule(self, module_name, flag):
        """Records the module that defines a specific flag.

        We keep track of which flag is defined by which module so that we
        can later sort the flags by module.

        Args:
          module_name: A string, the name of a Python module.
          flag: A Flag object, a flag that is key to the module.
        """
        flags_by_module = self.FlagsByModuleDict()
        flags_by_module.setdefault(module_name, []).append(flag)

    def _RegisterFlagByModuleId(self, module_id, flag):
        """Records the module that defines a specific flag.

        Args:
          module_id: An int, the ID of the Python module.
          flag: A Flag object, a flag that is key to the module.
        """
        flags_by_module_id = self.FlagsByModuleIdDict()
        flags_by_module_id.setdefault(module_id, []).append(flag)

    def _RegisterKeyFlagForModule(self, module_name, flag):
        """Specifies that a flag is a key flag for a module.

        Args:
          module_name: A string, the name of a Python module.
          flag: A Flag object, a flag that is key to the module.
        """
        key_flags_by_module = self.KeyFlagsByModuleDict()
        # The list of key flags for the module named module_name.
        key_flags = key_flags_by_module.setdefault(module_name, [])
        # Add flag, but avoid duplicates.
        if flag not in key_flags:
            key_flags.append(flag)

    def _FlagIsRegistered(self, flag_obj):
        """Checks whether a Flag object is registered under long name or short name.

        Args:
          flag_obj: A Flag object.

        Returns:
          A boolean: True iff flag_obj is registered under long name or short name.
        """
        flag_dict = self.FlagDict()
        # Check whether flag_obj is registered under its long name.
        name = flag_obj.name
        if flag_dict.get(name, None) == flag_obj:
            return True
        # Check whether flag_obj is registered under its short name.
        short_name = flag_obj.short_name
        if (short_name is not None and
                flag_dict.get(short_name, None) == flag_obj):
            return True
        return False

    def _CleanupUnregisteredFlagFromModuleDicts(self, flag_obj):
        """Cleanup unregistered flags from all module -> [flags] dictionaries.

        If flag_obj is registered under either its long name or short name, it
        won't be removed from the dictionaries.

        Args:
          flag_obj: A flag object.
        """
        if self._FlagIsRegistered(flag_obj):
            return
        for flags_by_module_dict in (self.FlagsByModuleDict(),
                                     self.FlagsByModuleIdDict(),
                                     self.KeyFlagsByModuleDict()):
            for flags_in_module in six.itervalues(flags_by_module_dict):
                # While (as opposed to if) takes care of multiple occurrences of a
                # flag in the list for the same module.
                while flag_obj in flags_in_module:
                    flags_in_module.remove(flag_obj)

    def _GetFlagsDefinedByModule(self, module):
        """Returns the list of flags defined by a module.

        Args:
          module: A module object or a module name (a string).

        Returns:
          A new list of Flag objects.  Caller may update this list as he
          wishes: none of those changes will affect the internals of this
          FlagValue object.
        """
        if not isinstance(module, str):
            module = module.__name__

        return list(self.FlagsByModuleDict().get(module, []))

    def _GetKeyFlagsForModule(self, module):
        """Returns the list of key flags for a module.

        Args:
          module: A module object or a module name (a string)

        Returns:
          A new list of Flag objects.  Caller may update this list as he
          wishes: none of those changes will affect the internals of this
          FlagValue object.
        """
        if not isinstance(module, str):
            module = module.__name__

        # Any flag is a key flag for the module that defined it.  NOTE:
        # key_flags is a fresh list: we can update it without affecting the
        # internals of this FlagValues object.
        key_flags = self._GetFlagsDefinedByModule(module)

        # Take into account flags explicitly declared as key for a module.
        for flag in self.KeyFlagsByModuleDict().get(module, []):
            if flag not in key_flags:
                key_flags.append(flag)
        return key_flags

    def FindModuleDefiningFlag(self, flagname, default=None):
        """Return the name of the module defining this flag, or default.

        Args:
          flagname: Name of the flag to lookup.
          default: Value to return if flagname is not defined. Defaults
              to None.

        Returns:
          The name of the module which registered the flag with this name.
          If no such module exists (i.e. no flag with this name exists),
          we return default.
        """
        registered_flag = self.FlagDict().get(flagname)
        if registered_flag is None:
            return default
        for module, flags in six.iteritems(self.FlagsByModuleDict()):
            for flag in flags:
                # It must compare the flag with the one in FlagDict. This is because a
                # flag might be overridden only for its long name (or short name),
                # and only its short name (or long name) is considered registered.
                if (flag.name == registered_flag.name and
                        flag.short_name == registered_flag.short_name):
                    return module
        return default

    def FindModuleIdDefiningFlag(self, flagname, default=None):
        """Return the ID of the module defining this flag, or default.

        Args:
          flagname: Name of the flag to lookup.
          default: Value to return if flagname is not defined. Defaults
              to None.

        Returns:
          The ID of the module which registered the flag with this name.
          If no such module exists (i.e. no flag with this name exists),
          we return default.
        """
        registered_flag = self.FlagDict().get(flagname)
        if registered_flag is None:
            return default
        for module_id, flags in six.iteritems(self.FlagsByModuleIdDict()):
            for flag in flags:
                # It must compare the flag with the one in FlagDict. This is because a
                # flag might be overridden only for its long name (or short name),
                # and only its short name (or long name) is considered registered.
                if (flag.name == registered_flag.name and
                        flag.short_name == registered_flag.short_name):
                    return module_id
        return default

    def _RegisterUnknownFlagSetter(self, setter):
        """Allow set default values for undefined flags.

        Args:
          setter: Method(name, value) to call to __setattr__ an unknown flag.
            Must raise NameError or ValueError for invalid name/value.
        """
        self.__dict__['__set_unknown'] = setter

    def _SetUnknownFlag(self, name, value):
        """Returns value if setting flag |name| to |value| returned True.

        Args:
          name: Name of the flag to set.
          value: Value to set.

        Returns:
          Flag value on successful call.

        Raises:
          UnrecognizedFlagError
          IllegalFlagValueError
        """
        setter = self.__dict__['__set_unknown']
        if setter:
            try:
                setter(name, value)
                return value
            except (TypeError, ValueError):  # Flag value is not valid.
                raise exceptions.IllegalFlagValueError('"{1}" is not valid for --{0}'
                                                       .format(name, value))
            except NameError:  # Flag name is not valid.
                pass
        raise exceptions.UnrecognizedFlagError(name, value)

    def AppendFlagValues(self, flag_values):
        """Appends flags registered in another FlagValues instance.

        Args:
          flag_values: registry to copy from
        """
        for flag_name, flag in six.iteritems(flag_values.FlagDict()):
            # Each flags with shortname appears here twice (once under its
            # normal name, and again with its short name).  To prevent
            # problems (DuplicateFlagError) with double flag registration, we
            # perform a check to make sure that the entry we're looking at is
            # for its normal name.
            if flag_name == flag.name:
                try:
                    self[flag_name] = flag
                except exceptions.DuplicateFlagError:
                    raise exceptions.DuplicateFlagError.from_flag(
                        flag_name, self, other_flag_values=flag_values)

    def RemoveFlagValues(self, flag_values):
        """Remove flags that were previously appended from another FlagValues.

        Args:
          flag_values: registry containing flags to remove.
        """
        for flag_name in flag_values.FlagDict():
            self.__delattr__(flag_name)

    def __setitem__(self, name, flag):
        """Registers a new flag variable."""
        fl = self.FlagDict()
        if not isinstance(flag, _flag.Flag):
            raise exceptions.IllegalFlagValueError(flag)
        if str is bytes and isinstance(name, unicode):
            # When using Python 2 with unicode_literals, allow it but encode it
            # into the bytes type we require.
            name = name.encode('utf-8')
        if not isinstance(name, type('')):
            raise exceptions.Error('Flag name must be a string')
        if not name:
            raise exceptions.Error('Flag name cannot be empty')
        if name in fl and not flag.allow_override and not fl[name].allow_override:
            module, module_name = _helpers.GetCallingModuleObjectAndName()
            if (self.FindModuleDefiningFlag(name) == module_name and
                    id(module) != self.FindModuleIdDefiningFlag(name)):
                # If the flag has already been defined by a module with the same name,
                # but a different ID, we can stop here because it indicates that the
                # module is simply being imported a subsequent time.
                return
            raise exceptions.DuplicateFlagError.from_flag(name, self)
        short_name = flag.short_name
        # If a new flag overrides an old one, we need to cleanup the old flag's
        # modules if it's not registered.
        flags_to_cleanup = set()
        if short_name is not None:
            if (short_name in fl and not flag.allow_override and
                    not fl[short_name].allow_override):
                raise exceptions.DuplicateFlagError.from_flag(short_name, self)
            if short_name in fl and fl[short_name] != flag:
                flags_to_cleanup.add(fl[short_name])
            fl[short_name] = flag
        if (name not in fl  # new flag
            or fl[name].using_default_value
                or not flag.using_default_value):
            if name in fl and fl[name] != flag:
                flags_to_cleanup.add(fl[name])
            fl[name] = flag
        for f in flags_to_cleanup:
            self._CleanupUnregisteredFlagFromModuleDicts(f)

    def __dir__(self):
        """Returns list of names of all defined flags.

        Useful for TAB-completion in ipython.

        Returns:
          list(str)
        """
        return sorted(self.__dict__['__flags'])

    # TODO(olexiy): Call GetFlag() to raise UnrecognizedFlagError if name is
    # unknown.
    def __getitem__(self, name):
        """Retrieves the Flag object for the flag --name."""
        return self.FlagDict()[name]

    def GetFlag(self, name):
        """Same as __getitem__, but raises a specific error."""
        res = self.FlagDict().get(name)
        if res is None:
            raise exceptions.UnrecognizedFlagError(name)
        return res

    def HideFlag(self, name):
        """Mark the flag --name as hidden."""
        self.__dict__['__hiddenflags'].add(name)

    def _IsUnparsedFlagAccessAllowed(self, name):
        """Determine whether to allow unparsed flag access or not."""
        if _UNPARSED_FLAG_ACCESS_ENV_NAME in os.environ:
            # We've been told explicitly what to do.
            allow_unparsed_flag_access = (
                os.getenv(_UNPARSED_FLAG_ACCESS_ENV_NAME) == '1')
        elif self.__dict__['__reset_called']:
            # Raise exception if .Reset() was called. This mostly happens in tests.
            allow_unparsed_flag_access = False
        elif _helpers.IsRunningTest():
            # Staged "rollout", based on name of the flag so that we don't break
            # everyone.  Hashing the flag is a way of choosing a random but
            # consistent subset of flags to lock down which we can make larger
            # over time.
            name_bytes = name.encode('utf8') if not isinstance(
                name, bytes) else name
            flag_percentile = (
                struct.unpack('<I', hashlib.md5(name_bytes).digest()[:4])[0] % 100)
            allow_unparsed_flag_access = (
                _UNPARSED_ACCESS_DISABLED_PERCENT <= flag_percentile)
        else:
            allow_unparsed_flag_access = True
        return allow_unparsed_flag_access

    def __getattr__(self, name):
        """Retrieves the 'value' attribute of the flag --name."""
        fl = self.FlagDict()
        if name not in fl:
            raise AttributeError(name)
        if name in self.__dict__['__hiddenflags']:
            raise AttributeError(name)

        if self.__dict__['__flags_parsed'] or fl[name].present:
            return fl[name].value
        else:
            error_message = (
                'Trying to access flag %s before flags were parsed.' % name)
            if self._IsUnparsedFlagAccessAllowed(name):
                # Print warning to stderr. Messages in logs are often ignored/unnoticed.
                warnings.warn(
                    error_message + ' This will raise an exception in the future.',
                    RuntimeWarning,
                    stacklevel=2)
                # Force logging.exception() to behave realistically, but don't propagate
                # exception up. Allow flag value to be returned (for now).
                try:
                    raise exceptions.UnparsedFlagAccessError(error_message)
                except exceptions.UnparsedFlagAccessError:
                    logging.exception(error_message)
                return fl[name].value
            else:
                raise exceptions.UnparsedFlagAccessError(error_message)

    def __setattr__(self, name, value):
        """Sets the 'value' attribute of the flag --name."""
        fl = self.FlagDict()
        if name in self.__dict__['__hiddenflags']:
            raise AttributeError(name)
        if name not in fl:
            return self._SetUnknownFlag(name, value)
        fl[name].value = value
        self._AssertValidators(fl[name].validators)
        fl[name].using_default_value = False
        return value

    def _AssertAllValidators(self):
        all_validators = set()
        for flag in six.itervalues(self.FlagDict()):
            for validator in flag.validators:
                all_validators.add(validator)
        self._AssertValidators(all_validators)

    def _AssertValidators(self, validators):
        """Assert if all validators in the list are satisfied.

        Asserts validators in the order they were created.
        Args:
          validators: Iterable(validators.Validator), validators to be
            verified
        Raises:
          AttributeError: if validators work with a non-existing flag.
          IllegalFlagValueError: if validation fails for at least one validator
        """
        for validator in sorted(
                validators, key=lambda validator: validator.insertion_index):
            try:
                validator.verify(self)
            except exceptions.ValidationError as e:
                message = validator.print_flags_with_values(self)
                raise exceptions.IllegalFlagValueError(
                    '%s: %s' % (message, str(e)))

    def __delattr__(self, flag_name):
        """Deletes a previously-defined flag from a flag object.

        This method makes sure we can delete a flag by using

          del FLAGS.<flag_name>

        E.g.,

          gflags.DEFINE_integer('foo', 1, 'Integer flag.')
          del gflags.FLAGS.foo

        If a flag is also registered by its the other name (long name or short
        name), the other name won't be deleted.

        Args:
          flag_name: A string, the name of the flag to be deleted.

        Raises:
          AttributeError: When there is no registered flag named flag_name.
        """
        fl = self.FlagDict()
        if flag_name not in fl:
            raise AttributeError(flag_name)

        flag_obj = fl[flag_name]
        del fl[flag_name]

        self._CleanupUnregisteredFlagFromModuleDicts(flag_obj)

    def _RemoveAllFlagAppearances(self, name):
        """Removes flag with name for all appearances.

        A flag can be registered with its long name and an optional short name.
        This method removes both of them. This is different than __delattr__.

        Args:
          name: Either flag's long name or short name.

        Raises:
          UnrecognizedFlagError: When flag name is not found.
        """
        flag_dict = self.FlagDict()
        if name not in flag_dict:
            raise exceptions.UnrecognizedFlagError(name)
        flag = flag_dict[name]
        names_to_remove = {name}
        names_to_remove.add(flag.name)
        if flag.short_name:
            names_to_remove.add(flag.short_name)
        for n in names_to_remove:
            self.__delattr__(n)

    def SetDefault(self, name, value):
        """Changes the default value (and current value) of the named flag object.

        Call this method at the top level of a module to avoid overwriting the value
        passed at the command line.

        Args:
          name: A string, the name of the flag to modify.
          value: The new default value.

        Raises:
          UnrecognizedFlagError: When there is no registered flag named name.
          IllegalFlagValueError: When value is not valid.
        """
        fl = self.FlagDict()
        if name not in fl:
            self._SetUnknownFlag(name, value)
            return
        if self.IsParsed():
            logging.warn(
                'FLAGS.SetDefault called on flag "%s" after flag parsing. Call this '
                'method at the top level of a module to avoid overwriting the value '
                'passed at the command line.',
                name)
        fl[name]._set_default(value)  # pylint: disable=protected-access
        self._AssertValidators(fl[name].validators)

    def __contains__(self, name):
        """Returns True if name is a value (flag) in the dict."""
        return name in self.FlagDict()

    has_key = __contains__  # a synonym for __contains__()

    def __iter__(self):
        return iter(self.FlagDict())

    def __call__(self, argv, known_only=False):
        """Parses flags from argv; stores parsed flags into this FlagValues object.

        All unparsed arguments are returned.

        Args:
           argv: argument list. Can be of any type that may be converted to a list.
           known_only: parse and remove known flags, return rest untouched.

        Returns:
           The list of arguments not parsed as options, including argv[0].

        Raises:
           Error: on any parsing error.
           ValueError: on flag value parsing error.
        """
        if not argv:
            # Unfortunately, the old parser used to accept an empty argv, and some
            # users rely on that behaviour. Allow it as a special case for now.
            self.MarkAsParsed()
            self._AssertAllValidators()
            return []

        # This pre parses the argv list for --flagfile=<> options.
        program_name = argv[0]
        args = self.ReadFlagsFromFiles(argv[1:], force_gnu=False)

        # Parse the arguments.
        unknown_flags, unparsed_args, undefok = self._ParseArgs(
            args, known_only)

        # Handle unknown flags by raising UnrecognizedFlagError.
        # Note some users depend on us raising this particular error.
        for name, value in unknown_flags:
            if name in undefok:
                continue

            suggestions = _helpers.GetFlagSuggestions(
                name, self.RegisteredFlags())
            raise exceptions.UnrecognizedFlagError(
                name, value, suggestions=suggestions)

        self.MarkAsParsed()
        self._AssertAllValidators()
        return [program_name] + unparsed_args

    def _ParseArgs(self, args, known_only):
        """Helper function to do the main argument parsing.

        This function goes through args and does the bulk of the flag parsing.
        It will find the corresponding flag in our flag dictionary, and call its
        .parse() method on the flag value.

        Args:
          args: List of strings with the arguments to parse.
          known_only: parse and remove known flags, return rest in unparsed_args

        Returns:
          A tuple with the following:
            unknown_flags: List of (flag name, arg) for flags we don't know about.
            unparsed_args: List of arguments we did not parse.
            undefok: Set of flags that were given via --undefok.

        Raises:
           Error: on any parsing error.
           ValueError: on flag value parsing error.
        """
        unknown_flags, unparsed_args, undefok = [], [], set()

        flag_dict = self.FlagDict()
        args = iter(args)
        for arg in args:
            value = None

            def GetValue():
                # pylint: disable=cell-var-from-loop
                try:
                    return next(args) if value is None else value
                except StopIteration:
                    raise exceptions.Error('Missing value for flag ' + arg)

            if not arg.startswith('-'):
                # A non-argument: default is break, GNU is skip.
                unparsed_args.append(arg)
                if self.IsGnuGetOpt():
                    continue
                else:
                    break

            if arg == '--':
                if known_only:
                    unparsed_args.append(arg)
                break

            if '=' in arg:
                name, value = arg.lstrip('-').split('=', 1)
            else:
                name, value = arg.lstrip('-'), None

            if not name:
                # The argument is all dashes (including one dash).
                unparsed_args.append(arg)
                if self.IsGnuGetOpt():
                    continue
                else:
                    break

            # --undefok is a special case.
            if name == 'undefok':
                if known_only:
                    unparsed_args.append(arg)
                value = GetValue()
                undefok.update(v.strip() for v in value.split(','))
                undefok.update('no' + v.strip() for v in value.split(','))
                continue

            flag = flag_dict.get(name)
            if flag:
                value = (flag.boolean and value is None) or GetValue()
            elif name.startswith('no') and len(name) > 2:
                # Boolean flags can take the form of --noflag, with no value.
                noflag = flag_dict.get(name[2:])
                if noflag and noflag.boolean:
                    if value is not None:
                        raise ValueError(arg + ' does not take an argument')
                    flag = noflag
                    value = False

            if flag:
                flag.parse(value)
                flag.using_default_value = False
            elif known_only:
                unparsed_args.append(arg)
            else:
                unknown_flags.append((name, arg))

        unparsed_args.extend(args)
        return unknown_flags, unparsed_args, undefok

    def IsParsed(self):
        """Whether flags were parsed."""
        return self.__dict__['__flags_parsed']

    def MarkAsParsed(self):
        """Explicitly mark parsed.

        Use this when the caller knows that this FlagValues has been parsed as if
        a __call__() invocation has happened.  This is only a public method for
        use by things like appcommands which do additional command like parsing.
        """
        self.__dict__['__flags_parsed'] = True

    def Reset(self):
        """Resets the values to the point before FLAGS(argv) was called."""
        for f in self.FlagDict().values():
            f.unparse()
        # We log this message before marking flags as unparsed to avoid a
        # problem when the logging library causes flags access.
        logging.info('Reset() called; flags access will now raise errors.')
        self.__dict__['__flags_parsed'] = False
        self.__dict__['__reset_called'] = True

    def RegisteredFlags(self):
        """Returns: a list of the names and short names of all registered flags."""
        return list(self.FlagDict())

    def FlagValuesDict(self):
        """Returns: a dictionary that maps flag names to flag values."""
        flag_values = {}

        for flag_name in self.RegisteredFlags():
            flag = self.FlagDict()[flag_name]
            flag_values[flag_name] = flag.value

        return flag_values

    def __str__(self):
        """Generates a help string for all known flags."""
        return self.GetHelp()

    def GetHelp(self, prefix='', include_special_flags=True):
        """Generates a help string for all known flags.

        Args:
          prefix: str, per-line output prefix.
          include_special_flags: bool, whether to include description of
            _SPECIAL_FLAGS, i.e. --flagfile and --undefok.

        Returns:
          str, formatted help message.
        """
        # TODO(vrusinov): this function needs a test.
        helplist = []

        flags_by_module = self.FlagsByModuleDict()
        if flags_by_module:
            modules = sorted(flags_by_module)

            # Print the help for the main module first, if possible.
            main_module = sys.argv[0]
            if main_module in modules:
                modules.remove(main_module)
                modules = [main_module] + modules

            for module in modules:
                self.__RenderOurModuleFlags(module, helplist)
            if include_special_flags:
                self.__RenderModuleFlags('gflags',
                                         _helpers.SPECIAL_FLAGS.FlagDict().values(),
                                         helplist)
        else:
            # Just print one long list of flags.
            values = self.FlagDict().values()
            if include_special_flags:
                values.append(_helpers.SPECIAL_FLAGS.FlagDict().values())
            self.__RenderFlagList(values, helplist, prefix)

        return '\n'.join(helplist)

    def __RenderModuleFlags(self, module, flags, output_lines, prefix=''):
        """Generates a help string for a given module."""
        if not isinstance(module, str):
            module = module.__name__
        output_lines.append('\n%s%s:' % (prefix, module))
        self.__RenderFlagList(flags, output_lines, prefix + '  ')

    def __RenderOurModuleFlags(self, module, output_lines, prefix=''):
        """Generates a help string for a given module."""
        flags = self._GetFlagsDefinedByModule(module)
        if flags:
            self.__RenderModuleFlags(module, flags, output_lines, prefix)

    def __RenderOurModuleKeyFlags(self, module, output_lines, prefix=''):
        """Generates a help string for the key flags of a given module.

        Args:
          module: A module object or a module name (a string).
          output_lines: A list of strings.  The generated help message
            lines will be appended to this list.
          prefix: A string that is prepended to each generated help line.
        """
        key_flags = self._GetKeyFlagsForModule(module)
        if key_flags:
            self.__RenderModuleFlags(module, key_flags, output_lines, prefix)

    def ModuleHelp(self, module):
        """Describe the key flags of a module.

        Args:
          module: A module object or a module name (a string).

        Returns:
          string describing the key flags of a module.
        """
        helplist = []
        self.__RenderOurModuleKeyFlags(module, helplist)
        return '\n'.join(helplist)

    def MainModuleHelp(self):
        """Describe the key flags of the main module.

        Returns:
          string describing the key flags of a module.
        """
        return self.ModuleHelp(sys.argv[0])

    def __RenderFlagList(self, flaglist, output_lines, prefix='  '):
        fl = self.FlagDict()
        special_fl = _helpers.SPECIAL_FLAGS.FlagDict()
        flaglist = [(flag.name, flag) for flag in flaglist]
        flaglist.sort()
        flagset = {}
        for (name, flag) in flaglist:
            # It's possible this flag got deleted or overridden since being
            # registered in the per-module flaglist.  Check now against the
            # canonical source of current flag information, the FlagDict.
            if fl.get(name, None) != flag and special_fl.get(name, None) != flag:
                # a different flag is using this name now
                continue
            # only print help once
            if flag in flagset:
                continue
            flagset[flag] = 1
            flaghelp = ''
            if flag.short_name:
                flaghelp += '-%s,' % flag.short_name
            if flag.boolean:
                flaghelp += '--[no]%s:' % flag.name
            else:
                flaghelp += '--%s:' % flag.name
            flaghelp += ' '
            if flag.help:
                flaghelp += flag.help
            flaghelp = _helpers.TextWrap(
                flaghelp, indent=prefix+'  ', firstline_indent=prefix)
            if flag.default_as_str:
                flaghelp += '\n'
                flaghelp += _helpers.TextWrap(
                    '(default: %s)' % flag.default_as_str, indent=prefix+'  ')
            if flag.parser.syntactic_help:
                flaghelp += '\n'
                flaghelp += _helpers.TextWrap(
                    '(%s)' % flag.parser.syntactic_help, indent=prefix+'  ')
            output_lines.append(flaghelp)

    def get_flag_value(self, name, default):  # pylint: disable=invalid-name
        """Returns the value of a flag (if not None) or a default value.

        Args:
          name: A string, the name of a flag.
          default: Default value to use if the flag value is None.

        Returns:
          Requested flag value or default.
        """

        value = self.__getattr__(name)
        if value is not None:  # Can't do if not value, b/c value might be '0' or ""
            return value
        else:
            return default

    # TODO(b/32098517): Remove this.
    get = get_flag_value

    def __IsFlagFileDirective(self, flag_string):
        """Checks whether flag_string contain a --flagfile=<foo> directive."""
        if isinstance(flag_string, type('')):
            if flag_string.startswith('--flagfile='):
                return 1
            elif flag_string == '--flagfile':
                return 1
            elif flag_string.startswith('-flagfile='):
                return 1
            elif flag_string == '-flagfile':
                return 1
            else:
                return 0
        return 0

    def ExtractFilename(self, flagfile_str):
        """Returns filename from a flagfile_str of form -[-]flagfile=filename.

        The cases of --flagfile foo and -flagfile foo shouldn't be hitting
        this function, as they are dealt with in the level above this
        function.

        Args:
          flagfile_str: flagfile string.

        Returns:
          str filename from a flagfile_str of form -[-]flagfile=filename.

        Raises:
          Error: when illegal --flagfile provided.
        """
        if flagfile_str.startswith('--flagfile='):
            return os.path.expanduser((flagfile_str[(len('--flagfile=')):]).strip())
        elif flagfile_str.startswith('-flagfile='):
            return os.path.expanduser((flagfile_str[(len('-flagfile=')):]).strip())
        else:
            raise exceptions.Error(
                'Hit illegal --flagfile type: %s' % flagfile_str)

    def __GetFlagFileLines(self, filename, parsed_file_stack=None):
        """Returns the useful (!=comments, etc) lines from a file with flags.

        Args:
          filename: A string, the name of the flag file.
          parsed_file_stack: A list of the names of the files that we have
            recursively encountered at the current depth. MUTATED BY THIS FUNCTION
            (but the original value is preserved upon successfully returning from
            function call).

        Returns:
          List of strings. See the note below.

        NOTE(springer): This function checks for a nested --flagfile=<foo>
        tag and handles the lower file recursively. It returns a list of
        all the lines that _could_ contain command flags. This is
        EVERYTHING except whitespace lines and comments (lines starting
        with '#' or '//').
        """
        if parsed_file_stack is None:
            parsed_file_stack = []
        # We do a little safety check for reparsing a file we've already encountered
        # at a previous depth.
        if filename in parsed_file_stack:
            sys.stderr.write('Warning: Hit circular flagfile dependency. Ignoring'
                             ' flagfile: %s\n' % (filename,))
            return []
        else:
            parsed_file_stack.append(filename)

        line_list = []  # All line from flagfile.
        # Subset of lines w/o comments, blanks, flagfile= tags.
        flag_line_list = []
        try:
            file_obj = open(filename, 'r')
        except IOError as e_msg:
            raise exceptions.CantOpenFlagFileError(
                'ERROR:: Unable to open flagfile: %s' % e_msg)

        with file_obj:
            line_list = file_obj.readlines()

        # This is where we check each line in the file we just read.
        for line in line_list:
            if line.isspace():
                pass
            # Checks for comment (a line that starts with '#').
            elif line.startswith('#') or line.startswith('//'):
                pass
            # Checks for a nested "--flagfile=<bar>" flag in the current file.
            # If we find one, recursively parse down into that file.
            elif self.__IsFlagFileDirective(line):
                sub_filename = self.ExtractFilename(line)
                included_flags = self.__GetFlagFileLines(
                    sub_filename, parsed_file_stack=parsed_file_stack)
                flag_line_list.extend(included_flags)
            else:
                # Any line that's not a comment or a nested flagfile should get
                # copied into 2nd position.  This leaves earlier arguments
                # further back in the list, thus giving them higher priority.
                flag_line_list.append(line.strip())

        parsed_file_stack.pop()
        return flag_line_list

    def ReadFlagsFromFiles(self, argv, force_gnu=True):
        """Processes command line args, but also allow args to be read from file.

        Args:
          argv: A list of strings, usually sys.argv[1:], which may contain one or
            more flagfile directives of the form --flagfile="./filename".
            Note that the name of the program (sys.argv[0]) should be omitted.
          force_gnu: If False, --flagfile parsing obeys normal flag semantics.
            If True, --flagfile parsing instead follows gnu_getopt semantics.
            *** WARNING *** force_gnu=False may become the future default!

        Returns:
          A new list which has the original list combined with what we read
          from any flagfile(s).

        Raises:
          IllegalFlagValueError: when --flagfile provided with no argument.

        References: Global gflags.FLAG class instance.

        This function should be called before the normal FLAGS(argv) call.
        This function scans the input list for a flag that looks like:
        --flagfile=<somefile>. Then it opens <somefile>, reads all valid key
        and value pairs and inserts them into the input list in exactly the
        place where the --flagfile arg is found.

        Note that your application's flags are still defined the usual way
        using gflags DEFINE_flag() type functions.

        Notes (assuming we're getting a commandline of some sort as our input):
        --> For duplicate flags, the last one we hit should "win".
        --> Since flags that appear later win, a flagfile's settings can be "weak"
            if the --flagfile comes at the beginning of the argument sequence,
            and it can be "strong" if the --flagfile comes at the end.
        --> A further "--flagfile=<otherfile.cfg>" CAN be nested in a flagfile.
            It will be expanded in exactly the spot where it is found.
        --> In a flagfile, a line beginning with # or // is a comment.
        --> Entirely blank lines _should_ be ignored.
        """
        rest_of_args = argv
        new_argv = []
        while rest_of_args:
            current_arg = rest_of_args[0]
            rest_of_args = rest_of_args[1:]
            if self.__IsFlagFileDirective(current_arg):
                # This handles the case of -(-)flagfile foo.  In this case the
                # next arg really is part of this one.
                if current_arg == '--flagfile' or current_arg == '-flagfile':
                    if not rest_of_args:
                        raise exceptions.IllegalFlagValueError(
                            '--flagfile with no argument')
                    flag_filename = os.path.expanduser(rest_of_args[0])
                    rest_of_args = rest_of_args[1:]
                else:
                    # This handles the case of (-)-flagfile=foo.
                    flag_filename = self.ExtractFilename(current_arg)
                new_argv.extend(self.__GetFlagFileLines(flag_filename))
            else:
                new_argv.append(current_arg)
                # Stop parsing after '--', like getopt and gnu_getopt.
                if current_arg == '--':
                    break
                # Stop parsing after a non-flag, like getopt.
                if not current_arg.startswith('-'):
                    if not force_gnu and not self.__dict__['__use_gnu_getopt']:
                        break
                else:
                    if ('=' not in current_arg and
                            rest_of_args and not rest_of_args[0].startswith('-')):
                        # If this is an occurence of a legitimate --x y, skip the value
                        # so that it won't be mistaken for a standalone arg.
                        fl = self.FlagDict()
                        name = current_arg.lstrip('-')
                        if name in fl and not fl[name].boolean:
                            current_arg = rest_of_args[0]
                            rest_of_args = rest_of_args[1:]
                            new_argv.append(current_arg)

        if rest_of_args:
            new_argv.extend(rest_of_args)

        return new_argv

    def FlagsIntoString(self):
        """Returns a string with the flags assignments from this FlagValues object.

        This function ignores flags whose value is None.  Each flag
        assignment is separated by a newline.

        NOTE: MUST mirror the behavior of the C++ CommandlineFlagsIntoString
        from http://code.google.com/p/google-gflags

        Returns:
          string with the flags assignments from this FlagValues object.
        """
        s = ''
        for flag in self.FlagDict().values():
            if flag.value is not None:
                s += flag.serialize() + '\n'
        return s

    def AppendFlagsIntoFile(self, filename):
        """Appends all flags assignments from this FlagInfo object to a file.

        Output will be in the format of a flagfile.

        NOTE: MUST mirror the behavior of the C++ AppendFlagsIntoFile
        from http://code.google.com/p/google-gflags

        Args:
          filename: string, name of the file.
        """
        with open(filename, 'a') as out_file:
            out_file.write(self.FlagsIntoString())

    def WriteHelpInXMLFormat(self, outfile=None):
        """Outputs flag documentation in XML format.

        NOTE: We use element names that are consistent with those used by
        the C++ command-line flag library, from
        http://code.google.com/p/google-gflags
        We also use a few new elements (e.g., <key>), but we do not
        interfere / overlap with existing XML elements used by the C++
        library.  Please maintain this consistency.

        Args:
          outfile: File object we write to.  Default None means sys.stdout.
        """
        doc = minidom.Document()
        all_flag = doc.createElement('AllFlags')
        doc.appendChild(all_flag)

        all_flag.appendChild(_helpers.CreateXMLDOMElement(
            doc, 'program', os.path.basename(sys.argv[0])))

        usage_doc = sys.modules['__main__'].__doc__
        if not usage_doc:
            usage_doc = '\nUSAGE: %s [flags]\n' % sys.argv[0]
        else:
            usage_doc = usage_doc.replace('%s', sys.argv[0])
        all_flag.appendChild(
            _helpers.CreateXMLDOMElement(doc, 'usage', usage_doc))

        # Get list of key flags for the main module.
        key_flags = self._GetKeyFlagsForModule(sys.argv[0])

        # Sort flags by declaring module name and next by flag name.
        flags_by_module = self.FlagsByModuleDict()
        all_module_names = list(flags_by_module.keys())
        all_module_names.sort()
        for module_name in all_module_names:
            flag_list = [(f.name, f) for f in flags_by_module[module_name]]
            flag_list.sort()
            for unused_flag_name, flag in flag_list:
                is_key = flag in key_flags
                all_flag.appendChild(flag._create_xml_dom_element(  # pylint: disable=protected-access
                    doc, module_name, is_key=is_key))

        outfile = outfile or sys.stdout
        if six.PY2:
            outfile.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
        else:
            outfile.write(
                doc.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8'))
        outfile.flush()

    # New PEP8 style functions.
    def set_gnu_getopt(self, gnu_getopt=True):
        self.UseGnuGetOpt(gnu_getopt)

    is_gnu_getopt = IsGnuGetOpt
    flags_by_module_dict = FlagsByModuleDict
    flags_by_module_id_dict = FlagsByModuleIdDict
    key_flags_by_module_dict = KeyFlagsByModuleDict
    register_key_flag_for_module = _RegisterKeyFlagForModule
    find_module_defining_flag = FindModuleDefiningFlag
    find_module_id_defining_flag = FindModuleIdDefiningFlag
    append_flag_values = AppendFlagValues
    remove_flag_values = RemoveFlagValues
    set_default = SetDefault
    is_parsed = IsParsed
    mark_as_parsed = MarkAsParsed
    flag_values_dict = FlagValuesDict
    module_help = ModuleHelp
    main_module_help = MainModuleHelp
    read_flags_from_files = ReadFlagsFromFiles
    flags_into_string = FlagsIntoString
    append_flags_into_file = AppendFlagsIntoFile
    write_help_in_xml_format = WriteHelpInXMLFormat
    get_key_flags_for_module = _GetKeyFlagsForModule
    unparse_flags = Reset


_helpers.SPECIAL_FLAGS = FlagValues()

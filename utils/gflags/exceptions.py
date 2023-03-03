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


"""//gflags exceptions.

Instead of importing this module directly, it's preferable to import the
flags package and use the aliases defined at the package level.
"""

import sys

from utils.gflags import _helpers


# TODO(vrusinov): use DISCLAIM_key_flags when it's moved out of __init__.
_helpers.disclaim_module_ids.add(id(sys.modules[__name__]))


class Error(Exception):
    """The base class for all flags errors."""


# TODO(b/31596146): Remove FlagsError.
FlagsError = Error


class CantOpenFlagFileError(Error):
    """Raised if flagfile fails to open: doesn't exist, wrong permissions, etc."""


class DuplicateFlagCannotPropagateNoneToSwig(Error):
    """Raised when redefining a SWIG flag and the default value is None.

    It's raised when redefining a SWIG flag with allow_override=True and the
    default value is None. Because it's currently impossible to pass None default
    value back to SWIG. See FlagValues.SetDefault for details.
    """


class DuplicateFlagError(Error):
    """Raised if there is a flag naming conflict."""

    @classmethod
    def from_flag(cls, flagname, flag_values, other_flag_values=None):
        """Create a DuplicateFlagError by providing flag name and values.

        Args:
          flagname: Name of the flag being redefined.
          flag_values: FlagValues object containing the first definition of
              flagname.
          other_flag_values: If this argument is not None, it should be the
              FlagValues object where the second definition of flagname occurs.
              If it is None, we assume that we're being called when attempting
              to create the flag a second time, and we use the module calling
              this one as the source of the second definition.

        Returns:
          An instance of DuplicateFlagError.
        """
        first_module = flag_values.FindModuleDefiningFlag(
            flagname, default='<unknown>')
        if other_flag_values is None:
            second_module = _helpers.GetCallingModule()
        else:
            second_module = other_flag_values.FindModuleDefiningFlag(
                flagname, default='<unknown>')
        flag_summary = flag_values[flagname].help
        msg = ("The flag '%s' is defined twice. First from %s, Second from %s.  "
               "Description from first occurrence: %s") % (
                   flagname, first_module, second_module, flag_summary)
        return cls(msg)


class IllegalFlagValueError(Error):
    """Raised if the flag command line argument is illegal."""


# TODO(yileiyang): Remove IllegalFlagValue.
IllegalFlagValue = IllegalFlagValueError


class UnrecognizedFlagError(Error):
    """Raised if a flag is unrecognized.

    Attributes:
      flagname: Name of the unrecognized flag.
      flagvalue: Value of the flag, empty if the flag is not defined.
    """

    def __init__(self, flagname, flagvalue='', suggestions=None):
        self.flagname = flagname
        self.flagvalue = flagvalue
        if suggestions:
            tip = '. Did you mean: %s?' % ', '.join(suggestions)
        else:
            tip = ''
        Error.__init__(
            self, 'Unknown command line flag \'%s\'%s' % (flagname, tip))


class UnparsedFlagAccessError(Error):
    """Attempt to use flag from unparsed FlagValues."""


class ValidationError(Error):
    """Raised if flag validator constraint is not satisfied."""

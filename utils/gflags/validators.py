#!/usr/bin/env python
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Module to enforce different constraints on flags.

Instead of importing this module directly, it's preferable to import the
flags package and use the aliases defined at the package level.

A validator represents an invariant, enforced over a one or more flags.
See 'FLAGS VALIDATORS' in the flags module's docstring for a usage manual.
"""

__author__ = 'olexiy@google.com (Olexiy Oryeshko)'


from utils.gflags import exceptions


# TODO(yileiyang): Remove this.
Error = exceptions.ValidationError  # pylint: disable=invalid-name


class Validator(object):
    """Base class for flags validators.

    Users should NOT overload these classes, and use gflags.Register...
    methods instead.
    """

    # Used to assign each validator an unique insertion_index
    validators_count = 0

    def __init__(self, checker, message):
        """Constructor to create all validators.

        Args:
          checker: function to verify the constraint.
            Input of this method varies, see SingleFlagValidator and
              multi_flags_validator for a detailed description.
          message: string, error message to be shown to the user
        """
        self.checker = checker
        self.message = message
        Validator.validators_count += 1
        # Used to assert validators in the order they were registered (CL/18694236)
        self.insertion_index = Validator.validators_count

    def verify(self, flag_values):
        """Verify that constraint is satisfied.

        flags library calls this method to verify Validator's constraint.
        Args:
          flag_values: gflags.FlagValues, containing all flags
        Raises:
          Error: if constraint is not satisfied.
        """
        param = self._get_input_to_checker_function(flag_values)
        if not self.checker(param):
            raise exceptions.ValidationError(self.message)

    def get_flags_names(self):
        """Return the names of the flags checked by this validator.

        Returns:
          [string], names of the flags
        """
        raise NotImplementedError('This method should be overloaded')

    def print_flags_with_values(self, flag_values):
        raise NotImplementedError('This method should be overloaded')

    def _get_input_to_checker_function(self, flag_values):
        """Given flag values, construct the input to be given to checker.

        Args:
          flag_values: gflags.FlagValues, containing all flags.
        Returns:
          Return type depends on the specific validator.
        """
        raise NotImplementedError('This method should be overloaded')


class SingleFlagValidator(Validator):
    """Validator behind register_validator() method.

    Validates that a single flag passes its checker function. The checker function
    takes the flag value and returns True (if value looks fine) or, if flag value
    is not valid, either returns False or raises an Exception.
    """

    def __init__(self, flag_name, checker, message):
        """Constructor.

        Args:
          flag_name: string, name of the flag.
          checker: function to verify the validator.
            input  - value of the corresponding flag (string, boolean, etc).
            output - Boolean. Must return True if validator constraint is satisfied.
              If constraint is not satisfied, it should either return False or
              raise Error.
          message: string, error message to be shown to the user if validator's
            condition is not satisfied
        """
        super(SingleFlagValidator, self).__init__(checker, message)
        self.flag_name = flag_name

    def get_flags_names(self):
        return [self.flag_name]

    def print_flags_with_values(self, flag_values):
        return 'flag --%s=%s' % (self.flag_name, flag_values[self.flag_name].value)

    def _get_input_to_checker_function(self, flag_values):
        """Given flag values, construct the input to be given to checker.

        Args:
          flag_values: gflags.FlagValues
        Returns:
          value of the corresponding flag.
        """
        return flag_values[self.flag_name].value


class MultiFlagsValidator(Validator):
    """Validator behind register_multi_flags_validator method.

    Validates that flag values pass their common checker function. The checker
    function takes flag values and returns True (if values look fine) or,
    if values are not valid, either returns False or raises an Exception.
    """

    def __init__(self, flag_names, checker, message):
        """Constructor.

        Args:
          flag_names: [string], containing names of the flags used by checker.
          checker: function to verify the validator.
            input  - dictionary, with keys() being flag_names, and value for each
              key being the value of the corresponding flag (string, boolean, etc).
            output - Boolean. Must return True if validator constraint is satisfied.
              If constraint is not satisfied, it should either return False or
              raise Error.
          message: string, error message to be shown to the user if validator's
            condition is not satisfied
        """
        super(MultiFlagsValidator, self).__init__(checker, message)
        self.flag_names = flag_names

    def _get_input_to_checker_function(self, flag_values):
        """Given flag values, construct the input to be given to checker.

        Args:
          flag_values: gflags.FlagValues
        Returns:
          dictionary, with keys() being self.lag_names, and value for each key
            being the value of the corresponding flag (string, boolean, etc).
        """
        return dict([key, flag_values[key].value] for key in self.flag_names)

    def print_flags_with_values(self, flag_values):
        prefix = 'flags '
        flags_with_values = []
        for key in self.flag_names:
            flags_with_values.append('%s=%s' % (key, flag_values[key].value))
        return prefix + ', '.join(flags_with_values)

    def get_flags_names(self):
        return self.flag_names

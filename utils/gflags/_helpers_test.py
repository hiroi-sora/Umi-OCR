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

"""Unittest for helpers module."""

import sys

import unittest

from utils.gflags import _helpers
from utils.gflags.flags_modules_for_testing import module_bar
from utils.gflags.flags_modules_for_testing import module_foo


class FlagSuggestionTest(unittest.TestCase):

    def setUp(self):
        self.longopts = [
            'fsplit-ivs-in-unroller=',
            'fsplit-wide-types=',
            'fstack-protector=',
            'fstack-protector-all=',
            'fstrict-aliasing=',
            'fstrict-overflow=',
            'fthread-jumps=',
            'ftracer',
            'ftree-bit-ccp',
            'ftree-builtin-call-dce',
            'ftree-ccp',
            'ftree-ch']

    def testDamerauLevenshteinId(self):
        self.assertEqual(0, _helpers._DamerauLevenshtein('asdf', 'asdf'))

    def testDamerauLevenshteinEmpty(self):
        self.assertEqual(5, _helpers._DamerauLevenshtein('', 'kites'))
        self.assertEqual(6, _helpers._DamerauLevenshtein('kitten', ''))

    def testDamerauLevenshteinCommutative(self):
        self.assertEqual(2, _helpers._DamerauLevenshtein('kitten', 'kites'))
        self.assertEqual(2, _helpers._DamerauLevenshtein('kites', 'kitten'))

    def testDamerauLevenshteinTransposition(self):
        self.assertEqual(1, _helpers._DamerauLevenshtein('kitten', 'ktiten'))

    def testMispelledSuggestions(self):
        suggestions = _helpers.GetFlagSuggestions('fstack_protector_all',
                                                  self.longopts)
        self.assertEqual(['fstack-protector-all'], suggestions)

    def testAmbiguousPrefixSuggestion(self):
        suggestions = _helpers.GetFlagSuggestions('fstack', self.longopts)
        self.assertEqual(
            ['fstack-protector', 'fstack-protector-all'], suggestions)

    def testMisspelledAmbiguousPrefixSuggestion(self):
        suggestions = _helpers.GetFlagSuggestions('stack', self.longopts)
        self.assertEqual(
            ['fstack-protector', 'fstack-protector-all'], suggestions)

    def testCrazySuggestion(self):
        suggestions = _helpers.GetFlagSuggestions(
            'asdfasdgasdfa', self.longopts)
        self.assertEqual([], suggestions)


class GetCallingModuleTest(unittest.TestCase):
    """Test whether we correctly determine the module which defines the flag."""

    def testGetCallingModule(self):
        self.assertEqual(_helpers.GetCallingModule(), sys.argv[0])
        self.assertEqual(
            module_foo.GetModuleName(),
            'gflags.flags_modules_for_testing.module_foo')
        self.assertEqual(
            module_bar.GetModuleName(),
            'gflags.flags_modules_for_testing.module_bar')

        # We execute the following exec statements for their side-effect
        # (i.e., not raising an error).  They emphasize the case that not
        # all code resides in one of the imported modules: Python is a
        # really dynamic language, where we can dynamically construct some
        # code and execute it.
        code = ('from utils.gflags import _helpers\n'
                'module_name = _helpers.GetCallingModule()')
        exec(code)  # pylint: disable=exec-used

        # Next two exec statements executes code with a global environment
        # that is different from the global environment of any imported
        # module.
        exec(code, {})  # pylint: disable=exec-used
        # vars(self) returns a dictionary corresponding to the symbol
        # table of the self object.  dict(...) makes a distinct copy of
        # this dictionary, such that any new symbol definition by the
        # exec-ed code (e.g., import flags, module_name = ...) does not
        # affect the symbol table of self.
        exec(code, dict(vars(self)))  # pylint: disable=exec-used

        # Next test is actually more involved: it checks not only that
        # GetCallingModule does not crash inside exec code, it also checks
        # that it returns the expected value: the code executed via exec
        # code is treated as being executed by the current module.  We
        # check it twice: first time by executing exec from the main
        # module, second time by executing it from module_bar.
        global_dict = {}
        exec(code, global_dict)  # pylint: disable=exec-used
        self.assertEqual(global_dict['module_name'],
                         sys.argv[0])

        global_dict = {}
        module_bar.ExecuteCode(code, global_dict)
        self.assertEqual(
            global_dict['module_name'],
            'gflags.flags_modules_for_testing.module_bar')

    def testGetCallingModuleWithIteritemsError(self):
        # This test checks that GetCallingModule is using
        # sys.modules.items(), instead of .iteritems().
        orig_sys_modules = sys.modules

        # Mock sys.modules: simulates error produced by importing a module
        # in paralel with our iteration over sys.modules.iteritems().
        class SysModulesMock(dict):

            def __init__(self, original_content):
                dict.__init__(self, original_content)

            def iteritems(self):
                # Any dictionary method is fine, but not .iteritems().
                raise RuntimeError('dictionary changed size during iteration')

        sys.modules = SysModulesMock(orig_sys_modules)
        try:
            # _GetCallingModule should still work as expected:
            self.assertEqual(_helpers.GetCallingModule(), sys.argv[0])
            self.assertEqual(
                module_foo.GetModuleName(),
                'gflags.flags_modules_for_testing.module_foo')
        finally:
            sys.modules = orig_sys_modules


class IsRunningTestTest(unittest.TestCase):

    def testUnderTest(self):
        self.assertTrue(_helpers.IsRunningTest())


def main():
    unittest.main()


if __name__ == '__main__':
    main()

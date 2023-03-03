#!/usr/bin/env python
import unittest

import gflags
from utils.gflags import _helpers

FLAGS = gflags.FLAGS


class FlagsUnitTest(unittest.TestCase):
    """Flags formatting Unit Test."""

    def testGetHelpWidth(self):
        """Verify that GetHelpWidth() reflects _help_width."""
        default_help_width = _helpers._DEFAULT_HELP_WIDTH  # Save.
        self.assertEqual(80, _helpers._DEFAULT_HELP_WIDTH)
        self.assertEqual(_helpers._DEFAULT_HELP_WIDTH, gflags.GetHelpWidth())
        _helpers._DEFAULT_HELP_WIDTH = 10
        self.assertEqual(_helpers._DEFAULT_HELP_WIDTH, gflags.GetHelpWidth())
        _helpers._DEFAULT_HELP_WIDTH = default_help_width  # restore

    def testTextWrap(self):
        """Test that wrapping works as expected.

        Also tests that it is using global gflags._help_width by default.
        """
        default_help_width = _helpers._DEFAULT_HELP_WIDTH
        _helpers._DEFAULT_HELP_WIDTH = 10

        # Generate a string with length 40, no spaces
        text = ''
        expect = []
        for n in range(4):
            line = str(n)
            line += '123456789'
            text += line
            expect.append(line)

        # Verify we still break
        wrapped = gflags.TextWrap(text).split('\n')
        self.assertEqual(4, len(wrapped))
        self.assertEqual(expect, wrapped)

        wrapped = gflags.TextWrap(text, 80).split('\n')
        self.assertEqual(1, len(wrapped))
        self.assertEqual([text], wrapped)

        # Normal case, breaking at word boundaries and rewriting new lines
        input_value = 'a b c d e f g h'
        expect = {1: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                  2: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                  3: ['a b', 'c d', 'e f', 'g h'],
                  4: ['a b', 'c d', 'e f', 'g h'],
                  5: ['a b c', 'd e f', 'g h'],
                  6: ['a b c', 'd e f', 'g h'],
                  7: ['a b c d', 'e f g h'],
                  8: ['a b c d', 'e f g h'],
                  9: ['a b c d e', 'f g h'],
                  10: ['a b c d e', 'f g h'],
                  11: ['a b c d e f', 'g h'],
                  12: ['a b c d e f', 'g h'],
                  13: ['a b c d e f g', 'h'],
                  14: ['a b c d e f g', 'h'],
                  15: ['a b c d e f g h']}
        for width, exp in expect.items():
            self.assertEqual(exp, gflags.TextWrap(
                input_value, width).split('\n'))

        # We turn lines with only whitespace into empty lines
        # We strip from the right up to the first new line
        self.assertEqual('', gflags.TextWrap('  '))
        self.assertEqual('\n', gflags.TextWrap('  \n  '))
        self.assertEqual('\n', gflags.TextWrap('\n\n'))
        self.assertEqual('\n\n', gflags.TextWrap('\n\n\n'))
        self.assertEqual('\n', gflags.TextWrap('\n '))
        self.assertEqual('a\n\nb', gflags.TextWrap('a\n  \nb'))
        self.assertEqual('a\n\n\nb', gflags.TextWrap('a\n  \n  \nb'))
        self.assertEqual('a\nb', gflags.TextWrap('  a\nb  '))
        self.assertEqual('\na\nb', gflags.TextWrap('\na\nb\n'))
        self.assertEqual('\na\nb\n', gflags.TextWrap('  \na\nb\n  '))
        self.assertEqual('\na\nb\n', gflags.TextWrap('  \na\nb\n\n'))

        # Double newline.
        self.assertEqual('a\n\nb', gflags.TextWrap(' a\n\n b'))

        # We respect prefix
        self.assertEqual(' a\n b\n c', gflags.TextWrap('a\nb\nc', 80, ' '))
        self.assertEqual('a\n b\n c', gflags.TextWrap('a\nb\nc', 80, ' ', ''))

        # tabs
        self.assertEqual('a\n b   c',
                         gflags.TextWrap('a\nb\tc', 80, ' ', ''))
        self.assertEqual('a\n bb  c',
                         gflags.TextWrap('a\nbb\tc', 80, ' ', ''))
        self.assertEqual('a\n bbb c',
                         gflags.TextWrap('a\nbbb\tc', 80, ' ', ''))
        self.assertEqual('a\n bbbb    c',
                         gflags.TextWrap('a\nbbbb\tc', 80, ' ', ''))
        self.assertEqual('a\n b\n c\n d',
                         gflags.TextWrap('a\nb\tc\td', 3, ' ', ''))
        self.assertEqual('a\n b\n c\n d',
                         gflags.TextWrap('a\nb\tc\td', 4, ' ', ''))
        self.assertEqual('a\n b\n c\n d',
                         gflags.TextWrap('a\nb\tc\td', 5, ' ', ''))
        self.assertEqual('a\n b   c\n d',
                         gflags.TextWrap('a\nb\tc\td', 6, ' ', ''))
        self.assertEqual('a\n b   c\n d',
                         gflags.TextWrap('a\nb\tc\td', 7, ' ', ''))
        self.assertEqual('a\n b   c\n d',
                         gflags.TextWrap('a\nb\tc\td', 8, ' ', ''))
        self.assertEqual('a\n b   c\n d',
                         gflags.TextWrap('a\nb\tc\td', 9, ' ', ''))
        self.assertEqual('a\n b   c   d',
                         gflags.TextWrap('a\nb\tc\td', 10, ' ', ''))

        # multiple tabs
        self.assertEqual('a       c',
                         gflags.TextWrap('a\t\tc', 80, ' ', ''))

        _helpers._DEFAULT_HELP_WIDTH = default_help_width  # restore

    def testDocToHelp(self):
        self.assertEqual('', gflags.DocToHelp('  '))
        self.assertEqual('', gflags.DocToHelp('  \n  '))
        self.assertEqual('a\n\nb', gflags.DocToHelp('a\n  \nb'))
        self.assertEqual('a\n\n\nb', gflags.DocToHelp('a\n  \n  \nb'))
        self.assertEqual('a b', gflags.DocToHelp('  a\nb  '))
        self.assertEqual('a b', gflags.DocToHelp('\na\nb\n'))
        self.assertEqual('a\n\nb', gflags.DocToHelp('\na\n\nb\n'))
        self.assertEqual('a b', gflags.DocToHelp('  \na\nb\n  '))
        # Different first line, one line empty - erm double new line.
        self.assertEqual('a b c\n\nd', gflags.DocToHelp('a\n  b\n  c\n\n  d'))
        self.assertEqual('a b\n      c d',
                         gflags.DocToHelp('a\n  b\n  \tc\n  d'))
        self.assertEqual('a b\n      c\n      d',
                         gflags.DocToHelp('a\n  b\n  \tc\n  \td'))

    def testDocToHelp_FlagValues(self):
        # !!!!!!!!!!!!!!!!!!!!
        # The following doc string is taken as is directly from utils.gflags.py:FlagValues
        # The intention of this test is to verify 'live' performance
        # !!!!!!!!!!!!!!!!!!!!
        """Used as a registry for 'Flag' objects.

        A 'FlagValues' can then scan command line arguments, passing flag
        arguments through to the 'Flag' objects that it owns.  It also
        provides easy access to the flag values.  Typically only one
        'FlagValues' object is needed by an application:  gflags.FLAGS

        This class is heavily overloaded:

        'Flag' objects are registered via __setitem__:
             FLAGS['longname'] = x   # register a new flag

        The .value member of the registered 'Flag' objects can be accessed as
        members of this 'FlagValues' object, through __getattr__.  Both the
        long and short name of the original 'Flag' objects can be used to
        access its value:
             FLAGS.longname          # parsed flag value
             FLAGS.x                 # parsed flag value (short name)

        Command line arguments are scanned and passed to the registered 'Flag'
        objects through the __call__ method.  Unparsed arguments, including
        argv[0] (e.g. the program name) are returned.
             argv = FLAGS(sys.argv)  # scan command line arguments

        The original registered Flag objects can be retrieved through the use
        """
        doc = gflags.DocToHelp(self.testDocToHelp_FlagValues.__doc__)
        # Test the general outline of the converted docs
        lines = doc.splitlines()
        self.assertEqual(17, len(lines))
        empty_lines = [index for index in range(
            len(lines)) if not lines[index]]
        self.assertEqual([1, 3, 5, 8, 12, 15], empty_lines)
        # test that some starting prefix is kept
        flags_lines = [index for index in range(len(lines))
                       if lines[index].startswith('     FLAGS')]
        self.assertEqual([7, 10, 11], flags_lines)
        # but other, especially common space has been removed
        space_lines = [index for index in range(len(lines))
                       if lines[index] and lines[index][0].isspace()]
        self.assertEqual([7, 10, 11, 14], space_lines)
        # No right space was kept
        rspace_lines = [index for index in range(len(lines))
                        if lines[index] != lines[index].rstrip()]
        self.assertEqual([], rspace_lines)
        # test double spaces are kept
        self.assertEqual(True, lines[2].endswith('application:  gflags.FLAGS'))

    def testTextWrapRaisesOnExcessiveIndent(self):
        """Ensure an indent longer than line length raises."""
        self.assertRaises(ValueError,
                          gflags.TextWrap, 'dummy', length=10, indent=' ' * 10)

    def testTextWrapRaisesOnExcessiveFirstLine(self):
        """Ensure a first line indent longer than line length raises."""
        self.assertRaises(
            ValueError,
            gflags.TextWrap, 'dummy', length=80, firstline_indent=' ' * 80)


if __name__ == '__main__':
    unittest.main()

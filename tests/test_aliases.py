# test_aliases.py

import unittest

from replkit.generic_repl import GenericREPL

class DummyInterpreter:
    def eval(self, line): pass
    def get_keywords(self): return set()

class AliasTests(unittest.TestCase):
    def setUp(self):
        self.repl = GenericREPL(interpreter=DummyInterpreter())

    def test_basic_alias_expansion(self):
        self.repl.aliases["@X"] = "A or B"
        result = self.repl.expand_aliases("@X and C")
        self.assertEqual(result, "(A or B) and C")

    def test_undefined_alias_raises(self):
        result = self.repl.expand_aliases("@UNDEF and A")
        self.assertEqual(result, "@UNDEF and A")

    def test_multiple_aliases(self):
        self.repl.aliases["@A"] = "True"
        self.repl.aliases["@B"] = "False"
        result = self.repl.expand_aliases("@A and @B")
        self.assertEqual(result, "(True) and (False)")

    def test_partial_match_not_replaced(self):
        self.repl.aliases["@A"] = "True"
        with self.assertRaises(ValueError) as context:
            self.repl.expand_aliases("@A1 and @A")

        self.assertIn("Unknown alias: '@A1'", str(context.exception))


    def test_no_aliases_defined(self):
        result = self.repl.expand_aliases("A and B")
        self.assertEqual(result, "A and B")

if __name__ == '__main__':
    unittest.main()

import unittest

from lark.exceptions import UnexpectedInput, VisitError

from src.parser import config_to_dict


class ParserTests(unittest.TestCase):
    def test_empty_dictionary(self):
        self.assertEqual(config_to_dict("{}"), {})

    def test_nested_dictionary_with_comment(self):
        text = (
            "# Настройки\n"
            "{ server: { timeout: -2.5E-1; name: q(Тест #1); }; }"
        )
        self.assertEqual(
            config_to_dict(text),
            {"server": {"timeout": -0.25, "name": "Тест #1"}},
        )

    def test_addition_and_constant_chain(self):
        text = "(def base 2e1); (def next @[base 1 +]); { timeout: @[next]; }"
        self.assertEqual(config_to_dict(text), {"timeout": 21.0})

    def test_power_and_subtraction(self):
        text = "{ result: @[2 3 pow() 5 -]; }"
        self.assertEqual(config_to_dict(text), {"result": 3})

    def test_dictionary_constant_inside_nested_dictionary(self):
        text = (
            "(def base { name: q(Тест); }); "
            "{ server: { config: @[base]; }; }"
        )
        self.assertEqual(
            config_to_dict(text),
            {"server": {"config": {"name": "Тест"}}},
        )

    def test_invalid_syntax(self):
        for text in (
            "{ name: q(Тест) }",
            "{ Name: q(Тест); }",
            "{ name: q(Тест; }",
        ):
            with self.subTest(text=text):
                with self.assertRaises(UnexpectedInput):
                    config_to_dict(text)

    def test_invalid_expressions(self):
        for text in (
            "{ result: @[unknown]; }",
            "{ result: @[1 +]; }",
            "{ result: @[1 2]; }",
            "(def word q(Тест)); { result: @[word 1 +]; }",
        ):
            with self.subTest(text=text):
                with self.assertRaises(VisitError) as raised:
                    config_to_dict(text)
                self.assertIsInstance(raised.exception.orig_exc, ValueError)

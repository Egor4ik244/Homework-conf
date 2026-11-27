from operator import add, pow as power, sub
from pathlib import Path

from lark import Lark, Token, Transformer, v_args
from lark.exceptions import VisitError

GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")
PARSER = Lark.open(str(GRAMMAR_PATH), parser="lalr")
OPERATIONS = {"+": add, "-": sub, "pow()": power}
BINARY_ARITY = 2
TOKEN_CONVERTERS = {"NAME": str, "NUMBER": float, "INTEGER": int}

def parse_config(text):
    """Разобрать текст конфигурации и вернуть дерево разбора."""
    return PARSER.parse(text)

@v_args(inline=True)
class ConfigTransformer(Transformer):
    """Преобразует дерево разбора в значения Python."""

    def __init__(self):
        super().__init__()
        self.constans = {}

    def __default_token__(self, token):
        """Преобразует токены значений, сохраняя токены операций."""
        if token.type == "STRING":
            return str(token).removeprefix("q(").removesuffix(")")

        converter = TOKEN_CONVERTERS.get(token.type)
        if converter is None:
            return token

        try:
            return converter(token)
        except ValueError as error:
            raise VisitError(token.type, token, error) from error

    def definition(self, name, value):
        self.constans[name] = value

    def reference(self, name):
        if name not in self.constans:
            raise ValueError(f"Неизвестная константа: {name}")
        return self.constans[name]

    def expression(self, *items):
        stack = []
        for item in items:
            if not isinstance(item, Token):
                stack.append(item)
                continue

            if len(stack) < BINARY_ARITY:
                raise ValueError(f"Не хватает операндов для {items}")

            right = stack.pop()
            left = stack.pop()
            if not all(isinstance(value, (int, float)) 
                       for value in (left, right)):
                raise ValueError(f"Операция {item} требует чисел")

            result = OPERATIONS[item](left, right)
            if isinstance(result, complex):
                raise ValueError(f"Операция {item} дала комплексное число")
            stack.append(result)

        if len(stack) != 1:
            raise ValueError(f"Вырвжение должно дать одно значение")
        return stack.pop()

    def entry(self, name, value):
        return name, value

    def dictionary(self, *entries):
        return dict(entries)

    def start(self, *items):
        return items[-1]


def config_to_dict(text):
    return ConfigTransformer().transform(parse_config(text))

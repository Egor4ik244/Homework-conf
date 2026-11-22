from pathlib import Path
from lark import Lark, Tree, Transformer, v_args


GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")
PARSER = Lark.open(str(GRAMMAR_PATH), parser="lalr")


def parse_config(text):
    """Разобрать текст конфигурации и вернуть дерево разбора."""
    return PARSER.parse(text)

@v_args(inline=True)
class ConfigTransformer(Transformer):
    """Преобразует дерево разбора в значения Python."""

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        return float(token)

    def STRING(self, token):
        return str(token).removeprefix("q(").removesuffix(")")

    def entry(self, name, value):
        return name, value

    def dictionary(self, *entries):
        return dict(entries)

    def start(self, config):
        return config


def config_to_dict(text):
    return ConfigTransformer().transform(parse_config(text))
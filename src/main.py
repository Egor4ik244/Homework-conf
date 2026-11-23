import argparse
import sys
from pathlib import Path

import yaml
from lark.exceptions import UnexpectedInput, VisitError

from parser import config_to_dict


def main():
    cli = argparse.ArgumentParser(
        description="Преобразовать конфигурацию в YAML")
    cli.add_argument("-o", required=True, type=Path, help="Путь к файлу YAML")
    args = cli.parse_args()

    try:
        data = config_to_dict(sys.stdin.read())
        output = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        args.o.write_text(output, encoding="utf-8")
    except VisitError as error:
        print(f"Ошибка вычисления: {error.orig_exc}", file=sys.stderr)
        return 1
    except (UnexpectedInput, OSError, UnicodeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
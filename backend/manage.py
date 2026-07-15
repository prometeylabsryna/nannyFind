#!/usr/bin/env python3
import os
import sys

from decouple import config


def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        config("DJANGO_SETTINGS_MODULE", default="config.settings.develop"),
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install dependencies from requirements.txt."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

import logging.config
from release_notes import logger_config, generator, parser

logging.config.dictConfig(logger_config.LoggingConfig)
logger = logging.getLogger(__name__)


def run() -> None:
    print("Parsing...\n")

    result = parser.parse("release-notes.csv", "summary", "0.0.0")

    if len(result.rowParseErrors) > 0:
        print(f"\n\n{len(result.rowParseErrors)} errors were encountered")
        for _, parseError in result.rowParseErrors.items():
            print(f"{parseError}")

    print()

    yes_choices = ["yes", "y"]
    no_choices = ["no", "n"]

    while True:
        user_input = input("Generate markdown (yes/no)?: ")
        if user_input.lower() in yes_choices:
            buffer = generator.generate_markdown(result)
            print(f"\n\n{buffer.getvalue()}")
            break
        elif user_input.lower() in no_choices:
            print("\nExiting...")
            break
        else:
            print("Type yes or no")
            continue


if __name__ == "__main__":
    run()

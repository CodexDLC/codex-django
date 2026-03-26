"""
CLI Utilities
=============
Common helpers for the CLI.
"""


def run_django_command(args: list[str]) -> None:
    """
    Executes a Django management command within the current process context.
    Expects that DJANGO_SETTINGS_MODULE is already set.
    """
    from django.core.management import execute_from_command_line

    # The first argument to execute_from_command_line should be the program name
    # We use 'manage.py' to mimic standard behavior
    full_args = ["manage.py"] + args
    try:
        execute_from_command_line(full_args)
    except SystemExit as e:
        # Django's execute_from_command_line often calls sys.exit()
        if e.code != 0:
            print(f"\n[red]Command failed with exit code: {e.code}[/red]")
    except Exception as e:
        print(f"\n[red]Error executing command: {e}[/red]")

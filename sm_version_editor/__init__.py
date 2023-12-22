import click
from sm_version_editor.main import *


@click.group()
def cli():
    pass


cli.add_command(list_secrets)
cli.add_command(list_secret_versions)
cli.add_command(update_secret_version_stage)
cli.add_command(get_secret_value)
cli.add_command(create_secret)
cli.add_command(update_secret_value)
cli.add_command(delete_secret)
cli.add_command(restore_secret)

if __name__ == "__main__":
    cli()

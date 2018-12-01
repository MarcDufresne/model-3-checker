import click


def action(message: str, color: str = "blue"):
    click.secho(message, nl=False, fg=color)


def done():
    click.secho("Done!", fg="green")

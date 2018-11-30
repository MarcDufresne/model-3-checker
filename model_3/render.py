import os

import click
import jinja2
import ujson


@click.command()
def render():
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(cur_dir, os.path.pardir, 'docs', 'data.json'), mode="r") as f:
        data = ujson.loads(f.read())

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(cur_dir, 'templates')),
    )

    template = env.get_template("index.html")

    click.echo("Wrinting 'index.html' file...")
    with open(os.path.join(cur_dir, os.path.pardir, 'docs', 'index.html'), mode="w") as f:
        f.write(template.render(**data))

    click.secho("Done!", fg="green")


if __name__ == '__main__':
    render()

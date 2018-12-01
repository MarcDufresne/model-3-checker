import os

import click
import jinja2
import ujson

from model_3 import action, done


@click.command()
def render():
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    data_json_file = os.path.join(cur_dir, os.path.pardir, 'docs', 'data.json')

    action("Loading JSON data... ")
    with open(data_json_file, mode="r") as f:
        data = ujson.loads(f.read())
    done()

    action("Rendering template from data... ")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(cur_dir, 'templates')),
    )

    template = env.get_template("index.html")

    with open(os.path.join(cur_dir, os.path.pardir, 'docs', 'index.html'), mode="w") as f:
        f.write(template.render(**data))
    done()


if __name__ == '__main__':
    render()

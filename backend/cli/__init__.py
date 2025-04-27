import click

from .database import group_database
from .app import group_app

root = click.Group(commands=[group_database, group_app])
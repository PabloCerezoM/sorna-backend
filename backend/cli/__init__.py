import click

from .database import group_database

root = click.Group(commands=[ group_database])
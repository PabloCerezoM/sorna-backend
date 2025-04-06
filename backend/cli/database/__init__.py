import click

from .drop import cmd_drop
from .create import cmd_create

group_database = click.Group("database", commands=[cmd_drop, cmd_create])
import click

@click.command("create")
def cmd_create():
    import asyncio

    from backend.database.functions import create_database

    try:
        asyncio.run(create_database())
    except Exception as e:
        click.echo(f"Error creating database: {e}")
        return

    click.echo("Database created!")







import click

@click.command("drop")
def cmd_drop():
    import asyncio

    from backend.database.functions import drop_database

    try:
        asyncio.run(drop_database())
    except Exception as e:
        click.echo(f"Error dropping database: {e}")
        return

    click.echo("Database dropped!")




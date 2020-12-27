import click


@click.group()
def cli():
    pass


@cli.command()
def run_webapp():
    """Run a local flask web server"""
    from aspire.web import create_webapp
    create_webapp().run(host='0.0.0.0', port=8080, debug=True)


@cli.command()
def seed_demo_data():
    """Seed demo data into the database"""
    from aspire.app.Demo import seed_demo_data
    seed_demo_data()


@cli.command(short_help="Run the Rater, using a CSV as input")
@click.argument('rating-manual-id', type=int)
@click.argument('file_path')
def rate_from_csv(rating_manual_id, file_path):
    """This script opens a CSV and attempts to read each line to use as input for rating against the manual
    with the provided ID. """
    from aspire.app.Rating import rate_from_csv
    rate_from_csv(rating_manual_id, file_path)


cli.add_command(run_webapp)
cli.add_command(seed_demo_data)
cli.add_command(rate_from_csv)

if __name__ == '__main__':
    cli()

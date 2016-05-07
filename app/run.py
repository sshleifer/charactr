import click

from subprocess import call
import webbrowser as wb

from app.chat_to_csv import create_csvs


@click.command()
@click.option('--saved', default=False, is_flag=True, help='dont regenerate csvs')
def run(saved):
    if not saved:
        create_csvs()
    print "Serving scatterplot at localhost:8000"
    wb.open("http://localhost:8014")
    call("python -m SimpleHTTPServer 8014", shell=True)

if __name__ == '__main__':
    run()

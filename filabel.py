import click, configparser, sys, gh_api


def validate_config(config):
    try:
        config['github']
    except KeyError:
        sys.stderr.write('Auth configuration not usable!\n')
        exit(1)
    try:
        config['labels']
    except KeyError:
        sys.stderr.write('Labels configuration not usable!\n')
        exit(1)


def validate_slugs(reposlugs):
    for slug in reposlugs:
        try:
            _, _ = slug.split('/')
        except ValueError:
            sys.stderr.write(f'Reposlug {slug} not valid!\n')
            exit(1)


def load_config(configfile, labelsfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    config.read(labelsfile)
    validate_config(config)
    return config


def write_output(output):
    for repo in output.keys():
        res = output[repo]['result']
        r = click.style('REPO', bold=True)
        s = click.style(res, bold=True, fg=('green' if res == 'OK' else 'red'))
        click.echo(f'{r} {repo} - {s}')

        for pr in output[repo]['PRs'].keys():
            request = output[repo]['PRs'][pr]
            url = request['url']
            p = click.style('PR', bold=True)
            s = click.style(request['status'], bold=True, fg=('green' if request['status'] == 'OK' else 'red'))
            click.echo(f'  {p} {url} - {s}')
            if request['status'] == 'OK':
                labels = sorted(request['labels'], key=lambda tup: tup[0])
                for label in labels:
                    colour = 'white'
                    if label[1] == '+':
                        colour = 'green'
                    elif label[1] == '-':
                        colour = 'red'
                    o = click.style(label[1], fg=colour)
                    l = click.style(label[0], fg=colour)
                    click.echo(f'    {o} {l}')



@click.command()
@click.option('-a', '--config-auth', metavar='FILENAME', required=True, help='File with authorization configuration.')
@click.option('-b', '--base', metavar='BRANCH', help='Filter pulls by base (PR target) branch name.')
@click.option('-d/-D', '--delete-old/--no-delete-old', help='Delete labels that do not match anymore.', default=True,
              show_default=True)
@click.option('-l', '--config-labels', metavar='FILENAME', required=True, help='File with labels configuration.')
@click.option('-s', '--state', help='Filter pulls by state.', type=click.Choice(['open', 'closed', 'all']),
              default='open', show_default=True)
@click.argument('reposlugs', nargs=-1, metavar='[REPOSLUGS]...')
def main(config_auth, base, delete_old, config_labels, state, reposlugs):
    """
    CLI tool for filename-pattern-based labeling of GitHub PRs
    """
    config = load_config(config_auth, config_labels)
    validate_slugs(reposlugs)
    api = gh_api.Api(config['github']['token'], state, base)
    output = {}
    for slug in reposlugs:
        output[slug] = {}
        output[slug]['PRs'] = {}
        r = api.get_prs(slug)
        for pull in r['PR']:
            output[slug]['PRs'][pull] = api.label_pr(slug, pull, config['labels'], delete_old)
        output[slug]['result'] = 'OK' if r['status_code'] == 200 else 'FAIL'
    write_output(output)


if __name__ == '__main__':
    main()

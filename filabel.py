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
            user, repo = slug.split('/')
        except ValueError:
            sys.stderr.write(f'Reposlug {slug} not valid!\n')
            exit(1)


def load_config(configfile, labelsfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    config.read(labelsfile)
    validate_config(config)
    return config


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
    api = gh_api.Api(config['github']['token'])
    api.test_api()


if __name__ == '__main__':
    main()

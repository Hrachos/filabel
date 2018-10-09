import click


@click.command()
@click.option('--count')
def main(count):
    print('Ahoj')
    if count:
        print(count)


if __name__ == '__main__':
    main()

import logging
import chromalog
import click

from ziny.zine_factory import ZineFactory

chromalog.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s : %(message)s'
)

logger = logging.getLogger('Main App')

@click.command()
@click.option('--verbose', is_flag=True, help='More logs')
def main(verbose:bool) -> int:
    logger.info('Welcome to the Photo Zine Generator.')

    if verbose:
        force_verbose()

    factory = ZineFactory(image_folder = 'images/')
    factory.scan()

def force_verbose():
    logging.getLogger('Main App').setLevel(logging.DEBUG)
    logging.getLogger('Zine Factory').setLevel(logging.DEBUG)
    logging.getLogger('Zine Image Metadata').setLevel(logging.DEBUG)

if __name__ == '__main__':
    main()
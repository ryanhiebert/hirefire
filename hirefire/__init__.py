__version__ = '0.2a1'


def version_hook(config):
    config['metadata']['version'] = __version__

import logging
import coloredlogs


def make_logger(app):
    # SQL
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    # Colored
    coloredlogs.install(level='DEBUG')

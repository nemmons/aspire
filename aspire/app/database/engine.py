# https://towardsdatascience.com/use-flask-and-sqlalchemy-not-flask-sqlalchemy-5a64fafe22a4
# https://github.com/cosmicpython/code/issues/14#issuecomment-601699049
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from yaml import safe_load
import os

Base = declarative_base()


class ConnectionManager(object):
    @classmethod
    def read_config_file(cls):
        config_filename = os.path.abspath(os.path.dirname(__file__)) + '/config.yml'
        if os.path.exists(config_filename):
            with open(config_filename) as f:
                return safe_load(f)
        return {}

    def __init__(self, config=None):

        if config is not None:
            self.config = config
        else:
            self.config = self.read_config_file()

        if 'SQLALCHEMY_DATABASE_URI' not in self.config:
            raise Exception("Missing required configuration key ''SQLALCHEMY_DATABASE_URI'")

        self.engine = create_engine(
            self.config['SQLALCHEMY_DATABASE_URI'],
            connect_args={"check_same_thread": False},
            echo=False
        )

    def get_session_factory(self):
        factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return factory

    def get_session(self):
        factory = self.get_session_factory()
        return factory()


def setup_test_db_session(sqlalchemy_uri='sqlite:///:memory:'):
    from alembic import command
    from alembic.config import Config

    import warnings
    from sqlalchemy.exc import SAWarning
    warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning,
                            r'^sqlalchemy\.sql\.sqltypes$')

    manager = ConnectionManager({'SQLALCHEMY_DATABASE_URI': sqlalchemy_uri})
    session = manager.get_session()
    engine = manager.engine

    with engine.begin() as connection:
        alembic_cfg = Config(os.path.abspath(os.path.dirname(__file__)) + '/alembic.ini')
        alembic_cfg.attributes['connection'] = connection
        alembic_cfg.set_main_option('script_location', os.path.abspath(os.path.dirname(__file__)) + '/migrations')
        alembic_cfg.set_main_option('sqlalchemy.url', sqlalchemy_uri)
        command.upgrade(alembic_cfg, 'head')

    return session


def run_migrations(command_name='upgrade', target='head'):
    from alembic import command
    from alembic.config import Config

    import warnings
    from sqlalchemy.exc import SAWarning
    warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning,
                            r'^sqlalchemy\.sql\.sqltypes$')

    manager = ConnectionManager()
    engine = manager.engine

    with engine.begin() as connection:
        alembic_cfg = Config(os.path.abspath(os.path.dirname(__file__)) + '/alembic.ini')
        alembic_cfg.attributes['connection'] = connection
        alembic_cfg.set_main_option('script_location', os.path.abspath(os.path.dirname(__file__)) + '/migrations')
        alembic_cfg.set_main_option('sqlalchemy.url', manager.config['SQLALCHEMY_DATABASE_URI'])
        # command.upgrade(alembic_cfg, target)

        fn = getattr(command, command_name)
        fn(alembic_cfg, target)

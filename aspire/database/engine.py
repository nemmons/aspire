# https://towardsdatascience.com/use-flask-and-sqlalchemy-not-flask-sqlalchemy-5a64fafe22a4
# https://github.com/cosmicpython/code/issues/14#issuecomment-601699049
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.abspath(os.path.dirname(__file__)) + "/test.db"


def get_session_factory(engine=None):
    if engine is None:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return factory


Base = declarative_base()


def setup_test_db_session(url='sqlite:///:memory:'):
    from sqlalchemy import engine_from_config
    from alembic import command
    from alembic.config import Config
    import os

    import warnings
    from sqlalchemy.exc import SAWarning
    warnings.filterwarnings('ignore', r".*support Decimal objects natively", SAWarning,
                            r'^sqlalchemy\.sql\.sqltypes$')

    settings = {'sqlalchemy.url': url}
    engine = engine_from_config(settings, 'sqlalchemy.')
    factory = get_session_factory(engine)

    with engine.begin() as connection:
        alembic_cfg = Config(os.path.abspath(os.path.dirname(__file__)) + '/alembic.ini')
        alembic_cfg.attributes['connection'] = connection
        alembic_cfg.set_main_option('script_location', os.path.abspath(os.path.dirname(__file__)) + '/migrations')
        command.upgrade(alembic_cfg, 'head')

    session = factory()
    return session

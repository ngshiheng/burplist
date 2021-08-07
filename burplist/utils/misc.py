import logging
from datetime import datetime, timedelta
from functools import lru_cache

from burplist.database.models import Price, Product
from burplist.database.utils import db_connect
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def remove_stale_products_prices(stale_days: int = 7) -> None:
    """
    Remove stale products and prices which are not updated for N number of days
    """
    assert stale_days > 0, 'You are prohibited to delete everything using this script.'

    engine = db_connect()
    db_session = sessionmaker(bind=engine)

    with db_session.begin() as session:
        stale_products = session.query(Product).filter(Product.updated_on <= datetime.utcnow() - timedelta(days=stale_days))
        stale_products_count = stale_products.count()
        logger.info(f'Found {stale_products_count} stale products.')

        if stale_products_count < 1:
            logger.info('No stale products to delete.')
            return

        product_ids = [product.id for product in stale_products.all()]
        stale_prices = session.query(Price).filter(Price.product_id.in_(product_ids))
        logger.info(f'Found {stale_prices.count()} stale prices.')

        stale_prices.delete()
        stale_products.delete()
        logger.info(f'{stale_products_count} stale products deleted successfully.')


@lru_cache(maxsize=1280)
def get_popular_styles() -> set[str]:
    logger.info('Getting distinct beer styles from DB.')

    engine = db_connect()
    session = sessionmaker(bind=engine)()

    try:
        return {style[0] for style in session.query(Product.style).distinct() if style[0]}

    except ProgrammingError as exception:
        logger.exception(f'An unexpected error has occurred while running {__name__}.', extra=dict(exception=exception))
        return {''}

    finally:
        session.close()


@lru_cache(maxsize=1280)
def get_popular_brands() -> set[str]:
    logger.info('Getting distinct beer brands from DB.')

    engine = db_connect()
    session = sessionmaker(bind=engine)()

    try:
        return {brand[0] for brand in session.query(Product.brand).distinct() if brand[0]}

    except ProgrammingError as exception:
        logger.exception(f'An unexpected error has occurred while running {__name__}.', extra=dict(exception=exception))
        return {''}

    finally:
        session.close()

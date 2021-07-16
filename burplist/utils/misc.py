import logging
from datetime import datetime, timedelta

from burplist.database.models import Price, Product, db_connect
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


def remove_stale_products_prices(stale_days: int = 7):
    """
    Remove stale products and prices which are not updated for N number of days
    """
    assert stale_days > 0, 'You are prohibited to delete everything using this script.'

    engine = db_connect()
    session = sessionmaker(bind=engine)()

    try:
        stale_products = session.query(Product).filter(Product.updated_on <= datetime.utcnow() - timedelta(days=stale_days))
        stale_products_count = stale_products.count()
        logger.info(f'Found {stale_products_count} stale products.')

        if stale_products_count < 1:
            logger.info('No stale products to delete. Bye.')
            return

        product_ids = [product.id for product in stale_products.all()]
        stale_prices = session.query(Price).filter(Price.product_id.in_(product_ids))
        logger.info(f'Found {stale_prices.count()} stale prices.')

        stale_prices.delete()
        stale_products.delete()
        session.commit()
        logger.info(f'{stale_products_count} stale products deleted successfully.')

    except Exception as exception:
        logger.exception(f'An unexpected error has occurred while running {__name__}.', extra=dict(exception=exception))

    finally:
        session.close()

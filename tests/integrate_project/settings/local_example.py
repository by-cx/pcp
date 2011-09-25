import logging


logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s %(message)s',
)

logging.disable(logging.DEBUG)

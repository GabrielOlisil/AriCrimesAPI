import os

from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, get_app
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def load_cred():
    cred = None
    try:
        serviceAccountKey = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        cred = credentials.Certificate(serviceAccountKey)

        try:
            get_app()
            logger.info("Firebase Admin SDK já estava inicializado.")
        except ValueError:
            initialize_app(cred)
            logger.info("Firebase Admin SDK inicializado com sucesso.")


    except Exception as e:
        logger.error(e)

    return cred

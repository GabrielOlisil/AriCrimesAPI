import os

from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, get_app
import logging
import json

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def load_cred():
    cred = None
    try:
        serviceAccountKey = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

        if not serviceAccountKey:
            raise ValueError("A variável de ambiente FIREBASE_SERVICE_ACCOUNT_JSON não foi definida.")

        firebase_creds_dict = json.loads(serviceAccountKey)

        cred = credentials.Certificate(firebase_creds_dict)

        try:
            get_app()
            logger.info("Firebase Admin SDK já estava inicializado.")
        except ValueError:
            initialize_app(cred)
            logger.info("Firebase Admin SDK inicializado com sucesso.")


    except Exception as e:
        logger.error(e)

    return cred

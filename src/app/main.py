from .core.config import settings
from .api import router
from src.app.core.setup import create_application
from dotenv import load_dotenv
load_dotenv()


app = create_application(router=router, settings=settings)

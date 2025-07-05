from prometheus_fastapi_instrumentator import Instrumentator
from .core.setup import create_application
from .core.config import settings
from .api import router
from dotenv import load_dotenv
load_dotenv()


app = create_application(router=router, settings=settings)
Instrumentator().instrument(app).expose(app)

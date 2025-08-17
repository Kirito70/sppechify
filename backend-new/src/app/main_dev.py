from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .admin.initialize import create_admin_interface
from .api import router
from .core.config import settings
from .core.setup import create_application, lifespan_factory

admin = create_admin_interface()


@asynccontextmanager
async def lifespan_with_admin_no_tables(app: FastAPI) -> AsyncGenerator[None, None]:
    """Custom lifespan that includes admin initialization but skips table creation."""
    # Get the default lifespan but skip table creation
    default_lifespan = lifespan_factory(settings, create_tables_on_start=False)

    # Run the default lifespan initialization and our admin initialization
    async with default_lifespan(app):
        # Initialize admin interface if it exists
        if admin:
            # Initialize admin database and setup
            await admin.initialize()

        yield


# Create app without automatic table creation for development
app = create_application(
    router=router, 
    settings=settings, 
    lifespan=lifespan_with_admin_no_tables,
    create_tables_on_start=False
)

# Mount admin interface if enabled
if admin:
    app.mount(settings.CRUD_ADMIN_MOUNT_PATH, admin.app)
#!/usr/bin/env python3
"""
Create the first admin/superuser for the Japanese Learning App.
This script creates an admin user with all required fields.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.db.database import local_session
from app.core.security import get_password_hash
from app.crud.crud_users import crud_users
from app.schemas.user import UserCreateInternal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create the first admin user with all required Japanese learning fields."""
    try:
        async with local_session() as session:
            # Check if admin user already exists
            existing_user = await crud_users.get(db=session, username=settings.ADMIN_USERNAME)
            
            if existing_user:
                logger.info(f"Admin user '{settings.ADMIN_USERNAME}' already exists")
                return existing_user
            
            # Create admin user with all required fields
            admin_user_data = UserCreateInternal(
                name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                username=settings.ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            )
            
            # Create the user with Japanese learning defaults for admin
            new_user = await crud_users.create(db=session, object=admin_user_data)
            
            # Make user a superuser (update after creation)
            await crud_users.update(
                db=session,
                object=new_user,
                object_data={"is_superuser": True}
            )
            
            logger.info(f"✅ Admin user '{settings.ADMIN_USERNAME}' created successfully")
            logger.info(f"   📧 Email: {settings.ADMIN_EMAIL}")
            logger.info(f"   🔐 Password: {settings.ADMIN_PASSWORD}")
            logger.info(f"   👑 Superuser: True")
            
            return new_user
            
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")
        raise


async def main():
    """Main entry point."""
    logger.info("🚀 Creating first admin user for Japanese Learning App...")
    
    try:
        admin_user = await create_admin_user()
        logger.info("✅ Admin user setup completed!")
        
        logger.info("\n📋 Admin Login Details:")
        logger.info(f"   URL: http://localhost:8001/admin")
        logger.info(f"   Username: {settings.ADMIN_USERNAME}")
        logger.info(f"   Password: {settings.ADMIN_PASSWORD}")
        logger.info(f"   API Docs: http://localhost:8001/docs")
        
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
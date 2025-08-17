#!/usr/bin/env python3
"""
Create or update the admin/superuser for the Japanese Learning App.
This script ensures there's always a working admin user available.
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
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def ensure_admin_user():
    """Create or update the admin user to ensure it exists and has superuser privileges."""
    try:
        async with local_session() as session:
            # Check if admin user exists
            result = await session.execute(
                text('SELECT id, username, email, is_superuser FROM "user" WHERE username = :username'),
                {'username': settings.ADMIN_USERNAME}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                if existing_user.is_superuser:
                    logger.info(f"✅ Admin user '{settings.ADMIN_USERNAME}' already exists and is a superuser")
                else:
                    # Make existing user a superuser
                    await session.execute(
                        text('UPDATE "user" SET is_superuser = true WHERE username = :username'),
                        {'username': settings.ADMIN_USERNAME}
                    )
                    await session.commit()
                    logger.info(f"✅ Admin user '{settings.ADMIN_USERNAME}' updated to superuser")
                    
            else:
                # Create new admin user with all required fields
                query = text('''
                    INSERT INTO "user" (
                        name, username, email, hashed_password, is_superuser,
                        native_language, current_jlpt_level, target_jlpt_level, 
                        daily_study_goal, study_streak, best_streak, 
                        total_sentences_learned, total_study_time_minutes, 
                        preferred_study_time, study_reminders_enabled, 
                        audio_enabled, furigana_enabled, romaji_enabled, 
                        difficulty_preference
                    ) VALUES (
                        :name, :username, :email, :password, true,
                        'english', 'N5', 'N1', 
                        20, 0, 0, 
                        0, 0, 
                        'anytime', true, 
                        true, true, true, 
                        'adaptive'
                    )
                ''')
                
                await session.execute(query, {
                    'name': settings.ADMIN_NAME,
                    'username': settings.ADMIN_USERNAME,
                    'email': settings.ADMIN_EMAIL,
                    'password': get_password_hash(settings.ADMIN_PASSWORD)
                })
                await session.commit()
                logger.info(f"✅ Admin user '{settings.ADMIN_USERNAME}' created successfully")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error managing admin user: {e}")
        return False


async def main():
    """Main entry point."""
    logger.info("🚀 Ensuring admin user exists for Japanese Learning App...")
    
    success = await ensure_admin_user()
    
    if success:
        logger.info("\n🎉 Admin user setup completed!")
        logger.info("\n📋 Admin Login Details:")
        logger.info(f"   👑 Username: {settings.ADMIN_USERNAME}")
        logger.info(f"   📧 Email: {settings.ADMIN_EMAIL}")
        logger.info(f"   🔐 Password: {settings.ADMIN_PASSWORD}")
        logger.info(f"   🌐 Admin Panel: http://localhost:8001/admin")
        logger.info(f"   📚 API Docs: http://localhost:8001/docs")
        logger.info(f"   🔍 Health Check: http://localhost:8001/api/v1/sentences")
    else:
        logger.error("❌ Failed to setup admin user")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
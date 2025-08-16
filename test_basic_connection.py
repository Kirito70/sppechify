#!/usr/bin/env python3
"""
Simple Database Connection Test
Tests basic PostgreSQL connectivity without async dependencies
"""
import sys

def test_basic_connection():
    """Test basic database connection using psycopg2"""
    print("🔍 Testing basic database connection...")
    
    try:
        import psycopg2
        print("✅ psycopg2 available")
    except ImportError:
        try:
            # Try to install psycopg2-binary if not available
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'])
            import psycopg2
            print("✅ psycopg2 installed and imported")
        except Exception as e:
            print(f"❌ Could not install/import psycopg2: {e}")
            return False
    
    # Database connection parameters for external PostgreSQL
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'japanese_learning',
        'user': 'postgres',
        'password': 'admin'
    }
    
    try:
        # Test connection
        print(f"🔗 Attempting connection to postgres://{conn_params['user']}@{conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connected successfully!")
        print(f"📊 PostgreSQL Version: {version[:80]}...")
        
        # Test database exists
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()[0]
        print(f"📂 Current Database: {current_db}")
        
        # List existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📋 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"   • {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        print(f"💡 Make sure PostgreSQL is running: docker-compose up postgres")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Basic Database Connection Test")
    print("=" * 50)
    
    success = test_basic_connection()
    
    if success:
        print("\n🎉 Database connection test passed!")
        print("💡 Next: Run the full SQLModel test with: python backend/test_db_connection.py")
        sys.exit(0)
    else:
        print("\n💥 Database connection test failed!")
        print("💡 Check if PostgreSQL is running: docker-compose ps")
        sys.exit(1)
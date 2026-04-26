"""
Interactive setup script for ARCS environment configuration
"""

def setup_mongodb():
    print("=" * 60)
    print("ARCS MongoDB Configuration")
    print("=" * 60)
    print()
    print("You have two options:")
    print("1. Use MongoDB Atlas (Cloud) - Recommended")
    print("2. Use Local MongoDB (Docker)")
    print()
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📝 MongoDB Atlas Setup")
        print("-" * 60)
        print("Your connection string:")
        print("mongodb://tanuj:<db_password>@ac-utvb68u-shard-00-00.ushqevx.mongodb.net:27017,...")
        print()
        password = input("Enter your MongoDB Atlas password: ").strip()
        
        mongodb_url = f"mongodb://tanuj:{password}@ac-utvb68u-shard-00-00.ushqevx.mongodb.net:27017,ac-utvb68u-shard-00-01.ushqevx.mongodb.net:27017,ac-utvb68u-shard-00-02.ushqevx.mongodb.net:27017/?ssl=true&replicaSet=atlas-a4hgsp-shard-0&authSource=admin&appName=Major"
        
    else:
        print("\n📝 Local MongoDB Setup")
        print("-" * 60)
        mongodb_url = "mongodb://localhost:27017/"
        print("Using local MongoDB at: mongodb://localhost:27017/")
    
    # Write .env file
    env_content = f"""# MongoDB Configuration
MONGODB_URL={mongodb_url}

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env file")
    print("\nYou can now start the backend with:")
    print("  python main.py")
    print()

if __name__ == "__main__":
    setup_mongodb()

"""
Database Seed Script

Creates sample data for development and testing:
- 3 users (farmer, vet, admin)
- Sample reports with various statuses
- Test sessions and feedback

Run with: python scripts/seed_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random

from app.core.config import settings
from app.core.security import get_password_hash


SAMPLE_USERS = [
    {
        "email": "farmer@test.com",
        "full_name": "John Farmer",
        "role": "farmer",
        "phone": "+1234567890",
        "password": "farmer123",
        "location": {
            "type": "Point",
            "coordinates": [-122.4194, 37.7749]  # San Francisco
        }
    },
    {
        "email": "vet@test.com",
        "full_name": "Dr. Sarah Veterinarian",
        "role": "vet",
        "phone": "+1234567891",
        "password": "vet123",
        "location": {
            "type": "Point",
            "coordinates": [-122.4294, 37.7849]
        }
    },
    {
        "email": "admin@test.com",
        "full_name": "Admin User",
        "role": "admin",
        "phone": "+1234567892",
        "password": "admin123"
    }
]


SAMPLE_DISEASES = [
    "Late Blight",
    "Early Blight",
    "Powdery Mildew",
    "Foot and Mouth Disease",
    "Mastitis",
    "Pneumonia"
]


SAMPLE_SYMPTOMS = [
    "Dark brown spots on leaves with white fuzzy growth underneath",
    "Yellowing leaves with dark spots spreading rapidly",
    "White powdery coating on leaves and stems",
    "Blisters on mouth, feet, and udder with fever",
    "Swollen udder with abnormal milk and fever",
    "Difficulty breathing, coughing, and nasal discharge"
]


async def seed_database():
    """Seed the database with sample data"""
    
    print(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        # Test connection
        await db.command("ping")
        print("✓ Connected to MongoDB")
        
        # Clear existing data
        print("\nClearing existing data...")
        await db.users.delete_many({})
        await db.reports.delete_many({})
        await db.sessions.delete_many({})
        await db.feedback.delete_many({})
        await db.notifications.delete_many({})
        print("✓ Cleared existing data")
        
        # Create users
        print("\nCreating users...")
        user_ids = {}
        for user_data in SAMPLE_USERS:
            password = user_data.pop("password")
            user_data["hashed_password"] = get_password_hash(password)
            user_data["created_at"] = datetime.utcnow()
            user_data["is_active"] = True
            
            result = await db.users.insert_one(user_data)
            user_ids[user_data["role"]] = str(result.inserted_id)
            print(f"  ✓ Created {user_data['role']}: {user_data['email']}")
        
        # Create reports
        print("\nCreating sample reports...")
        farmer_id = user_ids["farmer"]
        vet_id = user_ids["vet"]
        
        for i in range(15):
            # Randomize data
            disease = random.choice(SAMPLE_DISEASES)
            symptom = random.choice(SAMPLE_SYMPTOMS)
            confidence = random.uniform(0.7, 0.95)
            status = random.choice(["pending", "in_progress", "completed"])
            priority = random.choice(["normal", "high", "urgent"])
            
            # Create report
            report = {
                "farmer_id": farmer_id,
                "status": status,
                "priority": priority,
                "symptoms": {
                    "text": symptom,
                    "images": [f"/uploads/sample_{i}.jpg"] if random.random() > 0.3 else [],
                    "location": {
                        "type": "Point",
                        "coordinates": [
                            -122.4194 + random.uniform(-0.1, 0.1),
                            37.7749 + random.uniform(-0.1, 0.1)
                        ]
                    }
                },
                "ai_prediction": {
                    "disease_label": disease,
                    "confidence": round(confidence, 3),
                    "explanation": f"Analysis indicates {disease} based on symptom patterns.",
                    "highlighted_features": ["spots", "leaves", "fever"][:random.randint(1, 3)],
                    "similar_cases": []
                },
                "animal_type": None,
                "crop_type": "tomato" if "Blight" in disease else None,
                "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                "updated_at": datetime.utcnow() - timedelta(days=random.randint(0, 15))
            }
            
            # Add vet data for non-pending reports
            if status != "pending":
                report["vet_id"] = vet_id
                report["vet_notes"] = f"Examined case {i+1}. Diagnosis confirmed."
                report["diagnosis"] = disease
                report["treatment"] = "Prescribed appropriate medication and care instructions."
            
            if status == "completed":
                report["closed_at"] = datetime.utcnow() - timedelta(days=random.randint(0, 10))
                report["prescription"] = f"Prescription for {disease}: Follow treatment plan for 14 days."
            
            result = await db.reports.insert_one(report)
            print(f"  ✓ Created report {i+1}: {disease} ({status})")
        
        # Create sample session
        print("\nCreating sample session...")
        sample_report = await db.reports.find_one({"status": "completed"})
        if sample_report:
            session = {
                "report_id": str(sample_report["_id"]),
                "farmer_id": farmer_id,
                "vet_id": vet_id,
                "call_start": datetime.utcnow() - timedelta(days=5, hours=2),
                "call_end": datetime.utcnow() - timedelta(days=5, hours=1, minutes=45),
                "duration_seconds": 900,  # 15 minutes
                "session_notes": "Discussed symptoms and treatment plan via video call.",
                "active": False
            }
            await db.sessions.insert_one(session)
            print("  ✓ Created sample video session")
        
        # Create sample feedback
        print("\nCreating sample feedback...")
        for i in range(3):
            feedback = {
                "report_id": "sample_report_" + str(i),
                "vet_id": vet_id,
                "original_prediction": random.choice(SAMPLE_DISEASES),
                "corrected_prediction": random.choice(SAMPLE_DISEASES),
                "confidence": random.uniform(0.7, 0.9),
                "notes": "Corrected based on additional visual inspection.",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                "used_for_training": False
            }
            await db.feedback.insert_one(feedback)
            print(f"  ✓ Created feedback entry {i+1}")
        
        # Create indexes
        print("\nCreating database indexes...")
        await db.users.create_index("email", unique=True)
        await db.users.create_index("role")
        await db.reports.create_index("farmer_id")
        await db.reports.create_index("vet_id")
        await db.reports.create_index("status")
        await db.reports.create_index([("symptoms.location", "2dsphere")])
        await db.sessions.create_index("report_id")
        await db.feedback.create_index("report_id")
        print("✓ Indexes created")
        
        print("\n" + "="*60)
        print("Database seeded successfully!")
        print("="*60)
        print("\nTest Credentials:")
        print("-" * 60)
        for user in SAMPLE_USERS:
            email = user["email"]
            role = user["role"]
            # Password was already popped, but we know what they are
            passwords = {"farmer@test.com": "farmer123", "vet@test.com": "vet123", "admin@test.com": "admin123"}
            print(f"{role.upper():10} | Email: {email:25} | Password: {passwords[email]}")
        print("-" * 60)
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    print("="*60)
    print("FarmPulse AI - Database Seed Script")
    print("="*60)
    asyncio.run(seed_database())

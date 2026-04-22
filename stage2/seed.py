import json
import os
from stage2.database import create_db, create_profile, get_profile_by_name


def seed_database():
    """
    Load the 2026 profiles from the seed_profiles.json file
    and insert them into the DB, preventing duplicates by checking if the profile
    exists already before inserting.
    """
    create_db()

    seed_file = os.path.join(os.path.dirname(__file__), "seed_profiles.json")
    
    if not os.path.exists(seed_file):
        print(f"Seed file not found: {seed_file}")
        return
    
    with open(seed_file, 'r') as f:
        data = json.load(f)
    
    profiles = data.get("profiles", [])
    print(f"Found {len(profiles)} profiles to seed")
    
    seeded_count = 0
    skipped_count = 0

    for profile_data in profiles:
        existing = get_profile_by_name(profile_data['name'])
        if not existing:
            create_profile(profile_data)
            seeded_count += 1
            if seeded_count % 100 == 0:
                print(f"Seeded {seeded_count} profiles...")
        else:
            skipped_count += 1
    
    print(f"\nSeeding completed!")
    print(f"Total seeded: {seeded_count}")
    print(f"Total skipped (already exist): {skipped_count}")


if __name__ == "__main__":
    seed_database()
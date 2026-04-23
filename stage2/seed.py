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
    
    try:
        with open(seed_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading seed file: {e}")
        return
    
    profiles = data.get("profiles", [])
    print(f"Found {len(profiles)} profiles to seed")
    
    seeded_count = 0
    skipped_count = 0
    error_count = 0

    for i, profile_data in enumerate(profiles):
        try:
            existing = get_profile_by_name(profile_data['name'])
            if not existing:
                create_profile(profile_data)
                seeded_count += 1
            else:
                skipped_count += 1
            
            # Progress every 100 profiles
            if (i + 1) % 100 == 0:
                print(f"Progress: {i + 1}/{len(profiles)} - Seeded: {seeded_count}, Skipped: {skipped_count}")
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Print first 5 errors
                print(f"Error inserting {profile_data.get('name')}: {e}")
            if error_count == 6:
                print("(suppressing further error messages)")
    
    print(f"\n{'='*50}")
    print(f"Seeding completed!")
    print(f"Total seeded: {seeded_count}")
    print(f"Total skipped (already exist): {skipped_count}")
    print(f"Total errors: {error_count}")
    print(f"{'='*50}")


if __name__ == "__main__":
    seed_database()
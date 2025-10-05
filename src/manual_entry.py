"""
Manual data entry tool for artist information
"""
from database_manager import ArtDatabase

def enter_artist_data():
    """Interactive tool to manually enter artist data"""
    db = ArtDatabase()
    
    print("=== Artist Data Entry ===\n")
    
    name = input("Artist name: ").strip()
    
    # Check if artist already exists
    existing = db.get_artist(name)
    if existing:
        print(f"\n{name} already in database. Update? (y/n): ")
        if input().lower() != 'y':
            return
    
    print(f"\nEntering data for: {name}")
    print("(Press Enter to skip any field)\n")
    
    education = input("Education (e.g., 'BFA Yale, MFA RISD'): ").strip()
    art_style = input("Art style/medium (e.g., 'Abstract painting, mixed media'): ").strip()
    gallery = input("Gallery representation: ").strip()
    exhibitions = input("Notable exhibitions: ").strip()
    website = input("Website URL: ").strip()
    
    artist_data = {
        'name': name,
        'education': education or None,
        'art_style': art_style or None,
        'gallery_representation': gallery or None,
        'exhibition_history': exhibitions or None,
        'website': website or None
    }
    
    artist_id = db.add_artist(artist_data)
    print(f"\n✅ Artist data saved! (ID: {artist_id})")

if __name__ == "__main__":
    enter_artist_data()
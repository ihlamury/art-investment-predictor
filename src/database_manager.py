"""
Database Manager - Store artist and artwork data
"""
import sqlite3
import json
from datetime import datetime
import os

class ArtDatabase:
    def __init__(self, db_path='database/art_data.db'):
        """Initialize database connection"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                education TEXT,
                art_style TEXT,
                gallery_representation TEXT,
                exhibition_history TEXT,
                website TEXT,
                data_collected_date TEXT,
                raw_data TEXT
            )
        ''')
        
        # Artworks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artworks (
                artwork_id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER,
                title TEXT,
                year INTEGER,
                medium TEXT,
                dimensions TEXT,
                price REAL,
                source TEXT,
                analysis_date TEXT,
                FOREIGN KEY (artist_id) REFERENCES artists (id)
            )
        ''')
        
        # Analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                artwork_id INTEGER,
                recommendation TEXT,
                reasoning TEXT,
                confidence_score REAL,
                analysis_date TEXT,
                FOREIGN KEY (artwork_id) REFERENCES artworks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_artist(self, artist_data):
        """Add or update artist information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert exhibition_history to JSON string if it's a list
        exhibition_history = artist_data.get('exhibition_history')
        if isinstance(exhibition_history, list):
            exhibition_history = json.dumps(exhibition_history)

        cursor.execute('''
            INSERT OR REPLACE INTO artists
            (name, education, art_style, gallery_representation,
             exhibition_history, website, data_collected_date, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            artist_data['name'],
            artist_data.get('education'),
            artist_data.get('art_style'),
            artist_data.get('gallery_representation'),
            exhibition_history,
            artist_data.get('website'),
            datetime.now().isoformat(),
            json.dumps(artist_data.get('raw_data', {}))
        ))

        conn.commit()
        artist_id = cursor.lastrowid
        conn.close()
        return artist_id
    
    def get_artist(self, name):
        """Retrieve artist data by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM artists WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()

        if result:
            # Parse exhibition_history from JSON if it's a JSON string
            exhibition_history = result[5]
            try:
                if exhibition_history and exhibition_history.startswith('['):
                    exhibition_history = json.loads(exhibition_history)
            except:
                pass  # Keep as string if JSON parsing fails

            return {
                'artist_id': result[0],
                'name': result[1],
                'education': result[2],
                'art_style': result[3],
                'gallery_representation': result[4],
                'exhibition_history': exhibition_history,
                'website': result[6],
                'data_collected_date': result[7]
            }
        return None
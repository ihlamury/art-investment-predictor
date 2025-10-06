"""
Artist information scraper
"""
from database_manager import ArtDatabase
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import json

load_dotenv()

class ArtistScraper:
    def __init__(self):
        """Initialize scraper with Claude API"""
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not found in .env")
        self.client = Anthropic(api_key=api_key)
    
    def fetch_website_content(self, url):
        """Fetch website HTML content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_text_from_html(self, html):
        """Extract clean text from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def analyze_with_claude(self, artist_name, website_text):
        """Use Claude to extract structured artist information"""
        prompt = f"""
        Analyze this artist's website content and extract key information.
        
        Artist name: {artist_name}
        
        Website content:
        {website_text[:8000]}  # Limit to avoid token limits
        
        Extract and return ONLY a JSON object with these fields (use null if not found):
        {{
            "name": "{artist_name}",
            "education": "where they studied (degrees, institutions)",
            "art_style": "their artistic style and medium",
            "gallery_representation": "galleries that represent them",
            "exhibition_history": "notable exhibitions or shows",
            "website": "website URL",
            "career_stage": "emerging/mid-career/established",
            "notable_achievements": "awards, residencies, publications"
        }}
        
        Return ONLY valid JSON, no other text.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error analyzing with Claude: {e}")
            return None
    
    def scrape_artist_full(self, artist_name, base_url, save_to_db=True):
        """
        Scrape multiple pages of an artist's website
        
        Args:
            artist_name (str): Artist's name
            base_url (str): Base website URL
            save_to_db (bool): Whether to save to database
            
        Returns:
            dict: Extracted artist information
        """
        print(f"Scraping website for {artist_name}...")
        print(f"Base URL: {base_url}\n")
        
        # Common page paths to check
        pages_to_check = [
            '',           # Homepage
            '/about',
            '/bio',
            '/cv',
            '/exhibitions',
            '/resume'
        ]
        
        all_text = []
        
        for page in pages_to_check:
            url = base_url.rstrip('/') + page
            print(f"Fetching: {url}")
            
            html = self.fetch_website_content(url)
            if html:
                text = self.extract_text_from_html(html)
                all_text.append(text)
                print(f"  ✓ Extracted {len(text)} characters")
            else:
                print(f"  ✗ Failed to fetch")
        
        # Combine all text
        combined_text = '\n\n'.join(all_text)
        print(f"\nTotal extracted: {len(combined_text)} characters")
        
        # Analyze with Claude
        print("Analyzing with Claude...\n")
        artist_data = self.analyze_with_claude(artist_name, combined_text)
        
        if artist_data:
            artist_data['website'] = base_url
            print("✅ Successfully extracted artist data:")
            print(json.dumps(artist_data, indent=2))
            
            # Save to database
            if save_to_db:
                print("\nSaving to database...")
                db = ArtDatabase()
                artist_id = db.add_artist(artist_data)
                print(f"✅ Saved to database (Artist ID: {artist_id})")
        
        return artist_data

if __name__ == "__main__":
    scraper = ArtistScraper()
    
    artist_name = input("Artist name: ").strip()
    website_url = input("Website URL: ").strip()
    
    # Use the full scraper that checks multiple pages
    result = scraper.scrape_artist_full(artist_name, website_url)
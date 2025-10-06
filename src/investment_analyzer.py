"""
Investment Analyzer - Analyzes artist data to make investment recommendations
"""
from anthropic import Anthropic
from dotenv import load_dotenv
from database_manager import ArtDatabase
import os
import json

load_dotenv()

class InvestmentAnalyzer:
    def __init__(self):
        """Initialize analyzer with Claude API"""
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            raise ValueError("CLAUDE_API_KEY not found in .env")
        self.client = Anthropic(api_key=api_key)
        self.db = ArtDatabase()
    
    def analyze_artist(self, artist_name, artwork_price=None):
        """
        Analyze an artist for investment potential
        
        Args:
            artist_name (str): Artist's name
            artwork_price (float): Price of specific artwork (optional)
            
        Returns:
            dict: Investment analysis with recommendation
        """
        # Get artist data from database
        artist = self.db.get_artist(artist_name)
        
        if not artist:
            return {
                "error": f"Artist '{artist_name}' not found in database. Please scrape their data first."
            }
        
        # Build analysis prompt
        prompt = f"""
        You are an art investment analyst. Analyze this artist's data and provide an investment recommendation.
        
        Artist: {artist['name']}
        Education: {artist['education'] or 'Unknown'}
        Art Style: {artist['art_style'] or 'Unknown'}
        Gallery Representation: {artist['gallery_representation'] or 'None listed'}
        Exhibition History: {artist['exhibition_history'] or 'Limited information'}
        Career Stage: Based on data, assess if emerging/mid-career/established
        
        {"Current artwork price: $" + str(artwork_price) if artwork_price else "No specific artwork price provided"}
        
        Provide analysis in this JSON format:
        {{
            "recommendation": "BUY" or "PASS" or "RESEARCH MORE",
            "confidence": "HIGH" or "MEDIUM" or "LOW",
            "reasoning": "2-3 sentence explanation",
            "positive_factors": ["factor 1", "factor 2", ...],
            "risk_factors": ["risk 1", "risk 2", ...],
            "price_assessment": "fair/undervalued/overvalued/unknown" (if price provided),
            "investment_horizon": "short-term/medium-term/long-term",
            "comparable_artists": ["similar artist 1", "similar artist 2"]
        }}
        
        Consider:
        - Education quality (prestigious schools = positive)
        - Gallery representation (established galleries = positive)
        - Exhibition history (museums/established venues = positive)
        - Career trajectory (consistent growth = positive)
        - Market saturation (too commercial = risk)
        - For emerging artists, focus on potential; for established, focus on stability
        
        Return ONLY valid JSON.
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
            
            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            analysis = json.loads(json_str)
            analysis['artist_name'] = artist_name
            analysis['analyzed_date'] = artist['data_collected_date']
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {e}"
            }
    
    def generate_report(self, analysis):
        """Format analysis as readable report"""
        if 'error' in analysis:
            return f"ERROR: {analysis['error']}"
        
        report = f"""
{'='*60}
INVESTMENT ANALYSIS REPORT
{'='*60}

Artist: {analysis['artist_name']}
Analyzed: {analysis['analyzed_date']}

RECOMMENDATION: {analysis['recommendation']}
Confidence Level: {analysis['confidence']}

{analysis['reasoning']}

POSITIVE FACTORS:
{chr(10).join('  + ' + factor for factor in analysis['positive_factors'])}

RISK FACTORS:
{chr(10).join('  - ' + factor for factor in analysis['risk_factors'])}

Price Assessment: {analysis.get('price_assessment', 'N/A')}
Investment Horizon: {analysis['investment_horizon']}

Comparable Artists:
{chr(10).join('  • ' + artist for artist in analysis['comparable_artists'])}

{'='*60}
"""
        return report

if __name__ == "__main__":
    analyzer = InvestmentAnalyzer()
    
    # Test analysis
    artist_name = input("Artist name: ").strip()
    price_input = input("Artwork price (press Enter to skip): ").strip()
    price = float(price_input) if price_input else None
    
    print("\nAnalyzing...\n")
    analysis = analyzer.analyze_artist(artist_name, price)
    
    report = analyzer.generate_report(analysis)
    print(report)
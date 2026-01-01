import requests
from datetime import date
import random
import logging
import os
import sys
from requests_oauthlib import OAuth1

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class FortniteKelsierBot:
    def __init__(self):
        # OAuth 1.0a - 4 CREDENCIALES NECESARIAS
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Fortnite API (opcional)
        self.fortnite_api_key = os.getenv('FORTNITE_API_KEY')
        
        self.verify_credentials()
        self.last_appearance = date(2021, 11, 7)
        # Usar API v1.1 que es más estable
        self.api_url = "https://api.twitter.com/1.1/statuses/update.json"
        self.hashtags = ["#Fortnite", "#Kelsier", "#Mistborn", "#Cosmere"]
        self.fortnite_api_url = "https://fortniteapi.io/v2/shop"
    
    def verify_credentials(self):
        """Verify all 4 OAuth 1.0a credentials are set"""
        missing = []
        if not self.api_key: missing.append("TWITTER_API_KEY")
        if not self.api_secret: missing.append("TWITTER_API_SECRET")
        if not self.access_token: missing.append("TWITTER_ACCESS_TOKEN")
        if not self.access_token_secret: missing.append("TWITTER_ACCESS_TOKEN_SECRET")
        
        if missing:
            raise ValueError(f"❌ Missing: {', '.join(missing)}")
        
        logging.info("✅ All 4 Twitter credentials verified")
    
    def check_shop_for_kelsier(self):
        """Check if Kelsier skin is in the current item shop"""
        try:
            logging.info("🛍️ Checking Fortnite item shop...")
            
            headers = {}
            if self.fortnite_api_key:
                headers['Authorization'] = self.fortnite_api_key
            
            response = requests.get(self.fortnite_api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                shop_data = response.json()
                shop_items = shop_data.get('shop', [])
                
                for item in shop_items:
                    name = item.get('name', '').lower()
                    if 'kelsier' in name:
                        logging.info("🎉 KELSIER FOUND!")
                        return True
                
                logging.info("❌ Kelsier not found")
                return False
            else:
                logging.warning(f"⚠️ Could not fetch shop: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            return False
    
    def calculate_days(self):
        today = date.today()
        days = (today - self.last_appearance).days
        years = days / 365.25
        return days, years
    
    def generate_tweet_text(self):
        """Generate tweet text"""
        days, years = self.calculate_days()
        
        # Check shop
        kelsier_in_shop = self.check_shop_for_kelsier()

        if kelsier_in_shop:
            phrases = [
                f"🎉 Kelsier has RETURNED to Fortnite after {days} days ({years:.2f} years)!",
                f"🚀 Kelsier is BACK after {days} days ({years:.2f} years)!",
                f"✨ Kelsier FINALLY returns after {days} days ({years:.2f} years)!",
            ]
        else:
            phrases = [
                f"Day {days}: Kelsier absent for {days} days ({years:.2f} years).",
                f"{days} days since Kelsier in Fortnite ({years:.2f} years).",
                f"Kelsier watch: {days} days without appearing ({years:.2f} years).",
                f"Kelsier remains trapped in the Pits of Hathsin while his skin has been absent from Fortnite for {days} days ({years:.2f} years).",
                f"The Survivor of Hathsin hasn't survived the Fortnite Item Shop rotation for {days} days ({years:.2f} years).",
                f"Not even with Allomancy could Kelsier return to the Fortnite Shop after {days} days ({years:.2f} years).",
                f"The Lord of Scars has been scarred by absence: {days} days ({years:.2f} years) without Kelsier in Fortnite.",
                f"Mistborn legend Kelsier continues to be a 'what if' in Fortnite after {days} days ({years:.2f} years).",
                f"The Crew's leader is missing from the Fortnite Crew's Item Shop for {days} days ({years:.2f} years).",
                f"Kelsier's rebellion against the Fortnite Item Shop continues: {days} days ({years:.2f} years) of resistance.",
                f"The 'too angry to die' Mistborn hasn't been angry enough to return to Fortnite in {days} days ({years:.2f} years).",
                f"Even the Steel Inquisitors would pity Kelsier's {days}-day ({years:.2f} years) Fortnite absence.",
                f"The Eleventh Metal remains the eleventh-hour hope after {days} days ({years:.2f} years) without Kelsier in Fortnite.",
            ]
        
        main_text = random.choice(phrases)
        hashtags_text = " ".join(self.hashtags)
        full_tweet = f"{main_text} {hashtags_text}"
        
        if len(full_tweet) > 280:
            full_tweet = f"{main_text} #Fortnite #Kelsier #Mistborn"
        
        return full_tweet
    
    def post_tweet(self):
        """Post tweet using Twitter API v1.1 (more stable)"""
        tweet_text = self.generate_tweet_text()
        
        # OAuth 1.0a
        auth = OAuth1(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_token_secret
        )
        
        # Headers para evitar Cloudflare
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        # API v1.1 usa "status" en lugar de "text"
        payload = {"status": tweet_text}
        
        try:
            response = requests.post(
                self.api_url, 
                auth=auth, 
                headers=headers,
                data=payload,  # v1.1 usa data, no json
                timeout=30
            )
            
            logging.info(f"📊 API Response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                logging.info("✅ Tweet posted successfully!")
                return True
            else:
                # Mostrar error completo para debugging
                error_msg = response.text[:500] if response.text else "No error message"
                logging.error(f"❌ Error {response.status_code}: {error_msg}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Connection error: {e}")
            return False

def main():
    try:
        logging.info("🤖 Starting Fortnite Kelsier Bot (API v1.1)...")
        bot = FortniteKelsierBot()
        success = bot.post_tweet()
        
        if success:
            logging.info("🎉 Success!")
            sys.exit(0)
        else:
            logging.error("💥 Failed")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

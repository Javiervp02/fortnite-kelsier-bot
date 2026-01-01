import requests
from datetime import date
import random
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class FortniteKelsierBot:
    def __init__(self):
        # Solo necesitas UN Bearer Token
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Fortnite API (opcional)
        self.fortnite_api_key = os.getenv('FORTNITE_API_KEY')
        
        self.verify_credentials()
        self.last_appearance = date(2021, 11, 7)
        self.api_url = "https://api.twitter.com/2/tweets"
        self.hashtags = ["#Fortnite", "#Kelsier", "#Mistborn", "#Cosmere"]
        self.fortnite_api_url = "https://fortniteapi.io/v2/shop"
    
    def verify_credentials(self):
        """Verify Bearer Token is set"""
        if not self.bearer_token:
            raise ValueError("❌ Missing TWITTER_BEARER_TOKEN")
        
        logging.info("✅ Twitter Bearer Token verified")
    
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
            ]
        
        main_text = random.choice(phrases)
        hashtags_text = " ".join(self.hashtags)
        full_tweet = f"{main_text} {hashtags_text}"
        
        if len(full_tweet) > 280:
            full_tweet = f"{main_text} #Fortnite #Kelsier #Mistborn"
        
        return full_tweet
    
    def post_tweet(self):
        """Post tweet using Bearer Token"""
        tweet_text = self.generate_tweet_text()
        
        # SIMPLE: Solo Bearer Token
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"text": tweet_text}
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                logging.info("✅ Tweet posted!")
                return True
            else:
                logging.error(f"❌ Error {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Connection error: {e}")
            return False

def main():
    try:
        logging.info("🤖 Starting Fortnite Kelsier Bot...")
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

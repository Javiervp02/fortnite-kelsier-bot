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
    handlers=[
        logging.StreamHandler(sys.stdout)  # Important for GitHub Actions
    ]
)

class FortniteKelsierBot:
    def __init__(self):
        # Load from environment variables
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.verify_credentials()
        self.last_appearance = date(2021, 11, 7)
        self.api_url = "https://api.twitter.com/2/tweets"
        self.hashtags = ["#Fortnite", "#Kelsier", "#Mistborn", "#Cosmere"]
    
    def verify_credentials(self):
        """Verify credentials are set"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            missing = []
            if not self.api_key: missing.append("TWITTER_API_KEY")
            if not self.api_secret: missing.append("TWITTER_API_SECRET")
            if not self.access_token: missing.append("TWITTER_ACCESS_TOKEN")
            if not self.access_token_secret: missing.append("TWITTER_ACCESS_TOKEN_SECRET")
            
            error_msg = f"Missing credentials: {', '.join(missing)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        logging.info("✅ All credentials verified")
    
    def calculate_days(self):
        today = date.today()
        days = (today - self.last_appearance).days
        years = days / 365.25
        return days, years
    
    def generate_tweet_text(self):
        days, years = self.calculate_days()
        
        phrases = [
            f"The Kelsier Fortnite skin has been absent from the Fortnite Item Shop for {days} days ({years:.2f} years).",
            f"It's been {days} days ({years:.2f} years) since Kelsier last appeared in the Fortnite Item Shop.",
            f"Day {days} of waiting for Kelsier's return to Fortnite. That's {years:.2f} years!",
            f"The Kelsier Fortnite skin hasn't been seen in Fortnite for {days} days ({years:.2f} years).",
            f"{days} days and counting since Kelsier was last available in the Fortnite Item Shop ({years:.2f} years).",
            f"The Kelsier Fortnite skin crawled out of the Pits of Hathsin into Fortnite {days} days ago ({years:.2f} years).",
        ]
        
        main_text = random.choice(phrases)
        hashtags_text = " ".join(self.hashtags)
        
        full_tweet = f"{main_text} {hashtags_text}"
        
        if len(full_tweet) > 280:
            full_tweet = f"{main_text} #Fortnite #Kelsier #Mistborn"
        
        return full_tweet
    
    def post_tweet(self):
        tweet_text = self.generate_tweet_text()
        logging.info(f"📝 Generated tweet: {tweet_text}")
        
        auth = OAuth1(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_token_secret
        )
        
        payload = {"text": tweet_text}
        
        try:
            response = requests.post(self.api_url, auth=auth, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                logging.info("✅ Tweet posted successfully!")
                logging.info(f"🐦 Tweet ID: {response.json().get('data', {}).get('id', 'Unknown')}")
                return True
            else:
                logging.error(f"❌ Twitter API error: {response.status_code}")
                logging.error(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Connection error: {e}")
            return False

def main():
    try:
        logging.info("🤖 Starting Fortnite Kelsier Bot...")
        logging.info(f"📅 Today's date: {date.today()}")
        
        bot = FortniteKelsierBot()
        success = bot.post_tweet()
        
        if success:
            logging.info("🎉 Bot completed successfully!")
            sys.exit(0)  # Success exit code
        else:
            logging.error("💥 Bot failed to post tweet")
            sys.exit(1)  # Error exit code
            
    except Exception as e:
        logging.error(f"💥 Bot initialization error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

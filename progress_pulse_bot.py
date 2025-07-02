#!/usr/bin/env python3
"""
ProgressPulse - Twitter Year Progress Bot (Free Tier Fixed)
Posts daily updates using X API v2 with proper free tier authentication
"""

import tweepy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import datetime
import io
import os
import sys

class ProgressPulseBotFixed:
    def __init__(self):
        """Initialize ProgressPulse bot with correct free tier setup"""
        print("🤖 Initializing ProgressPulse Bot (Free Tier)...")
        
        # Get credentials from environment variables
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Validate credentials
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("❌ Missing Twitter API credentials. Please check environment variables.")
        
        # Initialize Twitter API v2 client (for posting)
        try:
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                bearer_token=self.bearer_token,
                wait_on_rate_limit=True
            )
            
            # Initialize v1.1 API for media upload (still needed)
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Test connection
            me = self.client.get_me()
            if me.data:
                print("✅ Twitter API v2 authentication successful!")
                print(f"👤 Connected as: @{me.data.username}")
            else:
                # Fallback to v1.1 verification
                user = self.api_v1.verify_credentials()
                print("✅ Twitter API v1.1 authentication successful!")
                print(f"👤 Connected as: @{user.screen_name}")
            
        except Exception as e:
            print(f"❌ Twitter API authentication failed: {str(e)}")
            print("💡 Make sure your app has 'Read and Write' permissions")
            raise
    
    def calculate_year_progress(self):
        """Calculate comprehensive year progress statistics"""
        today = datetime.date.today()
        year_start = datetime.date(today.year, 1, 1)
        year_end = datetime.date(today.year, 12, 31)
        
        days_passed = (today - year_start).days
        days_remaining = (year_end - today).days
        total_days = (year_end - year_start).days + 1
        percentage_complete = round((days_passed / total_days) * 100, 1)
        
        # Additional calculations
        weeks_remaining = days_remaining // 7
        months_remaining = (year_end.month - today.month) + (12 * (year_end.year - today.year))
        if year_end.day < today.day:
            months_remaining -= 1
        
        return {
            'year': today.year,
            'today': today,
            'days_passed': days_passed,
            'days_remaining': days_remaining,
            'total_days': total_days,
            'percentage_complete': percentage_complete,
            'weeks_remaining': weeks_remaining,
            'months_remaining': max(0, months_remaining)
        }
    
    def create_progress_chart(self, data):
        """Create a beautiful, professional bar chart showing year progress"""
        # Set up the figure with optimal dimensions
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('white')
        
        # Data for the chart
        categories = ['Days Completed', 'Days Remaining']
        values = [data['days_passed'], data['days_remaining']]
        colors = ['#1DA1F2', '#E8F4FD']  # Twitter blue and light blue
        
        # Create horizontal bar chart
        bars = ax.barh(categories, values, color=colors, height=0.6)
        
        # Add subtle shadow effect
        for bar in bars:
            bar.set_edgecolor('#CCCCCC')
            bar.set_linewidth(0.5)
        
        # Customize the chart
        ax.set_xlabel('Days', fontsize=14, fontweight='bold', color='#333333')
        ax.set_title(f'{data["year"]} Year Progress\n{data["percentage_complete"]}% Complete', 
                     fontsize=18, fontweight='bold', pad=20, color='#1DA1F2')
        
        # Add value labels on bars with better positioning
        for i, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            # Position text in the center of the bar
            ax.text(width/2, bar.get_y() + bar.get_height()/2, 
                   f'{value:,} days', ha='center', va='center', 
                   fontweight='bold', fontsize=14, color='#333333',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Style improvements
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        ax.spines['left'].set_color('#DDDDDD')
        
        # Set limits and add grid
        ax.set_xlim(0, data['total_days'] + 20)
        ax.grid(axis='x', alpha=0.3, linestyle='--', color='#CCCCCC')
        
        # Add subtle background
        ax.set_facecolor('#FAFAFA')
        
        # Add watermark
        ax.text(0.99, 0.01, 'ProgressPulse', transform=ax.transAxes, 
               ha='right', va='bottom', fontsize=10, alpha=0.5, style='italic')
        
        # Optimize layout
        plt.tight_layout(pad=2.0)
        
        # Save to bytes buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        
        plt.close()  # Close the figure to free memory
        return img_buffer
    
    def create_tweet_text(self, data):
        """Create engaging, dynamic tweet text based on time of year"""
        weeks_remaining = data['weeks_remaining']
        
        # Dynamic messaging based on time of year
        if data['percentage_complete'] >= 95:
            emoji = "🎊"
            message = "Almost there! Final sprint time!"
        elif data['percentage_complete'] >= 90:
            emoji = "🎯"
            message = "We're in the final stretch!"
        elif data['percentage_complete'] >= 75:
            emoji = "🍂"
            message = "Fourth quarter energy!"
        elif data['percentage_complete'] >= 50:
            emoji = "⚡"
            message = "Past the halfway mark!"
        elif data['percentage_complete'] >= 25:
            emoji = "🌸"
            message = "Building momentum!"
        else:
            emoji = "🚀"
            message = "The year is just beginning!"
        
        # Additional context based on remaining time
        if weeks_remaining <= 2:
            time_context = f"Just {data['days_remaining']} days left!"
        elif weeks_remaining <= 4:
            time_context = f"Only {weeks_remaining} weeks remaining!"
        else:
            time_context = f"About {weeks_remaining} weeks left to go!"
        
        tweet_text = f"""{emoji} {data['year']} Progress Update

📊 {data['percentage_complete']}% of the year complete
📅 {data['days_remaining']:,} days remaining
⏰ {time_context}

{message}

What will you accomplish with the time left? 💪

#YearProgress #{data['year']} #Motivation #Goals #TimeManagement #Productivity"""
        
        return tweet_text
    
    def post_daily_update(self):
        """Main function to create and post the daily year progress update"""
        try:
            print("🔄 Starting daily ProgressPulse update...")
            
            # Calculate progress
            data = self.calculate_year_progress()
            print(f"📊 Year progress: {data['percentage_complete']}% complete")
            print(f"📅 Days remaining: {data['days_remaining']:,}")
            print(f"⏰ Weeks remaining: {data['weeks_remaining']}")
            
            # Create chart
            print("🎨 Creating progress chart...")
            chart_buffer = self.create_progress_chart(data)
            print(f"📊 Chart created successfully, size: {len(chart_buffer.getvalue())} bytes")
            
            # Create tweet text
            tweet_text = self.create_tweet_text(data)
            print(f"📝 Tweet text created ({len(tweet_text)} characters)")
            print("📄 Tweet preview:")
            print("-" * 50)
            print(tweet_text)
            print("-" * 50)
            
            # Check tweet length
            if len(tweet_text) > 280:
                print("⚠️ Warning: Tweet exceeds 280 characters!")
                print("🔧 Truncating tweet...")
                tweet_text = tweet_text[:277] + "..."
            
            # Upload image using v1.1 API (required for media upload)
            print("📤 Uploading progress chart to Twitter...")
            try:
                media = self.api_v1.media_upload(filename='year_progress_chart.png', 
                                                file=chart_buffer)
                print(f"✅ Image uploaded successfully! Media ID: {media.media_id}")
            except Exception as e:
                print(f"❌ Image upload failed: {str(e)}")
                # Try posting without image
                print("⚠️ Attempting to post without image...")
                media = None
            
            # Post tweet using v2 API
            print("🐦 Posting tweet to Twitter...")
            try:
                if media:
                    # Post with media
                    response = self.client.create_tweet(
                        text=tweet_text,
                        media_ids=[media.media_id]
                    )
                else:
                    # Post text only
                    response = self.client.create_tweet(text=tweet_text)
                
                if response.data:
                    tweet_id = response.data['id']
                    print(f"✅ Tweet posted successfully!")
                    print(f"🆔 Tweet ID: {tweet_id}")
                    
                    # Get username for URL
                    me = self.client.get_me()
                    if me.data:
                        username = me.data.username
                        print(f"🔗 Tweet URL: https://twitter.com/{username}/status/{tweet_id}")
                    
                    print(f"📝 Tweet text length: {len(tweet_text)} characters")
                    return True
                else:
                    print("❌ Tweet creation failed - no response data")
                    return False
                
            except tweepy.Forbidden as e:
                print(f"❌ Tweet posting failed (403 Forbidden): {str(e)}")
                print("🔍 This might be a free tier limitation or app permission issue")
                print("💡 Possible solutions:")
                print("   1. Check your app permissions are 'Read and Write'")
                print("   2. Regenerate your access tokens after setting permissions")
                print("   3. Try posting a simple text-only tweet first")
                
                # Try a simple text-only tweet as fallback
                print("\n🔄 Attempting simple text-only tweet...")
                try:
                    simple_text = f"📊 {data['year']} Progress: {data['percentage_complete']}% complete, {data['days_remaining']} days remaining! #YearProgress"
                    response = self.client.create_tweet(text=simple_text)
                    if response.data:
                        print("✅ Simple tweet posted successfully!")
                        return True
                except Exception as e2:
                    print(f"❌ Simple tweet also failed: {str(e2)}")
                
                return False
                
            except Exception as e:
                print(f"❌ Tweet posting failed: {str(e)}")
                print(f"🔍 Error type: {type(e).__name__}")
                if hasattr(e, 'response'):
                    print(f"🔍 HTTP Status: {e.response.status_code}")
                    print(f"🔍 Response: {e.response.text}")
                return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function to run ProgressPulse bot"""
    print("🎯 ProgressPulse Bot Starting (Free Tier Fixed)...")
    print("=" * 50)
    
    try:
        # Create and run the bot
        bot = ProgressPulseBotFixed()
        success = bot.post_daily_update()
        
        if success:
            print("\n🎉 ProgressPulse completed successfully!")
            print("📱 Check your Twitter account for the new post!")
            sys.exit(0)
        else:
            print("\n💥 ProgressPulse encountered an error!")
            print("💡 Free tier has limitations - consider these options:")
            print("   - Apply for elevated access")
            print("   - Use manual posting approach")
            print("   - Try alternative platforms")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

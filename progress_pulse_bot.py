#!/usr/bin/env python3
"""
ProgressPulse - Twitter Year Progress Bot (Free Tier Fixed)
Posts daily updates using X API v2 with proper free tier authentication
"""

import tweepy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import calendar
import datetime
import io
import json
import os
import sys
import urllib.request

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
        self.include_today = os.getenv('PROGRESS_INCLUDE_TODAY', 'false').strip().lower() in (
            '1', 'true', 'yes', 'y'
        )
        self.use_remote_content = os.getenv('USE_REMOTE_CONTENT', 'true').strip().lower() in (
            '1', 'true', 'yes', 'y'
        )
        try:
            self.quote_max_length = int(os.getenv('QUOTE_MAX_LENGTH', '120'))
        except ValueError:
            self.quote_max_length = 120
        try:
            self.joke_max_length = int(os.getenv('JOKE_MAX_LENGTH', '120'))
        except ValueError:
            self.joke_max_length = 120
        try:
            self.http_timeout = float(os.getenv('CONTENT_HTTP_TIMEOUT', '5'))
        except ValueError:
            self.http_timeout = 5.0
        
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
            self.v1_available = True
            
            # Test connection (v2 can 403 if OAuth2 user context is not enabled)
            try:
                me = self.client.get_me()
                if me.data:
                    print("?o. Twitter API v2 authentication successful!")
                    print(f"?Y'? Connected as: @{me.data.username}")
                else:
                    # Fallback to v1.1 verification
                    try:
                        user = self.api_v1.verify_credentials()
                        print("?o. Twitter API v1.1 authentication successful!")
                        print(f"?Y'? Connected as: @{user.screen_name}")
                    except tweepy.Forbidden:
                        self.v1_available = False
                        print("WARNING: Twitter API v1.1 forbidden; continuing without v1.1 features.")
            except tweepy.Forbidden:
                # Free-tier or OAuth2 user-context restrictions can block v2 get_me
                try:
                    user = self.api_v1.verify_credentials()
                    print("?o. Twitter API v1.1 authentication successful!")
                    print(f"?Y'? Connected as: @{user.screen_name}")
                except tweepy.Forbidden:
                    self.v1_available = False
                    print("WARNING: Twitter API v1.1 forbidden; continuing without v1.1 features.")
        except Exception as e:
            print(f"❌ Twitter API authentication failed: {str(e)}")
            print("💡 Make sure your app has 'Read and Write' permissions")
            raise

    def _fetch_json(self, url):
        """Fetch JSON with a short timeout and optional remote toggle."""
        if not self.use_remote_content:
            return None
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "ProgressPulseBot/1.0"}
            )
            with urllib.request.urlopen(request, timeout=self.http_timeout) as response:
                if hasattr(response, "status") and response.status != 200:
                    return None
                payload = response.read()
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return None

    def _get_remote_quote(self):
        data = self._fetch_json("https://zenquotes.io/api/random")
        if not data or not isinstance(data, list):
            return None
        item = data[0] if data else None
        if not item:
            return None
        content = item.get("q")
        author = item.get("a")
        if not content:
            return None
        quote = f"\"{content}\""
        if author:
            quote = f"{quote} - {author}"
        if len(quote) > self.quote_max_length:
            return None
        return quote

    def _get_remote_joke(self):
        data = self._fetch_json(
            "https://v2.jokeapi.dev/joke/Any?type=single&safe-mode"
        )
        if not data or data.get("error"):
            return None
        joke = data.get("joke")
        if not joke:
            return None
        if len(joke) > self.joke_max_length:
            return None
        return joke
    
    def calculate_year_progress(self):
        """Calculate comprehensive year progress statistics with correct math"""
        today = datetime.date.today()
        year_start = datetime.date(today.year, 1, 1)
        year_end = datetime.date(today.year, 12, 31)
        
        # Total days in the year
        total_days = (year_end - year_start).days + 1  # +1 because we include both start and end dates

        # Calculate days passed (optionally include today as completed)
        days_passed = (today - year_start).days + (1 if self.include_today else 0)

        # Calculate days remaining (kept consistent with total days)
        days_remaining = total_days - days_passed
        
        # Calculate percentage (more precise)
        percentage_complete = round((days_passed / total_days) * 100, 1)
        
        # Debug verification
        print(f"🔍 Debug: Days passed: {days_passed}, Days remaining: {days_remaining}, Total: {total_days}")
        print(f"🔍 Verification: {days_passed} + {days_remaining} = {days_passed + days_remaining} (should equal {total_days})")
        print(f"🔍 Today: {today}, Year start: {year_start}, Year end: {year_end}")
        
        # Additional calculations
        weeks_remaining = days_remaining // 7
        months_remaining = (year_end.month - today.month) + (12 * (year_end.year - today.year))
        if year_end.day < today.day:
            months_remaining -= 1
        
        return {
            'year': today.year,
            'today': today,
            'include_today': self.include_today,
            'days_passed': days_passed,
            'days_remaining': days_remaining,
            'total_days': total_days,
            'percentage_complete': percentage_complete,
            'weeks_remaining': weeks_remaining,
            'months_remaining': max(0, months_remaining)
        }
    
    def create_progress_chart(self, data):
        """Create a beautiful stacked horizontal bar chart showing year progress"""
        # Set up the figure with optimal dimensions
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('white')
        
        # Data for the stacked chart
        days_completed = data['days_passed']
        days_remaining = data['days_remaining']
        colors = ['#1DA1F2', '#E8F4FD']  # Twitter blue for completed, light blue for remaining
        
        # Create single stacked horizontal bar
        category = [f"{data['year']} Progress"]
        
        # Create the stacked bar
        bar1 = ax.barh(category, days_completed, color=colors[0], height=0.4, label='Days Completed')
        bar2 = ax.barh(category, days_remaining, left=days_completed, color=colors[1], height=0.4, label='Days Remaining')
        
        # Add subtle borders
        for bar in [bar1[0], bar2[0]]:
            bar.set_edgecolor('#CCCCCC')
            bar.set_linewidth(1)
        
        # Customize the chart
        ax.set_xlabel('Days', fontsize=14, fontweight='bold', color='#333333')
        ax.set_title(f'{data["year"]} Year Progress - {data["percentage_complete"]}% Complete', 
                     fontsize=18, fontweight='bold', pad=20, color='#1DA1F2')
        
        # Add value labels on the stacked bars
        # Label for completed days (left side)
        ax.text(days_completed/2, 0, f'{days_completed:,} days\ncompleted', 
               ha='center', va='center', fontweight='bold', fontsize=12, color='white',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#1DA1F2', alpha=0.8))
        
        # Label for remaining days (right side)
        ax.text(days_completed + days_remaining/2, 0, f'{days_remaining:,} days\nremaining', 
               ha='center', va='center', fontweight='bold', fontsize=12, color='#333333',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        # Add percentage labels at the edges
        ax.text(days_completed, 0.25, f'{data["percentage_complete"]}%', 
               ha='center', va='center', fontweight='bold', fontsize=10, color='#1DA1F2')
        ax.text(days_completed, -0.25, f'{100 - data["percentage_complete"]}%', 
               ha='center', va='center', fontweight='bold', fontsize=10, color='#666666')
        
        # Style improvements
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        
        # Set limits and add subtle grid
        ax.set_xlim(0, data['total_days'])
        ax.set_ylim(-0.5, 0.5)
        ax.grid(axis='x', alpha=0.2, linestyle='--', color='#CCCCCC')
        
        # Remove y-axis ticks and labels for cleaner look
        ax.set_yticks([])
        
        # Add month markers on x-axis for context
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        months_days = []
        running_total = 0
        for month in range(1, 13):
            running_total += calendar.monthrange(data['year'], month)[1]
            months_days.append(running_total)

        for i, (day, month_name) in enumerate(zip(months_days, month_names)):
            if i % 2 == 0:  # Show every other month to avoid crowding
                ax.axvline(x=day, color='#EEEEEE', linestyle='-', alpha=0.5)
                ax.text(day, -0.4, month_name, ha='center', va='center', fontsize=8, color='#888888')
        
        # Add subtle background
        ax.set_facecolor('#FAFAFA')
        
        # Add watermark
        ax.text(0.99, 0.02, 'ProgressPulse', transform=ax.transAxes, 
               ha='right', va='bottom', fontsize=10, alpha=0.5, style='italic')
        
        # Add progress bar visual enhancement
        total_width = data['total_days']
        progress_width = days_completed
        
        # Add a subtle progress indicator line
        ax.axvline(x=progress_width, color='#1DA1F2', linestyle='-', linewidth=3, alpha=0.7)
        
        # Optimize layout
        plt.tight_layout(pad=1.5)
        
        # Save to bytes buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        
        plt.close()  # Close the figure to free memory
        return img_buffer
    
    def create_tweet_text(self, data):
        """Create rotating tweet text with hooks, insights, and prompts."""
        weekday = data['today'].weekday()
        pct = data['percentage_complete']

        hooks = [
            "Monday check-in: {pct}% of {year} done.",
            "Day {days_passed}/{total_days}: {pct}% complete.",
            "Midweek pulse: {pct}% of {year} complete.",
            "Thursday pace: {days_remaining} days left in {year}.",
            "Friday recap: {pct}% done. {days_remaining} days left.",
            "Weekend update: {pct}% complete.",
            "Sunday reset: {days_remaining} days left this year.",
        ]

        insights = [
            "My take: consistency beats intensity over a year.",
            "My take: small wins compound faster than big plans.",
            "My take: clarity first, then action.",
            "My take: momentum is built by showing up again.",
            "My take: focus makes average days count.",
            "My take: tiny steps keep big goals alive.",
            "My take: progress follows attention.",
        ]

        jokes = [
            "Quick joke: tomorrow is not a project plan.",
            "Quick joke: time blocking is great until time blocks back.",
            "Quick joke: consistency is the only streak I want.",
            "Quick joke: progress looks better in morning light.",
        ]

        fallback_quotes = [
            "Quote: small steps add up.",
            "Quote: focus on the next right step.",
            "Quote: consistency makes ordinary days count.",
            "Quote: start now, refine later.",
        ]

        prompts = [
            "What is one thing you will finish this week?",
            "What is your next 1% action today?",
            "Name one small win you can lock in today.",
            "What would make today count?",
            "Pick one priority and move it forward.",
            "What can you complete before Friday?",
            "What will you do in the next 30 minutes?",
        ]

        hook = hooks[weekday].format(
            pct=pct,
            year=data['year'],
            days_passed=data['days_passed'],
            total_days=data['total_days'],
            days_remaining=data['days_remaining'],
        )
        insight = insights[data['days_passed'] % len(insights)]
        prompt = prompts[data['days_remaining'] % len(prompts)]
        show_joke = data['days_passed'] > 0 and data['days_passed'] % 7 == 0
        show_quote = not show_joke and data['days_passed'] % 3 == 0

        extra_line = None
        if show_joke:
            extra_line = self._get_remote_joke() or jokes[data['days_passed'] % len(jokes)]
        elif show_quote:
            extra_line = self._get_remote_quote() or fallback_quotes[
                data['days_passed'] % len(fallback_quotes)
            ]

        extra_tags = ['#Goals', '#Productivity', '#Focus', '#Consistency']
        extra_tag = extra_tags[data['days_passed'] % len(extra_tags)]
        hashtags = f"#YearProgress #{data['year']} {extra_tag}"

        lines = [
            hook,
            f"{data['days_remaining']:,} days left. {data['weeks_remaining']} weeks left.",
            insight,
        ]
        if extra_line:
            lines.append(extra_line)
        lines.extend([prompt, hashtags])

        tweet_text = "\n".join(lines)
        if extra_line and len(tweet_text) > 280:
            lines = [
                hook,
                f"{data['days_remaining']:,} days left. {data['weeks_remaining']} weeks left.",
                insight,
                prompt,
                hashtags,
            ]
            tweet_text = "\n".join(lines)

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
            if self.v1_available:
                print("Uploading progress chart to Twitter...")
                try:
                    media = self.api_v1.media_upload(filename='year_progress_chart.png', 
                                                    file=chart_buffer)
                    print(f"Image uploaded successfully! Media ID: {media.media_id}")
                except Exception as e:
                    print(f"Image upload failed: {str(e)}")
                    # Try posting without image
                    print("Attempting to post without image...")
                    media = None
            else:
                print("WARNING: v1.1 not available; posting without image.")
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
                    try:
                        me = self.client.get_me()
                        if me.data:
                            username = me.data.username
                            print(f"Tweet URL: https://twitter.com/{username}/status/{tweet_id}")
                    except tweepy.Forbidden:
                        print("WARNING: v2 get_me forbidden; skipping tweet URL.")
                    
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

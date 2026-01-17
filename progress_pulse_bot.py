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
        """Create a clean, modern progress bar chart for the year."""
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        # Hide axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        days_completed = data['days_passed']
        days_remaining = data['days_remaining']
        total_days = data['total_days']
        progress = days_completed / total_days if total_days else 0

        # Layout
        bar_x = 0.08
        bar_y = 0.42
        bar_w = 0.84
        bar_h = 0.12

        # Colors
        title_color = '#0B2545'
        text_color = '#34495E'
        accent = '#1DA1F2'
        bar_bg = '#E8F1FB'

        # Title and headline
        ax.text(bar_x, 0.86, f"{data['year']} Year Progress", fontsize=18,
                fontweight='bold', color=title_color)
        ax.text(bar_x, 0.76, f"{data['percentage_complete']}% complete", fontsize=32,
                fontweight='bold', color=accent)
        ax.text(bar_x, 0.68,
                f"{days_completed:,} days done / {days_remaining:,} days left",
                fontsize=14, color=text_color)
        ax.text(bar_x, 0.62, f"{data['weeks_remaining']} weeks left", fontsize=12,
                color=text_color)

        # Progress bar background
        bar_bg_patch = matplotlib.patches.FancyBboxPatch(
            (bar_x, bar_y), bar_w, bar_h,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=0, facecolor=bar_bg
        )
        ax.add_patch(bar_bg_patch)

        # Progress bar fill
        fill_w = bar_w * progress
        if fill_w > 0:
            bar_fg_patch = matplotlib.patches.FancyBboxPatch(
                (bar_x, bar_y), fill_w, bar_h,
                boxstyle="round,pad=0.01,rounding_size=0.02",
                linewidth=0, facecolor=accent
            )
            ax.add_patch(bar_fg_patch)

        # Progress marker
        marker_x = bar_x + fill_w
        ax.plot([marker_x], [bar_y + bar_h / 2], marker='o', markersize=8,
                color=accent, markeredgecolor='white', markeredgewidth=1)

        # Start and end labels
        ax.text(bar_x, bar_y - 0.06, "Jan 1", fontsize=10, color='#7F8C8D')
        ax.text(bar_x + bar_w, bar_y - 0.06, "Dec 31", fontsize=10,
                color='#7F8C8D', ha='right')

        # Footer
        ax.text(0.99, 0.04, 'ProgressPulse', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=10, color='#95A5A6')

        plt.tight_layout(pad=1.0)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close()
        return img_buffer

    def create_tweet_text(self, data):
        """Create tweet text with spacing and light emojis."""
        weekday = data['today'].weekday()
        pct = data['percentage_complete']

        hooks = [
            "Monday reset.",
            "Tuesday momentum check.",
            "Midweek pulse.",
            "Thursday pace check.",
            "Friday recap.",
            "Weekend update.",
            "Sunday reset.",
        ]

        insights = [
            "Consistency beats intensity over a year.",
            "Small wins compound faster than big plans.",
            "Clarity first, then action.",
            "Momentum comes from showing up again.",
            "Focus makes average days count.",
            "Tiny steps keep big goals alive.",
            "Progress follows attention.",
        ]

        jokes = [
            "Tomorrow is not a project plan.",
            "Time blocking is great until time blocks back.",
            "Consistency is the only streak I want.",
            "Progress looks better in morning light.",
        ]

        fallback_quotes = [
            "\"Small steps add up.\"",
            "\"Focus on the next right step.\"",
            "\"Consistency makes ordinary days count.\"",
            "\"Start now, refine later.\"",
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

        hook = hooks[weekday]
        insight = insights[data['days_passed'] % len(insights)]
        prompt = prompts[data['days_remaining'] % len(prompts)]
        show_joke = data['days_passed'] > 0 and data['days_passed'] % 7 == 0
        show_quote = not show_joke and data['days_passed'] % 3 == 0

        extra_line = None
        if show_joke:
            joke = self._get_remote_joke() or jokes[data['days_passed'] % len(jokes)]
            extra_line = f"\U0001F642 {joke}"
        elif show_quote:
            quote = self._get_remote_quote() or fallback_quotes[
                data['days_passed'] % len(fallback_quotes)
            ]
            extra_line = f"\U0001F4AC {quote}"

        extra_tags = ['#Goals', '#Productivity', '#Focus', '#Consistency']
        extra_tag = extra_tags[data['days_passed'] % len(extra_tags)]
        hashtags = f"#YearProgress #{data['year']} {extra_tag}"

        lines = [
            f"\U0001F5D3 {hook}",
            f"{pct}% complete. {data['days_remaining']:,} days left.",
            f"\u2728 {insight}",
        ]
        if extra_line:
            lines.append(extra_line)
        lines.append(f"\U0001F449 {prompt}")
        lines.append(hashtags)

        tweet_text = "\n\n".join(lines)
        if extra_line and len(tweet_text) > 280:
            lines = [
                f"\U0001F5D3 {hook}",
                f"{pct}% complete. {data['days_remaining']:,} days left.",
                f"\u2728 {insight}",
                f"\U0001F449 {prompt}",
                hashtags,
            ]
            tweet_text = "\n\n".join(lines)

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
                        media_ids=[media.media_id],
                        user_auth=True
                    )
                else:
                    # Post text only
                    response = self.client.create_tweet(text=tweet_text, user_auth=True)
                
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
                if hasattr(e, 'response') and e.response is not None:
                    print(f"HTTP Status: {e.response.status_code}")
                    print(f"Response: {e.response.text}")
                
                # Try a simple text-only tweet as fallback
                print("\n🔄 Attempting simple text-only tweet...")
                try:
                    simple_text = f"📊 {data['year']} Progress: {data['percentage_complete']}% complete, {data['days_remaining']} days remaining! #YearProgress"
                    response = self.client.create_tweet(text=simple_text, user_auth=True)
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

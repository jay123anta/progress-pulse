#!/usr/bin/env python3
"""
ProgressPulse Local Test Script
Test the bot functionality WITHOUT posting to Twitter
Use this to verify everything works before running the actual bot
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import datetime
import os
import sys

def test_imports():
    """Test that all required packages are installed"""
    print("📦 Testing package imports...")
    
    try:
        import tweepy
        print(f"  ✅ tweepy {tweepy.__version__}")
    except ImportError as e:
        print(f"  ❌ tweepy: {e}")
        return False
    
    try:
        import matplotlib
        print(f"  ✅ matplotlib {matplotlib.__version__}")
    except ImportError as e:
        print(f"  ❌ matplotlib: {e}")
        return False
    
    try:
        import PIL
        print(f"  ✅ pillow {PIL.__version__}")
    except ImportError as e:
        print(f"  ❌ pillow: {e}")
        return False
    
    return True

def test_progress_calculation():
    """Test the year progress calculation"""
    print("\n🧮 Testing year progress calculation...")
    
    today = datetime.date.today()
    year_start = datetime.date(today.year, 1, 1)
    year_end = datetime.date(today.year, 12, 31)
    
    include_today = os.getenv('PROGRESS_INCLUDE_TODAY', 'false').strip().lower() in (
        '1', 'true', 'yes', 'y'
    )
    total_days = (year_end - year_start).days + 1
    days_passed = (today - year_start).days + (1 if include_today else 0)
    days_remaining = total_days - days_passed
    percentage_complete = round((days_passed / total_days) * 100, 1)
    
    # Additional calculations
    weeks_remaining = days_remaining // 7
    months_remaining = (year_end.month - today.month) + (12 * (year_end.year - today.year))
    if year_end.day < today.day:
        months_remaining -= 1
    
    data = {
        'year': today.year,
        'today': today,
        'include_today': include_today,
        'days_passed': days_passed,
        'days_remaining': days_remaining,
        'total_days': total_days,
        'percentage_complete': percentage_complete,
        'weeks_remaining': weeks_remaining,
        'months_remaining': max(0, months_remaining)
    }
    
    print(f"  📅 Year: {data['year']}")
    print(f"  📊 Days passed: {data['days_passed']:,}")
    print(f"  📊 Days remaining: {data['days_remaining']:,}")
    print(f"  📊 Total days: {data['total_days']}")
    print(f"  📊 Percentage complete: {data['percentage_complete']}%")
    print(f"  📊 Weeks remaining: {data['weeks_remaining']}")
    print(f"  📊 Months remaining: {data['months_remaining']}")
    print("  ✅ Progress calculation test passed!")
    
    return data

def test_chart_creation(data):
    """Test chart creation and save to file"""
    print("\n🎨 Testing chart creation...")
    
    try:
        # Create a test chart
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
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            ax.text(width/2, bar.get_y() + bar.get_height()/2, 
                   f'{value:,} days', ha='center', va='center', 
                   fontweight='bold', fontsize=14, color='#333333',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Style improvements
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        ax.spines['left'].set_color('#DDDDDD')
        
        ax.set_xlim(0, data['total_days'] + 20)
        ax.grid(axis='x', alpha=0.3, linestyle='--', color='#CCCCCC')
        
        # Add subtle background
        ax.set_facecolor('#FAFAFA')
        
        # Add watermark
        ax.text(0.99, 0.01, 'ProgressPulse TEST', transform=ax.transAxes, 
               ha='right', va='bottom', fontsize=10, alpha=0.5, style='italic')
        
        plt.tight_layout(pad=2.0)
        
        # Save test chart
        plt.savefig('test_progress_chart.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()

        print("  Chart creation test passed!")
        print("  Test chart saved as 'test_progress_chart.png'")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Chart creation test failed: {str(e)}")
        return False

def test_tweet_text(data):
    """Test tweet text generation"""
    print("\nTesting tweet text generation...")

    try:
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
            extra_line = jokes[data['days_passed'] % len(jokes)]
        elif show_quote:
            extra_line = fallback_quotes[data['days_passed'] % len(fallback_quotes)]

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

        print("Generated tweet text:")
        print("  " + "-" * 60)
        for line in tweet_text.split('\n'):
            print(f"  {line}")
        print("  " + "-" * 60)
        print(f"Character count: {len(tweet_text)}/280")

        if len(tweet_text) > 280:
            print("Warning: Tweet is longer than 280 characters")
            print("Consider shortening the message or hashtags")
            return False

        print("Tweet text test passed")
        return True

    except Exception as e:
        print(f"Tweet text test failed: {str(e)}")
        return False

def test_credentials():
    """Test if Twitter API credentials are set"""
    print("\n🔐 Testing Twitter API credentials...")
    
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET', 
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Show first 8 characters for verification
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"  ❌ Missing environment variables:")
        for var in missing_vars:
            print(f"     - {var}")
        print("  💡 Set these before running the actual bot!")
        return False
    else:
        print("  ✅ All required environment variables are set!")
        return True

def test_twitter_connection():
    """Test Twitter API connection (if credentials are available)"""
    print("\n🐦 Testing Twitter API connection...")
    
    try:
        import tweepy
        
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            print("  ⚠️ Skipping Twitter connection test (missing credentials)")
            return None
        
        # Initialize Twitter API
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Verify credentials
        user = api.verify_credentials()
        print(f"  ✅ Twitter API connection successful!")
        print(f"  👤 Connected as: @{user.screen_name}")
        print(f"  📊 Account stats: {user.followers_count:,} followers, {user.friends_count:,} following")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Twitter API connection failed: {str(e)}")
        print("  💡 Check your API credentials and app permissions")
        return False

def main():
    """Run all tests"""
    print("🧪 ProgressPulse Bot Test Suite")
    print("=" * 60)
    print("⚠️  NOTE: This is a TEST script - it will NOT post to Twitter!")
    print("⚠️  Use 'python progress_pulse_bot.py' to actually post tweets")
    print("=" * 60)
    
    # Test results
    results = {}
    
    # Test 1: Package imports
    results['imports'] = test_imports()
    
    # Test 2: Progress calculation
    if results['imports']:
        data = test_progress_calculation()
        results['calculation'] = data is not None
    else:
        print("\n⚠️ Skipping remaining tests due to import failures")
        data = None
        results['calculation'] = False
    
    # Test 3: Chart creation
    if results['calculation'] and data:
        results['chart'] = test_chart_creation(data)
    else:
        results['chart'] = False
    
    # Test 4: Tweet text generation
    if results['calculation'] and data:
        results['tweet_text'] = test_tweet_text(data)
    else:
        results['tweet_text'] = False
    
    # Test 5: Credentials check
    results['credentials'] = test_credentials()
    
    # Test 6: Twitter connection (if credentials available)
    results['twitter_connection'] = test_twitter_connection()
    
    # Summary
    print("\n🏁 Test Results Summary")
    print("=" * 60)
    print(f"📦 Package imports: {'✅' if results['imports'] else '❌'}")
    print(f"🧮 Progress calculation: {'✅' if results['calculation'] else '❌'}")
    print(f"🎨 Chart creation: {'✅' if results['chart'] else '❌'}")
    print(f"📝 Tweet text: {'✅' if results['tweet_text'] else '❌'}")
    print(f"🔐 Credentials: {'✅' if results['credentials'] else '❌'}")
    
    if results['twitter_connection'] is None:
        print(f"🐦 Twitter connection: ⚠️ (skipped)")
    else:
        print(f"🐦 Twitter connection: {'✅' if results['twitter_connection'] else '❌'}")
    
    # Overall status
    core_tests = [results['imports'], results['calculation'], results['chart'], results['tweet_text']]
    
    print("\n" + "=" * 60)
    if all(core_tests):
        print("🎉 All core functionality tests passed!")
        if results['credentials'] and results['twitter_connection']:
            print("🚀 ProgressPulse is ready to run!")
            print("💡 You can now run: python progress_pulse_bot.py")
        elif results['credentials']:
            print("⚠️ Twitter credentials are set but connection failed")
            print("💡 Check your API permissions and try again")
        else:
            print("⚠️ Set up Twitter API credentials to run the bot")
            print("💡 Add the 4 required environment variables")
    else:
        print("❌ Some core tests failed. Please fix the errors above.")
        sys.exit(1)
    
    print("\n🔄 To run the actual bot (posts to Twitter):")
    print("   python progress_pulse_bot.py")

if __name__ == "__main__":
    main()

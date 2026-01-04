#!/usr/bin/env python3
"""
ProgressPulse Local Test Script
Test the bot functionality WITHOUT posting to Twitter
Use this to verify everything works before running the actual bot
"""

import datetime
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tweepy


def test_imports():
    """Test that all required packages are installed"""
    print("Testing package imports...")

    try:
        import tweepy as _tweepy
        print(f"  OK: tweepy {_tweepy.__version__}")
    except ImportError as e:
        print(f"  FAIL: tweepy: {e}")
        return False

    try:
        import matplotlib as _matplotlib
        print(f"  OK: matplotlib {_matplotlib.__version__}")
    except ImportError as e:
        print(f"  FAIL: matplotlib: {e}")
        return False

    try:
        import PIL as _pil
        print(f"  OK: pillow {_pil.__version__}")
    except ImportError as e:
        print(f"  FAIL: pillow: {e}")
        return False

    return True


def test_progress_calculation():
    """Test the year progress calculation"""
    print("\nTesting year progress calculation...")

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

    print(f"  Year: {data['year']}")
    print(f"  Days passed: {data['days_passed']}")
    print(f"  Days remaining: {data['days_remaining']}")
    print(f"  Total days: {data['total_days']}")
    print(f"  Percent complete: {data['percentage_complete']}%")
    print(f"  Weeks remaining: {data['weeks_remaining']}")
    print(f"  Months remaining: {data['months_remaining']}")
    print("  OK: progress calculation")

    return data


def test_chart_creation(data):
    """Test chart creation and save to file"""
    print("\nTesting chart creation...")

    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        days_completed = data['days_passed']
        days_remaining = data['days_remaining']
        total_days = data['total_days']
        progress = days_completed / total_days if total_days else 0

        bar_x = 0.08
        bar_y = 0.42
        bar_w = 0.84
        bar_h = 0.12

        title_color = '#0B2545'
        text_color = '#34495E'
        accent = '#1DA1F2'
        bar_bg = '#E8F1FB'

        ax.text(bar_x, 0.86, f"{data['year']} Year Progress", fontsize=18,
                fontweight='bold', color=title_color)
        ax.text(bar_x, 0.76, f"{data['percentage_complete']}% complete", fontsize=32,
                fontweight='bold', color=accent)
        ax.text(bar_x, 0.68,
                f"{days_completed:,} days done / {days_remaining:,} days left",
                fontsize=14, color=text_color)
        ax.text(bar_x, 0.62, f"{data['weeks_remaining']} weeks left", fontsize=12,
                color=text_color)

        bar_bg_patch = matplotlib.patches.FancyBboxPatch(
            (bar_x, bar_y), bar_w, bar_h,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=0, facecolor=bar_bg
        )
        ax.add_patch(bar_bg_patch)

        fill_w = bar_w * progress
        if fill_w > 0:
            bar_fg_patch = matplotlib.patches.FancyBboxPatch(
                (bar_x, bar_y), fill_w, bar_h,
                boxstyle="round,pad=0.01,rounding_size=0.02",
                linewidth=0, facecolor=accent
            )
            ax.add_patch(bar_fg_patch)

        marker_x = bar_x + fill_w
        ax.plot([marker_x], [bar_y + bar_h / 2], marker='o', markersize=8,
                color=accent, markeredgecolor='white', markeredgewidth=1)

        ax.text(bar_x, bar_y - 0.06, "Jan 1", fontsize=10, color='#7F8C8D')
        ax.text(bar_x + bar_w, bar_y - 0.06, "Dec 31", fontsize=10,
                color='#7F8C8D', ha='right')

        ax.text(0.99, 0.04, 'ProgressPulse TEST', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=10, color='#95A5A6')

        plt.tight_layout(pad=1.0)
        plt.savefig('test_progress_chart.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()

        print("  OK: chart creation")
        print("  Test chart saved as 'test_progress_chart.png'")
        return True

    except Exception as e:
        print(f"  FAIL: chart creation: {str(e)}")
        return False


def test_tweet_text(data):
    """Test tweet text generation"""
    print("\nTesting tweet text generation...")

    try:
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
            joke = jokes[data['days_passed'] % len(jokes)]
            extra_line = f"\U0001F642 {joke}"
        elif show_quote:
            quote = fallback_quotes[data['days_passed'] % len(fallback_quotes)]
            extra_line = f"\U0001F4AC {quote}"

        extra_tags = ['#Goals', '#Productivity', '#Focus', '#Consistency']
        extra_tag = extra_tags[data['days_passed'] % len(extra_tags)]
        hashtags = f"#YearProgress #{data['year']} {extra_tag}"

        lines = [
            f"\U0001F5D3 {hook}",
            f"{pct}% complete. {data['days_remaining']:,} days left.",
            f"\U00002728 {insight}",
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
                f"\U00002728 {insight}",
                f"\U0001F449 {prompt}",
                hashtags,
            ]
            tweet_text = "\n\n".join(lines)

        print("Generated tweet text:")
        print("  " + "-" * 60)
        for line in tweet_text.split('\n'):
            print(f"  {line}")
        print("  " + "-" * 60)
        print(f"Character count: {len(tweet_text)}/280")

        if len(tweet_text) > 280:
            print("Warning: Tweet is longer than 280 characters")
            return False

        print("OK: tweet text")
        return True

    except Exception as e:
        print(f"FAIL: tweet text: {str(e)}")
        return False


def test_credentials():
    """Test if Twitter API credentials are set"""
    print("\nTesting Twitter API credentials...")

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
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  OK: {var}: {masked_value}")

    if missing_vars:
        print("  Missing environment variables:")
        for var in missing_vars:
            print(f"    - {var}")
        print("  Set these before running the actual bot")
        return False

    print("  OK: all required environment variables are set")
    return True


def test_twitter_connection():
    """Test Twitter API connection (if credentials are available)"""
    print("\nTesting Twitter API connection...")

    try:
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([api_key, api_secret, access_token, access_token_secret]):
            print("  Skipping Twitter connection test (missing credentials)")
            return None

        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        user = api.verify_credentials()
        print("  OK: Twitter API connection successful")
        print(f"  Connected as: @{user.screen_name}")
        return True

    except Exception as e:
        print(f"  FAIL: Twitter API connection failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("ProgressPulse Bot Test Suite")
    print("=" * 60)
    print("NOTE: This is a TEST script - it will NOT post to Twitter")
    print("Use 'python progress_pulse_bot.py' to actually post tweets")
    print("=" * 60)

    results = {}
    results['imports'] = test_imports()

    if results['imports']:
        data = test_progress_calculation()
        results['calculation'] = data is not None
    else:
        print("\nSkipping remaining tests due to import failures")
        data = None
        results['calculation'] = False

    if results['calculation'] and data:
        results['chart'] = test_chart_creation(data)
        results['tweet_text'] = test_tweet_text(data)
    else:
        results['chart'] = False
        results['tweet_text'] = False

    results['credentials'] = test_credentials()
    results['twitter_connection'] = test_twitter_connection()

    print("\nTest Results Summary")
    print("=" * 60)
    print(f"Imports: {'OK' if results['imports'] else 'FAIL'}")
    print(f"Progress calculation: {'OK' if results['calculation'] else 'FAIL'}")
    print(f"Chart creation: {'OK' if results['chart'] else 'FAIL'}")
    print(f"Tweet text: {'OK' if results['tweet_text'] else 'FAIL'}")
    print(f"Credentials: {'OK' if results['credentials'] else 'FAIL'}")

    if results['twitter_connection'] is None:
        print("Twitter connection: SKIPPED")
    else:
        print(f"Twitter connection: {'OK' if results['twitter_connection'] else 'FAIL'}")

    core_tests = [results['imports'], results['calculation'], results['chart'], results['tweet_text']]
    if all(core_tests):
        print("\nAll core functionality tests passed")
    else:
        print("\nSome core tests failed. Please fix the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()

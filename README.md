# 🎯 ProgressPulse - Twitter Year Progress Bot

> Your daily pulse on time's progress

An elegant, automated Twitter bot that posts beautiful daily updates about the remaining days in the current year, complete with professional progress charts and motivational messaging.

## 🌟 Features

- **📊 Daily Progress Charts** - Beautiful horizontal bar charts showing year completion
- **🤖 Fully Automated** - Runs daily on GitHub Actions (completely free)
- **💪 Dynamic Messaging** - Context-aware motivational content based on time of year  
- **🎨 Professional Design** - Twitter-branded charts with clean aesthetics
- **⚡ Error Handling** - Robust error handling and rate limit management
- **📱 Mobile Optimized** - Charts designed to look great on all devices

## 📸 Example Output

### Tweet Text:
```
🍂 2025 Progress Update

📊 66.3% of the year complete
📅 123 days remaining  
⏰ About 17 weeks left to go!

Fourth quarter energy!

What will you accomplish with the time left? 💪

#YearProgress #2025 #Motivation #Goals #TimeManagement #Productivity
```

### Visual Chart:
Beautiful horizontal bar chart showing:
- Days Completed: 242 days (in Twitter blue)
- Days Remaining: 123 days (in light blue)
- Professional styling with grid lines and labels

## 🚀 Quick Start

### Prerequisites
- GitHub account
- Twitter Developer account
- Twitter account for the bot (recommended: create a dedicated account)

### 1. Get Twitter API Access
1. Apply at [developer.twitter.com](https://developer.twitter.com)
2. Create a new app called "ProgressPulse"
3. Generate API keys and tokens
4. Save these 4 values securely:
   - API Key
   - API Key Secret  
   - Access Token
   - Access Token Secret

### 2. Set Up Repository
1. Fork or create this repository
2. Make sure it's **public** (required for free GitHub Actions)

### 3. Add Twitter Credentials
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these 4 secrets:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`

### 4. Test & Deploy
1. Go to **Actions** tab
2. Click "ProgressPulse Daily Tweet"
3. Click "Run workflow" to test
4. Check your Twitter account for the post!

## ⏰ Scheduling

By default, ProgressPulse posts daily at **12:00 PM UTC**.

### Change the Schedule:
Edit `.github/workflows/daily-progress-tweet.yml`:

```yaml
# Popular schedule options:
- cron: '0 12 * * *'      # Daily at 12 PM UTC
- cron: '0 9 * * 1,3,5'   # Mon, Wed, Fri at 9 AM UTC  
- cron: '0 18 * * 0'      # Every Sunday at 6 PM UTC
- cron: '30 8 * * *'      # Daily at 8:30 AM UTC
```

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

## 🛠️ Customization

### Modify Chart Appearance
Edit the `create_progress_chart()` method in `progress_pulse_bot.py`:
- Change colors: Modify the `colors` array
- Adjust dimensions: Change `figsize=(12, 8)`
- Add themes: Create seasonal color schemes

### Customize Messages
Edit the `create_tweet_text()` method:
- Add your own motivational messages
- Include different hashtags
- Modify the percentage thresholds for different messages

### Example Customizations:
```python
# Seasonal colors
colors = ['#FF6B6B', '#4ECDC4']  # Coral and teal
colors = ['#A8E6CF', '#FFD93D']  # Green and yellow
colors = ['#6C5CE7', '#FDCB6E']  # Purple and orange

# Custom messages
if data['percentage_complete'] >= 75:
    message = "Q4 hustle mode activated! 🔥"
```

## 📁 Project Structure

```
progress-pulse/
├── progress_pulse_bot.py           # Main bot script
├── requirements.txt                # Python dependencies
├── .github/workflows/
│   └── daily-progress-tweet.yml   # GitHub Actions workflow
├── test_local.py                  # Local testing script
└── README.md                      # This file
```

## 🧪 Local Testing

Test the bot on your computer before deploying:

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/progress-pulse.git
cd progress-pulse
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
# Linux/Mac
export TWITTER_API_KEY="your_key_here"
export TWITTER_API_SECRET="your_secret_here"
export TWITTER_ACCESS_TOKEN="your_token_here"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret_here"

# Windows
set TWITTER_API_KEY=your_key_here
set TWITTER_API_SECRET=your_secret_here
set TWITTER_ACCESS_TOKEN=your_token_here
set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
```

### 4. Run Tests
```bash
# Test without posting to Twitter
python test_local.py

# Run the actual bot (will post to Twitter)
python progress_pulse_bot.py
```

## 📊 Monitoring & Analytics

### GitHub Actions Monitoring
- **Actions Tab**: View execution logs and success/failure status
- **Email Notifications**: Get notified if the workflow fails
- **Manual Triggers**: Run the bot manually anytime

### Twitter Analytics
- Track engagement (likes, retweets, replies)
- Monitor follower growth
- Analyze best posting times

## 🔧 Troubleshooting

### Common Issues

**❌ "Missing Twitter API credentials"**
- Double-check that all 4 secrets are added to GitHub
- Ensure secret names match exactly
- Verify the secret values are correct

**❌ "Rate limit exceeded"**
- Twitter limits posting frequency
- The bot will automatically retry
- Consider reducing posting frequency if persistent

**❌ "Authentication failed"**
- Verify your Twitter API keys are valid
- Check that your Twitter app has write permissions
- Ensure tokens haven't expired

**❌ "Chart creation failed"**
- Usually resolves automatically on retry
- Check GitHub Actions logs for specific errors
- Ensure matplotlib dependencies are installed

### Getting Help
1. Check the **Issues** tab for similar problems
2. Review **GitHub Actions** logs for detailed error messages
3. Verify all setup steps were completed correctly

## 🎨 Advanced Features

### Potential Enhancements
- **Multiple Chart Types**: Pie charts, progress bars, calendars
- **Seasonal Themes**: Holiday-specific colors and messages
- **Historical Data**: Track progress over multiple years
- **Interactive Features**: Polls, Q&A, goal tracking
- **Multi-Platform**: Post to LinkedIn, Instagram, etc.
- **Analytics Dashboard**: Track bot performance and engagement

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Ways to Contribute:
- 🐛 Report bugs
- 💡 Suggest new features  
- 🎨 Improve chart designs
- 📝 Enhance documentation
- 🧪 Add tests

## 🙏 Acknowledgments

- Built with [Tweepy](https://www.tweepy.org/) for Twitter API integration
- Charts created with [Matplotlib](https://matplotlib.org/)
- Automated with [GitHub Actions](https://github.com/features/actions)

## 📈 Roadmap

- [ ] Add seasonal themes
- [ ] Implement goal tracking features
- [ ] Create web dashboard
- [ ] Add multiple social platform support
- [ ] Build mobile app companion

---

**Made with ❤️ for productivity and motivation**

*ProgressPulse - Feel the rhythm of your year* 🎯

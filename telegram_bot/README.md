# Telegram Bot - TON Economy Bot

A comprehensive Telegram bot built with aiogram 3.x featuring a TON-based economy system.

## Features

### 💰 Economy System
- **TON-based balance**: Users earn and withdraw TON cryptocurrency
- **Referral program**: Earn 0.025 TON for each referral
- **Withdrawal system**: Minimum withdrawal of 0.2 TON
- **Frozen balance**: 24-hour freeze period on rewards

### 📋 Task Management
- Users submit tasks with screenshots
- Admin approval workflow
- Reward distribution upon approval
- Task history tracking

### 🎁 Promo Code System
- Create promotional codes with custom rewards
- Usage limits and expiration dates
- One-time use per user

### 👥 Subscription System
- Channel subscription verification
- Daily reward claims
- Early unsubscribe penalty logic
- 24-hour reward freezing

### 🛠️ Admin Panel
- Review and approve/reject tasks
- Manage withdrawal requests
- Create promo codes
- View user statistics
- Action logging

### 🌐 Internationalization (i18n)
- Multi-language support (English/Russian)
- User language preference storage
- Easy to add new languages

## Project Structure

```
telegram_bot/
├── app/
│   ├── config.py           # Configuration management
│   ├── database/
│   │   ├── __init__.py     # Database connection
│   │   └── repositories.py # Data access layer
│   ├── handlers/
│   │   ├── __init__.py     # Handler registration
│   │   ├── start.py        # Start command & registration
│   │   ├── balance.py      # Balance & economy
│   │   ├── referral.py     # Referral system
│   │   ├── tasks.py        # Task submission
│   │   ├── withdraw.py     # Withdrawal system
│   │   ├── promo.py        # Promo codes
│   │   └── admin.py        # Admin panel
│   ├── keyboards/
│   │   └── __init__.py     # Inline keyboards
│   ├── middlewares/
│   │   ├── __init__.py     # Middleware setup
│   │   ├── i18n.py         # Internationalization
│   │   └── auth.py         # Authentication
│   ├── models/
│   │   └── __init__.py     # SQLAlchemy models
│   └── utils/
│       └── __init__.py     # Utility functions
├── locales/
│   ├── en/LC_MESSAGES/     # English translations
│   └── ru/LC_MESSAGES/     # Russian translations
├── main.py                 # Bot entry point
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## Installation

### 1. Clone and Setup

```bash
cd telegram_bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
DATABASE_URL=sqlite+aiosqlite:///bot_database.db
TON_WALLET_ADDRESS=your_wallet_address
MIN_WITHDRAWAL_AMOUNT=0.2
REFERRAL_REWARD=0.025
SUBSCRIPTION_CHANNEL_ID=-1001234567890
FREEZE_PERIOD_HOURS=24
DEFAULT_LOCALE=en
AVAILABLE_LOCALES=en,ru
```

### 3. Run the Bot

```bash
python main.py
```

## Database Models

### User
- Telegram ID, username, name
- Balance (available & frozen)
- Referral tracking
- Subscription status
- Language preference

### Task
- Title, description, screenshot
- Status (pending/approved/rejected)
- Reward amount
- Admin review tracking

### Withdrawal
- Amount, wallet address
- Status (pending/processing/completed/rejected)
- Transaction hash
- Admin processing tracking

### PromoCode
- Code, reward amount
- Usage limits
- Expiration date

## Key Features Explained

### Referral System
- Each user gets a unique referral link
- Referrer earns 0.025 TON when referral joins
- Bonus tiers for multiple referrals

### Subscription Rewards
- Users must subscribe to channel
- 24-hour freeze on claimed rewards
- Penalty calculation for early unsubscribe

### Task Approval Flow
1. User submits task with screenshot
2. Admin reviews in pending queue
3. Admin approves (credits reward) or rejects (with comment)
4. User notified of decision

### Withdrawal Process
1. User requests withdrawal (min 0.2 TON)
2. Balance is immediately deducted
3. Admin reviews and processes
4. TON is sent to user's wallet
5. Transaction hash recorded

## Admin Commands

Admins (defined in `ADMIN_IDS`) can access:
- `/admin_panel` - Main admin menu
- Task review queue
- Withdrawal management
- Promo code creation
- User statistics

## Development

### Adding New Languages

1. Create locale directory: `locales/<lang>/LC_MESSAGES/`
2. Copy and translate `messages.po`
3. Compile translations (optional): `msgfmt -o messages.mo messages.po`
4. Add language code to `AVAILABLE_LOCALES` in config

### Adding New Handlers

1. Create handler file in `app/handlers/`
2. Define router and handlers
3. Register in `app/handlers/__init__.py`

### Database Migrations

For schema changes, you can:
1. Modify models in `app/models/__init__.py`
2. Delete `bot_database.db` (development only)
3. Restart bot to recreate tables

For production, use Alembic or similar migration tool.

## Security Considerations

- Admin IDs are validated on every admin action
- Wallet addresses are validated before withdrawal
- Promo codes have usage limits and expiration
- All admin actions are logged

## License

MIT License

## Support

For issues and feature requests, please open an issue on GitHub.

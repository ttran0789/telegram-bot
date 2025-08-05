# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Telegram bot project. The bot will be built using the `python-telegram-bot` library.

## Development Commands

Python environment: `C:\Users\tuan\Anaconda3\envs\env\python.exe`

- `"C:\Users\tuan\Anaconda3\envs\env\python.exe" bot.py` - Run the bot locally
- `"C:\Users\tuan\Anaconda3\envs\env\python.exe" -m pytest` - Run tests (when test framework is added)
- `"C:\Users\tuan\Anaconda3\envs\env\python.exe" -m pip install -r requirements.txt` - Install dependencies
- `"C:\Users\tuan\Anaconda3\envs\env\python.exe" -m flake8` or `"C:\Users\tuan\Anaconda3\envs\env\python.exe" -m black` - Code formatting/linting (when added)

## Architecture Notes

### Bot Structure
- Main bot file typically named `bot.py` or `main.py`
- Handlers for different command types (commands, messages, callbacks)
- Configuration management for bot token and settings
- Database integration if needed for user data/state

### Key Components
- **Bot Token**: Store in environment variables, never commit to code
- **Handlers**: Command handlers, message handlers, callback query handlers
- **Middleware**: For logging, authentication, rate limiting if needed
- **Database**: SQLite for simple projects, PostgreSQL for production
- **Deployment**: Consider Docker containerization

### Environment Setup
- Use `.env` file for local development (add to .gitignore)
- Required environment variables: `TELEGRAM_BOT_TOKEN`
- Optional: Database connection strings, API keys for external services

## Dependencies
- `python-telegram-bot` - Main Telegram bot framework
- `python-dotenv` - Environment variable management
- Database libraries as needed (sqlite3, psycopg2, etc.)
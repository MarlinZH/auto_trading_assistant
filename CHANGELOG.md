# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README with setup guide and features
- ARCHITECTURE.md documenting system design
- Unit tests for RiskManager and Config classes
- GitHub Actions CI/CD workflows for tests and security
- CONTRIBUTING.md with development guidelines
- Improved .gitignore for better file management

### Changed
- Renamed `auto_trade_fixed.py` to `trading_bot.py`
- Renamed `main_fixed.py` to `portfolio_sync.py`
- Consolidated requirements into single `requirements.txt` with pinned versions
- Updated README to reflect current architecture

### Deprecated
- `auto_trade.py` (replaced by `trading_bot.py`)
- `main.py` (replaced by `portfolio_sync.py`)
- `requirements_updated.txt` (consolidated into `requirements.txt`)

### Removed
- None yet (files to be removed in next commit)

## [0.2.0] - 2024-10

### Added
- Risk management system with position limits
- Stop loss and take profit functionality
- Daily trade limits
- Paper trading mode for safe testing
- Comprehensive logging system
- Security improvements and credential management
- Configuration validation

### Changed
- Improved error handling throughout codebase
- Centralized configuration management
- Enhanced security with .env file support

### Fixed
- Credential exposure in code
- Missing error handling in API calls
- Configuration validation issues

## [0.1.0] - 2024-07

### Added
- Initial automated trading bot
- Robinhood API integration
- Binance price data integration
- Notion portfolio sync
- Basic trading logic
- Portfolio snapshot analyzer
- Options tracking support

### Known Issues
- Hardcoded credentials (fixed in 0.2.0)
- Limited error handling (fixed in 0.2.0)
- No risk management (fixed in 0.2.0)

---

## Version History Summary

- **0.1.0** - Initial release with basic trading functionality
- **0.2.0** - Added risk management and security improvements
- **Unreleased** - Phase 1 cleanup and documentation improvements

## Upgrade Guide

### From 0.1.0 to 0.2.0

1. Create `.env` file based on `.env.example`
2. Move credentials from hardcoded values to `.env`
3. Update import statements if using as library
4. Configure risk management parameters

### From 0.2.0 to Unreleased

1. Rename script calls:
   - `python auto_trade_fixed.py` → `python trading_bot.py`
   - `python main_fixed.py` → `python portfolio_sync.py`
2. Update any custom scripts that import renamed modules
3. Install updated dependencies: `pip install -r requirements.txt`
4. Run tests to ensure everything works: `pytest tests/`
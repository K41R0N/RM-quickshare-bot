# Contributing to Telegram to reMarkable Bot

Thank you for your interest in contributing! This project welcomes contributions from everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- **Clear title** describing the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Logs** if available

### Suggesting Features

Feature requests are welcome! Please open an issue with:

- **Clear description** of the feature
- **Use case** - why is this useful?
- **Proposed implementation** (if you have ideas)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m 'Add amazing feature'`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Update documentation if needed

### Testing

Before submitting:

- Test with multiple article sources
- Verify EPUB creation works
- Check reMarkable upload succeeds
- Ensure no credentials are exposed

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/telegram-remarkable-bot.git
cd telegram-remarkable-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export TELEGRAM_TOKEN='your-test-token'

# Run the bot
python3 bot.py
```

## Areas for Contribution

### High Priority

- [ ] Add unit tests
- [ ] Improve error handling
- [ ] Support more article sources
- [ ] Add configuration file support
- [ ] Implement rate limiting

### Medium Priority

- [ ] Add article tagging
- [ ] Support custom EPUB styling
- [ ] Implement article queue
- [ ] Add web dashboard
- [ ] Support multiple languages

### Low Priority

- [ ] Docker support
- [ ] Kubernetes deployment
- [ ] Metrics and monitoring
- [ ] Article search functionality

## Questions?

Feel free to open an issue for any questions about contributing!

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to learn and improve.

---

**Thank you for contributing! 🎉**

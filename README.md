# The Blue List

A privacy-focused web application helping users make informed decisions about businesses, online security, home safety, and relocation options.

## Overview

The Blue List is an open-source platform providing resources and tools across four key areas:

1. **Ethical Business Directory**: Track political donations and find ethical alternatives
2. **Home Safety Guide**: Access personalized safety and preparedness recommendations
3. **Online Security Center**: Get customized digital security checklists and guides
4. **Relocation Resources**: Explore international relocation options and requirements

## PRIVACY DISCLAIMER
The Blue List does not collect any user information. A valid email address is required to add or edit business listings on The Blue List, but no other PII or user data is collected at any time.

## Features

### Ethical Business Directory
- Search companies by name or category
- View political donation history and percentages
- Find ethical alternatives in the same business category
- Location-based searching without tracking
- Private and secure - no user location data stored

### Home Safety Guide
- Downloadable general safety checklists
- Personalized recommendations based on:
  - Household size
  - Pets
  - Living space
  - Climate considerations
  - Medical requirements
- Focus on food safety, water access, and medical care

### Online Security Center
- Comprehensive security assessments
- Customized security checklists
- Recommendations for:
  - Encrypted communications
  - Secure browsers
  - VPN configuration
  - Network security
  - Data protection

### Relocation Resources
- Country guides for US expats
- Interactive questionnaires for personalized recommendations
- Detailed checklists covering:
  - Documentation requirements
  - Visa applications
  - Cost of living estimates
  - Employment opportunities
  - Preparation timelines

## Privacy & Security

- No user tracking
- No location data collection
- No personal data storage
- Open-source for transparency

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- Node.js & npm (for frontend assets)

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/thebluelist.git
cd thebluelist

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configurations

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Configuration
Key environment variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
DEBUG=True
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

### Development Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use Black for code formatting
- Include docstrings for all functions

## Testing

```bash
# Run all tests
python manage.py test

# Run specific test suite
python manage.py test online_security
```

## Deployment

The application is designed to be deployed on any Python-compatible hosting platform. Currently tested with:
- Railway
- Google Cloud Platform
- AWS

## Staying Updated

To ensure you have the latest version:

```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
```

## License

This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

- [Open an issue](https://github.com/yourusername/thebluelist/issues)

## Project Status

Currently in active development. See our [project board](https://github.com/yourusername/thebluelist/projects) for current progress and upcoming features.

## Acknowledgments

- All contributors and maintainers
- Open source community
- Privacy and security advocates
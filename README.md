# The Blue List
### https://www.mybluelist.org

A privacy-focused web application helping users make informed decisions about businesses, online security, home safety, and relocation options for the years ahead.

## Overview

The Blue List is an open-source platform providing resources and tools across four key areas:

1. **Ethical Business Directory**: Track political donations and find ethical alternatives
2. **Home Safety Guide**: Access personalized safety and preparedness recommendations
3. **Online Security Center**: Get customized digital security checklists and guides
4. **Relocation Resources**: Explore international relocation options and requirements

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
  - A valid email address is required to create an account, but is deleted after first login.
- Open-source for transparency

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Node.js & npm (for frontend assets)

### PostgreSQL Setup

#### On macOS
```bash
# Using Homebrew
brew install postgresql@14
brew services start postgresql@14

# Create database and user
psql postgres
CREATE DATABASE thebluelist;
CREATE USER your_database_user WITH PASSWORD 'your_password';
ALTER ROLE your_database_user SET client_encoding TO 'utf8';
ALTER ROLE your_database_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_database_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE thebluelist TO your_database_user;
\q
```

#### On Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo service postgresql start

# Create database and user
sudo -u postgres psql
CREATE DATABASE thebluelist;
CREATE USER your_database_user WITH PASSWORD 'your_password';
ALTER ROLE your_database_user SET client_encoding TO 'utf8';
ALTER ROLE your_database_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_database_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE thebluelist TO your_database_user;
\q
```

#### On Windows
1. Download PostgreSQL installer from https://www.postgresql.org/download/windows/
2. Run installer, noting down the password you set for the postgres user
3. Open pgAdmin (installed with PostgreSQL)
4. Create new database named 'thebluelist'
5. Create new user 'your_database_user' with appropriate privileges


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
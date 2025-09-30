# Interactive SQL Agent

An intelligent SQL database agent that can interact with various databases using natural language queries and batch execution for safe data modifications.

## Features

- 🤖 **Natural Language Interface** - Ask questions in plain English
- 📦 **Batch Execution Mode** - Plans and executes modifications safely
- 🔍 **Debug Mode** - See the actual SQL queries being executed
- 🎯 **Multi-Database Support** - Works with SQLite, PostgreSQL, MySQL, etc.
- ⚙️ **Configurable** - Customize behavior through environment variables

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd testing_blade
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the agent**:
   ```bash
   python testing_blade.py
   ```

## Configuration

All configuration is done through environment variables in the `.env` file:

### Database Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_URI` | Database connection string | `sqlite:///Chinook.db` | `postgresql://user:pass@localhost:5432/db` |
| `DATABASE_TYPE` | Database type for prompts | `SQLite` | `PostgreSQL`, `MySQL` |

### LLM Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key | *Required* | `sk-...` |
| `LLM_MODEL` | Model to use | `gpt-4o-mini` | `gpt-4`, `gpt-3.5-turbo` |
| `LLM_PROVIDER` | LLM provider | `openai` | `anthropic`, `azure` |

### Agent Behavior

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEBUG_MODE` | Show SQL queries | `false` | `true`, `false` |
| `BATCH_MODE` | Enable batch execution | `true` | `true`, `false` |
| `RECURSION_LIMIT` | Max agent steps | `50` | `30`, `100` |
| `TOP_K_RESULTS` | Max query results | `5` | `10`, `20` |

## Usage Examples

### Basic Queries
```
💬 You: How many artists are there?
💬 You: Show me albums by AC/DC
💬 You: What are the top 5 selling tracks?
```

### Batch Modifications
```
💬 You: Create a new artist called "Rock Stars" with an album "Best Songs" and 3 tracks

🤖 SQL Agent: I need to perform these operations:
1. Create new artist "Rock Stars"
2. Create new album "Best Songs" for this artist
3. Add track "Song 1" to the album
4. Add track "Song 2" to the album  
5. Add track "Song 3" to the album

Should I proceed with this plan?

💬 You: yes
```

## Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `config` | Show current configuration |
| `debug` | Toggle debug mode |
| `batch` | Toggle batch execution mode |
| `clear` | Clear conversation history |
| `exit` | Exit the application |

## Database Support

### SQLite
```env
DATABASE_URI=sqlite:///path/to/database.db
DATABASE_TYPE=SQLite
```

### PostgreSQL
```env
DATABASE_URI=postgresql://username:password@localhost:5432/database_name
DATABASE_TYPE=PostgreSQL
```

### MySQL
```env
DATABASE_URI=mysql://username:password@localhost:3306/database_name
DATABASE_TYPE=MySQL
```

## Safety Features

- **Batch Planning**: Modifications are planned and confirmed before execution
- **Transaction Safety**: All modifications in a single transaction
- **Error Recovery**: Automatic rollback on failures
- **User Confirmation**: Clear plans in plain English before execution

## Development

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Testing
```bash
# Run with debug mode
DEBUG_MODE=true python testing_blade.py

# Test with different database
DATABASE_URI=postgresql://localhost/test python testing_blade.py
```

## Troubleshooting

### Database Connection Issues
- Check `DATABASE_URI` format
- Verify database server is running
- Ensure credentials are correct

### LLM Issues
- Verify `OPENAI_API_KEY` is set
- Check API key has sufficient credits
- Try different `LLM_MODEL` if needed

### Performance Issues
- Reduce `RECURSION_LIMIT` for faster responses
- Lower `TOP_K_RESULTS` for smaller result sets
- Enable `DEBUG_MODE` to see what's happening

## Makefile Manual

This project includes a comprehensive Makefile that automates all development tasks. Here's a complete guide to all available commands:

### Quick Reference

```bash
make help          # Show all available commands
make setup         # Complete project setup
make run           # Run the SQL agent
make debug         # Debug with pdb
```

### Setup Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `make setup` | Complete project setup (venv + dependencies + database) | First-time setup |
| `make venv` | Create Python virtual environment | Manual venv creation |
| `make install` | Install Python dependencies from requirements.txt | After adding new deps |
| `make download-db` | Download and create Chinook SQLite database | Database setup |

**Example Setup Workflow:**
```bash
# Clone the repository
git clone <repository-url>
cd testing_blade

# Complete setup in one command
make setup

# Start using the agent
make run
```

### Development Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `make run` | Run the SQL agent with default settings | Daily development |
| `make run-high-limit` | Run with higher recursion limit (100) | Complex operations |
| `make debug` | Run agent in debug mode with Python debugger (pdb) | Troubleshooting |
| `make freeze` | Update requirements.txt with current dependencies | After installing new packages |

**Development Examples:**
```bash
# Normal usage
make run

# For complex batch operations that might hit recursion limits
make run-high-limit

# Debug a specific issue
make debug
# In pdb: use 'n' (next), 's' (step), 'c' (continue), 'l' (list), 'p <var>' (print)

# After installing new packages
pip install some-new-package
make freeze
```

### Maintenance Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `make clean` | Remove generated files (__pycache__, *.pyc, etc.) | Clean workspace |
| `make clean-all` | Remove everything including virtual environment | Fresh start |
| `make update` | Update all dependencies to latest versions | Dependency updates |
| `make test` | Test database connection and show basic info | Verify setup |

**Maintenance Examples:**
```bash
# Clean up generated files
make clean

# Complete reset (useful for troubleshooting)
make clean-all
make setup

# Update dependencies
make update
```

### Environment Management

| Command | Description | Usage |
|---------|-------------|-------|
| `make env-example` | Create .env file from .env.example template | Initial configuration |
| `make check-env` | Validate environment configuration | Verify settings |

**Environment Setup:**
```bash
# Create .env from template
make env-example

# Edit .env with your settings
nano .env

# Verify configuration
make check-env
```

### Database Management

| Command | Description | Usage |
|---------|-------------|-------|
| `make db-info` | Show database statistics (tables, record counts) | Database overview |
| `make db-reset` | Delete and re-download database | Reset to clean state |

**Database Examples:**
```bash
# Check database status
make db-info

# Reset database to original state
make db-reset
```

### Advanced Usage

#### Custom Environment Variables
```bash
# Run with custom recursion limit
RECURSION_LIMIT=150 make run

# Run with debug mode enabled
DEBUG_MODE=true make run

# Use different database
DATABASE_URI=postgresql://localhost/mydb make run
```

#### Development Shortcuts
```bash
# Quick development cycle
make dev              # Equivalent to: make setup run

# Complete restart
make restart          # Equivalent to: make clean-all setup run

# Quick run (skip checks)
make quick-run        # Direct python execution
```

#### Troubleshooting Commands
```bash
# Test database connection
make test

# Check environment configuration
make check-env

# View database information
make db-info

# Reset everything
make clean-all setup
```

### Makefile Features

#### Smart Validation
- Checks for required files before running
- Validates database existence
- Verifies environment configuration
- Provides helpful error messages

#### Colored Output
- 🔴 Red: Errors and warnings
- 🟢 Green: Success messages
- 🟡 Yellow: In-progress operations
- 🔵 Blue: Information messages

#### Error Recovery
- Automatically creates requirements.txt if missing
- Downloads database if not found
- Creates virtual environment as needed
- Provides clear next steps on failures

#### Cross-Platform Compatibility
- Works on macOS, Linux, and Windows (with make installed)
- Uses standard Unix commands
- Handles path differences automatically

### Common Workflows

#### First Time Setup
```bash
git clone <repo>
cd testing_blade
make setup
# Edit .env with your API key
make run
```

#### Daily Development
```bash
make run              # Start the agent
# ... work with the agent ...
make clean            # Clean up when done
```

#### Adding New Dependencies
```bash
source venv/bin/activate  # Activate venv
pip install new-package   # Install package
make freeze              # Update requirements.txt
git add requirements.txt  # Commit changes
```

#### Troubleshooting
```bash
make test             # Test database connection
make check-env        # Verify environment
make db-info          # Check database status
make clean-all setup  # Nuclear option: reset everything
```

#### Complex Operations
```bash
make run-high-limit   # For batch operations that need more steps
make debug           # For investigating issues
```

### Tips and Best Practices

1. **Always run `make setup` first** - It handles all dependencies
2. **Use `make help`** - Shows all available commands with descriptions  
3. **Check `make test`** - Verifies your setup is working
4. **Use `make clean`** - Regularly clean generated files
5. **Try `make run-high-limit`** - For complex batch operations
6. **Use `make debug`** - When you need to investigate issues
7. **Run `make freeze`** - After installing new packages
8. **Use `make db-reset`** - To start with a fresh database

## License

MIT License - see LICENSE file for details.

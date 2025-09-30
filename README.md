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

## License

MIT License - see LICENSE file for details.

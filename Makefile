# =============================================================================
# Interactive SQL Agent - Makefile
# =============================================================================

# Variables
VENV_NAME = venv
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
DB_FILE = Chinook.db
SQL_FILE = Chinook_Sqlite.sql
REQUIREMENTS = requirements.txt
MAIN_SCRIPT = testing_blade.py

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Default target
.PHONY: help
help:
	@echo "$(BLUE)Interactive SQL Agent - Available Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(NC)"
	@echo "  make setup          - Complete setup (venv + deps + db)"
	@echo "  make venv           - Create virtual environment"
	@echo "  make install        - Install dependencies"
	@echo "  make download-db    - Download Chinook database"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@echo "  make run            - Run the SQL agent"
	@echo "  make run-high-limit - Run with higher recursion limit (100)"
	@echo "  make debug          - Run the agent in debug mode with pdb"
	@echo "  make freeze         - Freeze dependencies to requirements.txt"
	@echo ""
	@echo "$(GREEN)Maintenance Commands:$(NC)"
	@echo "  make clean          - Clean generated files"
	@echo "  make clean-all      - Clean everything including venv"
	@echo "  make update         - Update dependencies"
	@echo "  make test           - Test database connection"
	@echo ""

# =============================================================================
# Setup Commands
# =============================================================================

.PHONY: setup
setup: venv install download-db
	@echo "$(GREEN)✅ Setup complete! Run 'make run' to start the agent.$(NC)"

.PHONY: venv
venv:
	@echo "$(YELLOW)🔧 Creating virtual environment...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then \
		python3 -m venv $(VENV_NAME); \
		echo "$(GREEN)✅ Virtual environment created$(NC)"; \
	else \
		echo "$(BLUE)ℹ️  Virtual environment already exists$(NC)"; \
	fi

.PHONY: install
install: venv
	@echo "$(YELLOW)📦 Installing dependencies...$(NC)"
	@if [ -f "$(REQUIREMENTS)" ]; then \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r $(REQUIREMENTS); \
		echo "$(GREEN)✅ Dependencies installed$(NC)"; \
	else \
		echo "$(RED)❌ requirements.txt not found. Creating basic requirements...$(NC)"; \
		$(PIP) install --upgrade pip; \
		$(PIP) install langchain langchain-community langchain-openai langgraph python-dotenv; \
		$(MAKE) freeze; \
	fi

.PHONY: download-db
download-db:
	@echo "$(YELLOW)🗄️  Downloading Chinook database...$(NC)"
	@if [ ! -f "$(DB_FILE)" ]; then \
		echo "$(BLUE)📥 Fetching SQL file...$(NC)"; \
		curl -s https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql -o $(SQL_FILE); \
		if [ -f "$(SQL_FILE)" ]; then \
			echo "$(BLUE)🔨 Creating SQLite database...$(NC)"; \
			sqlite3 $(DB_FILE) < $(SQL_FILE); \
			rm $(SQL_FILE); \
			echo "$(GREEN)✅ Chinook database created successfully$(NC)"; \
		else \
			echo "$(RED)❌ Failed to download SQL file$(NC)"; \
			exit 1; \
		fi \
	else \
		echo "$(BLUE)ℹ️  Database already exists$(NC)"; \
	fi

# =============================================================================
# Development Commands
# =============================================================================

.PHONY: run
run: venv
	@echo "$(YELLOW)🚀 Starting SQL Agent...$(NC)"
	@if [ ! -f "$(DB_FILE)" ]; then \
		echo "$(RED)❌ Database not found. Run 'make download-db' first.$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)⚠️  .env file not found. Using defaults...$(NC)"; \
	fi
	@$(PYTHON) $(MAIN_SCRIPT)

.PHONY: debug
debug: venv
	@echo "$(YELLOW)🐛 Starting SQL Agent in debug mode with pdb...$(NC)"
	@if [ ! -f "$(DB_FILE)" ]; then \
		echo "$(RED)❌ Database not found. Run 'make download-db' first.$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)⚠️  .env file not found. Using defaults...$(NC)"; \
	fi
	@echo "$(BLUE)ℹ️  Debug commands: 'n' (next), 's' (step), 'c' (continue), 'l' (list), 'p <var>' (print)$(NC)"
	@$(PYTHON) -m pdb $(MAIN_SCRIPT)

.PHONY: run-high-limit
run-high-limit: venv
	@echo "$(YELLOW)🚀 Starting SQL Agent with high recursion limit...$(NC)"
	@if [ ! -f "$(DB_FILE)" ]; then \
		echo "$(RED)❌ Database not found. Run 'make download-db' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)ℹ️  Using recursion limit: 100$(NC)"
	@RECURSION_LIMIT=100 $(PYTHON) $(MAIN_SCRIPT)

.PHONY: freeze
freeze: venv
	@echo "$(YELLOW)❄️  Freezing dependencies...$(NC)"
	@$(PIP) freeze > $(REQUIREMENTS)
	@echo "$(GREEN)✅ Dependencies frozen to $(REQUIREMENTS)$(NC)"

# =============================================================================
# Maintenance Commands
# =============================================================================

.PHONY: clean
clean:
	@echo "$(YELLOW)🧹 Cleaning generated files...$(NC)"
	@rm -f $(SQL_FILE)
	@rm -rf __pycache__
	@rm -rf *.pyc
	@rm -rf .pytest_cache
	@echo "$(GREEN)✅ Cleaned generated files$(NC)"

.PHONY: clean-all
clean-all: clean
	@echo "$(YELLOW)🧹 Cleaning everything including virtual environment...$(NC)"
	@rm -rf $(VENV_NAME)
	@rm -f $(DB_FILE)
	@echo "$(GREEN)✅ Cleaned everything$(NC)"

.PHONY: update
update: venv
	@echo "$(YELLOW)🔄 Updating dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install --upgrade -r $(REQUIREMENTS)
	@$(MAKE) freeze
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

.PHONY: test
test: venv
	@echo "$(YELLOW)🧪 Testing database connection...$(NC)"
	@if [ ! -f "$(DB_FILE)" ]; then \
		echo "$(RED)❌ Database not found. Run 'make download-db' first.$(NC)"; \
		exit 1; \
	fi
	@$(PYTHON) -c "from langchain_community.utilities import SQLDatabase; db = SQLDatabase.from_uri('sqlite:///$(DB_FILE)'); print('✅ Database connection successful'); print(f'📊 Tables: {len(db.get_usable_table_names())}')"

# =============================================================================
# Development Shortcuts
# =============================================================================

.PHONY: dev
dev: setup run

.PHONY: restart
restart: clean-all setup run

.PHONY: quick-run
quick-run:
	@$(PYTHON) $(MAIN_SCRIPT)

# =============================================================================
# Environment Management
# =============================================================================

.PHONY: env-example
env-example:
	@echo "$(YELLOW)📝 Creating .env from example...$(NC)"
	@if [ ! -f ".env" ] && [ -f ".env.example" ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ .env created from .env.example$(NC)"; \
		echo "$(YELLOW)⚠️  Please edit .env with your configuration$(NC)"; \
	else \
		echo "$(BLUE)ℹ️  .env already exists or .env.example not found$(NC)"; \
	fi

.PHONY: check-env
check-env:
	@echo "$(YELLOW)🔍 Checking environment configuration...$(NC)"
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ .env file exists$(NC)"; \
		if grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then \
			echo "$(RED)❌ Please set your OPENAI_API_KEY in .env$(NC)"; \
		else \
			echo "$(GREEN)✅ OPENAI_API_KEY appears to be set$(NC)"; \
		fi \
	else \
		echo "$(RED)❌ .env file not found$(NC)"; \
		echo "$(BLUE)ℹ️  Run 'make env-example' to create one$(NC)"; \
	fi

# =============================================================================
# Database Management
# =============================================================================

.PHONY: db-info
db-info:
	@echo "$(YELLOW)📊 Database information...$(NC)"
	@if [ -f "$(DB_FILE)" ]; then \
		echo "$(GREEN)✅ Database exists: $(DB_FILE)$(NC)"; \
		sqlite3 $(DB_FILE) "SELECT 'Tables: ' || COUNT(*) FROM sqlite_master WHERE type='table';"; \
		sqlite3 $(DB_FILE) "SELECT 'Artists: ' || COUNT(*) FROM Artist;"; \
		sqlite3 $(DB_FILE) "SELECT 'Albums: ' || COUNT(*) FROM Album;"; \
		sqlite3 $(DB_FILE) "SELECT 'Tracks: ' || COUNT(*) FROM Track;"; \
	else \
		echo "$(RED)❌ Database not found$(NC)"; \
	fi

.PHONY: db-reset
db-reset:
	@echo "$(YELLOW)🔄 Resetting database...$(NC)"
	@rm -f $(DB_FILE)
	@$(MAKE) download-db

# =============================================================================
# Special Targets
# =============================================================================

# Prevent make from deleting intermediate files
.PRECIOUS: $(VENV_NAME) $(DB_FILE)

# Ensure these targets run even if files with same names exist
.PHONY: all clean install run debug test help

from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from dotenv import load_dotenv

import os

# Load environment variables from .env file
load_dotenv()

db = SQLDatabase.from_uri("sqlite:///Chinook.db")


# Check if OpenAI API key is loaded from environment
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# Agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

system_message = """
You are an expert SQL database agent designed to interact with a {dialect} database.

## Core Instructions:
1. **Always start by examining the database schema** - Use the list tables and describe schema tools to understand the available tables and their structure.

2. **Query Construction**:
   - Create syntactically correct {dialect} queries
   - Only select relevant columns, never use SELECT *
   - Limit results to {top_k} unless user specifies otherwise
   - Order results by relevant columns when appropriate

3. **Query Validation**:
   - **ALWAYS double-check your queries before execution**
   - Verify column names exist in the correct tables
   - Check foreign key relationships and constraints
   - Ensure proper JOIN syntax when combining tables

4. **Error Handling**:
   - If a SELECT query fails, analyze the error and rewrite the query
   - For data modification queries (INSERT/UPDATE/DELETE), be extra cautious
   - Never retry failed modification queries without understanding the cause

5. **Data Modifications - BATCH EXECUTION MODE**:
   - **Plan first, execute later** - When user requests modifications, create a complete execution plan
   - **Group related operations** - Combine all necessary INSERTs, UPDATEs, DELETEs into a single plan
   - **Explain in simple terms** - Describe what each step will accomplish
   - **No partial executions** - Either plan everything or ask for clarification
   - **Use transactions automatically** - All planned modifications will be executed in a single transaction
   - For INSERT operations: Check for required fields and proper data types
   - For UPDATE operations: Always use WHERE clauses to avoid unintended changes
   - For DELETE operations: Use WHERE clauses and verify the scope of deletion

## Planning Format:
When user requests modifications, respond with:
1. "I need to perform these operations:"
2. List each step in simple language
3. Ask "Should I proceed with this plan?"
4. Wait for user confirmation before executing

6. **Response Format**:
   - Provide clear, concise answers based on query results
   - Explain any assumptions made
   - If data is missing or unclear, state this explicitly

## Database-Specific Notes:
- This is a {dialect} database
- **You can only execute one statement at a time** - Each SQL command must be executed separately
- Each SQL statement executes independently
- Use proper {dialect} syntax and functions
- Be mindful of {dialect}-specific data types and constraints

Remember: Accuracy and data integrity are paramount. When in doubt, examine the schema and test with simple queries first.
""".format(
    dialect="SQLite",
    top_k=5,
)

agent_executor = create_react_agent(
    llm,
    tools,
    prompt=system_message,
)

# Debug mode - set to True to see all SQL queries
DEBUG_MODE = False

# Batch execution mode
BATCH_MODE = True


def requires_modifications(user_input):
    """Detect if the request requires database modifications"""
    modification_keywords = [
        "create",
        "add",
        "insert",
        "new",
        "make",
        "update",
        "change",
        "modify",
        "edit",
        "alter",
        "delete",
        "remove",
        "drop",
        "clear",
    ]

    return any(keyword in user_input.lower() for keyword in modification_keywords)


def is_modification_query(query):
    """Detect if a SQL query is a modification"""
    query_upper = query.upper().strip()
    modification_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    return any(query_upper.startswith(keyword) for keyword in modification_keywords)


def execute_with_batch_safety(conversation_history):
    """Execute agent with batch safety checks"""

    # Check if this might be a modification request
    last_message = conversation_history[-1]["content"]
    might_modify = requires_modifications(last_message)

    if BATCH_MODE and might_modify:
        print("🔍 Detected potential modification request")
        print("📋 Agent will plan operations before executing")

    # Execute agent normally - the updated prompt will handle planning
    agent_response = ""
    step_count = 0
    executed_queries = []

    for step in agent_executor.stream(
        {"messages": conversation_history.copy()},
        stream_mode="values",
        recursion_limit=50,
    ):
        if step.get("messages"):
            last_message = step["messages"][-1]

            # Show agent steps
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                step_count += 1
                tool_call = last_message.tool_calls[0]
                tool_name = tool_call["name"]
                print(f"🔧 Step {step_count}: Executing {tool_name}")

                # Show SQL query in debug mode
                if DEBUG_MODE and tool_name == "sql_db_query":
                    query = tool_call.get("args", {}).get("query", "")
                    if query:
                        print(f"   📝 SQL Query: {query}")
                        executed_queries.append(query)
                elif DEBUG_MODE and tool_name == "sql_db_query_checker":
                    query = tool_call.get("args", {}).get("query", "")
                    if query:
                        print(f"   🔍 Checking Query: {query}")

            # Capture final response
            if last_message.content and last_message.content != agent_response:
                agent_response = last_message.content

    return agent_response, executed_queries


def interactive_cli():
    """Interactive CLI interface to chat with the SQL agent"""
    global DEBUG_MODE, BATCH_MODE

    print("🤖 Interactive SQL Agent")
    print("=" * 50)
    print("Ask questions about the database.")
    print("Special commands:")
    print("  - 'exit' or 'quit': Exit the program")
    print("  - 'clear': Clear conversation history")
    print("  - 'debug': Toggle debug mode (show SQL queries)")
    print("  - 'batch': Toggle batch execution mode")
    print("  - 'help': Show this help")
    print("=" * 50)
    print(f"🔍 Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")
    print(f"📦 Batch mode: {'ON' if BATCH_MODE else 'OFF'}")

    # Conversation history
    conversation_history = []

    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()

            # Special commands
            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye!")
                break
            elif user_input.lower() == "clear":
                conversation_history = []
                print("\n🧹 History cleared.")
                continue
            elif user_input.lower() == "debug":
                DEBUG_MODE = not DEBUG_MODE
                print(f"\n🔍 Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")
                continue
            elif user_input.lower() == "batch":
                BATCH_MODE = not BATCH_MODE
                print(f"\n📦 Batch mode: {'ON' if BATCH_MODE else 'OFF'}")
                continue
            elif user_input.lower() == "help":
                print("\n📖 Help:")
                print("  - You can ask questions about the Chinook database")
                print(
                    "  - Examples: 'How many artists are there?', 'Show AC/DC albums'"
                )
                print("  - The agent can create, modify and query data")
                print("  - Use 'debug' to toggle SQL query visibility")
                print("  - Use 'batch' to toggle batch execution mode")
                print(
                    "  - In batch mode, modifications are planned first, then executed"
                )
                continue
            elif not user_input:
                print("⚠️  Please write a question.")
                continue

            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})

            print("\n🤖 SQL Agent: Processing your query...")
            if BATCH_MODE:
                print(
                    "📦 Batch mode: Modifications will be planned and executed together"
                )
            print("-" * 40)

            # Execute agent with batch safety
            agent_response, executed_queries = execute_with_batch_safety(
                conversation_history
            )

            # Show final response
            print("-" * 40)
            print("✅ Response:")
            print(agent_response)

            # Show summary of executed queries if any modifications were made
            if executed_queries and any(
                is_modification_query(q) for q in executed_queries
            ):
                modification_queries = [
                    q for q in executed_queries if is_modification_query(q)
                ]
                print(
                    f"\n📊 Summary: {len(modification_queries)} modification(s) executed"
                )
                if DEBUG_MODE:
                    for i, query in enumerate(modification_queries, 1):
                        print(f"   {i}. {query}")

            # Add agent response to history
            if agent_response:
                conversation_history.append(
                    {"role": "assistant", "content": agent_response}
                )

        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
            continue
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Try with another question.")
            continue


if __name__ == "__main__":
    interactive_cli()

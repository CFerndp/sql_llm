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

5. **Data Modifications**:
   - **Always use transactions for data modifications** - Wrap INSERT/UPDATE/DELETE operations in BEGIN/COMMIT blocks
   - **Transaction pattern**: BEGIN TRANSACTION; [your modifications]; COMMIT; 
   - **Error handling**: If any modification fails, execute ROLLBACK to revert all changes
   - For INSERT operations: Check for required fields and proper data types
   - For UPDATE operations: Always use WHERE clauses to avoid unintended changes
   - For DELETE operations: Use WHERE clauses and verify the scope of deletion
   - **Important**: {dialect} executes each statement individually - plan accordingly
   - **Never leave transactions open** - Always COMMIT or ROLLBACK

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


def interactive_cli():
    """Interactive CLI interface to chat with the SQL agent"""
    global DEBUG_MODE

    print("🤖 Interactive SQL Agent")
    print("=" * 50)
    print("Ask questions about the database.")
    print("Special commands:")
    print("  - 'exit' or 'quit': Exit the program")
    print("  - 'clear': Clear conversation history")
    print("  - 'debug': Toggle debug mode (show SQL queries)")
    print("  - 'help': Show this help")
    print("=" * 50)
    print(f"🔍 Debug mode: {'ON' if DEBUG_MODE else 'OFF'}")

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
            elif user_input.lower() == "help":
                print("\n📖 Help:")
                print("  - You can ask questions about the Chinook database")
                print(
                    "  - Examples: 'How many artists are there?', 'Show AC/DC albums'"
                )
                print("  - The agent can create, modify and query data")
                print("  - Use 'debug' to toggle SQL query visibility")
                continue
            elif not user_input:
                print("⚠️  Please write a question.")
                continue

            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})

            print("\n🤖 SQL Agent: Processing your query...")
            print("-" * 40)

            # Execute agent with complete history
            agent_response = ""
            step_count = 0

            for step in agent_executor.stream(
                {"messages": conversation_history.copy()},
                stream_mode="values",
                recursion_limit=80,
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
                        elif DEBUG_MODE and tool_name == "sql_db_query_checker":
                            query = tool_call.get("args", {}).get("query", "")
                            if query:
                                print(f"   🔍 Checking Query: {query}")

                    # Capture final response
                    if last_message.content and last_message.content != agent_response:
                        agent_response = last_message.content

            # Show final response
            print("-" * 40)
            print("✅ Response:")
            print(agent_response)

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

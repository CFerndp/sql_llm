from reprlib import recursive_repr
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

# from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import ast
import re

# from IPython.display import Image, display

from typing_extensions import Annotated


from typing_extensions import TypedDict
from dotenv import load_dotenv

import os

# Load environment variables from .env file
load_dotenv()

db = SQLDatabase.from_uri("sqlite:///Chinook.db")


class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str


# Check if OpenAI API key is loaded from environment
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# system_message = """
# Given an input question, create a syntactically correct {dialect} query to
# run to help find the answer. Unless the user specifies in his question a
# specific number of examples they wish to obtain, always limit your query to
# at most {top_k} results. You can order the results by a relevant column to
# return the most interesting examples in the database.

# Never query for all the columns from a specific table, only ask for a the
# few relevant columns given the question.

# Pay attention to use only the column names that you can see in the schema
# description. Be careful to not query for columns that do not exist. Also,
# pay attention to which column is in which table.

# Only use the following tables:
# {table_info}
# """

# user_prompt = "Question: {input}"

# query_prompt_template = ChatPromptTemplate(
#     [("system", system_message), ("user", user_prompt)]
# )


# class QueryOutput(TypedDict):
#     """Generated SQL query."""

#     query: Annotated[str, ..., "Syntactically valid SQL query."]


# def write_query(state: State):
#     """Generate SQL query to fetch information."""
#     prompt = query_prompt_template.invoke(
#         {
#             "dialect": db.dialect,
#             "top_k": 10,
#             "table_info": db.get_table_info(),
#             "input": state["question"],
#         }
#     )
#     structured_llm = llm.with_structured_output(QueryOutput)
#     result = structured_llm.invoke(prompt)
#     return {"query": result["query"]}


# def execute_query(state: State):
#     """Execute SQL query."""
#     execute_query_tool = QuerySQLDatabaseTool(db=db)
#     return {"result": execute_query_tool.invoke(state["query"])}


# def generate_answer(state: State):
#     """Answer question using retrieved information as context."""
#     prompt = (
#         "Given the following user question, corresponding SQL query, "
#         "and SQL result, answer the user question.\n\n"
#         f"Question: {state['question']}\n"
#         f"SQL Query: {state['query']}\n"
#         f"SQL Result: {state['result']}"
#     )
#     response = llm.invoke(prompt)
#     return {"answer": response.content}


# graph_builder = StateGraph(State).add_sequence(
#     [write_query, execute_query, generate_answer]
# )
# graph_builder.add_edge(START, "write_query")
# graph = graph_builder.compile()


# # display(Image(graph.get_graph().draw_mermaid_png()))

# # for step in graph.stream(
# #     {"question": "How many employees are there?"}, stream_mode="updates"
# # ):
# #     print(step)


# memory = MemorySaver()
# graph = graph_builder.compile(checkpointer=memory, interrupt_before=["execute_query"])

# # Now that we're using persistence, we need to specify a thread ID
# # so that we can continue the run after review.
# config = {"configurable": {"thread_id": "1"}}

# for step in graph.stream(
#     {"question": "How many employees are there?"},
#     config,
#     stream_mode="updates",
# ):
#     print(step)

# try:
#     user_approval = input("Do you want to go to execute query? (yes/no): ")
# except Exception:
#     user_approval = "no"

# if user_approval.lower() == "yes":
#     # If approved, continue the graph execution
#     for step in graph.stream(None, config, stream_mode="updates"):
#         print(step)
# else:
#     print("Operation cancelled by user.")


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

question = """
Dame toda la información del artista Test Extreme
"""


for step in agent_executor.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
    recursion_limit=80,
):
    step["messages"][-1].pretty_print()

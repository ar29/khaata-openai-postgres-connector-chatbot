import chainlit as cl
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.tools import tool
import os
import openai
import psycopg2
from typing import Optional
import chainlit as cl
from dotenv import load_dotenv, find_dotenv
# from pydantic.v1 import BaseModel
from pydantic.v1 import BaseModel, Field

_ = load_dotenv(find_dotenv()) # read local .env file
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = "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"


# Define the input schema
class SQLQueryInput(BaseModel):
    sql_query: str = (Field(..., description="SQL Query of the given input in natural language to fetch data for"))

@tool(args_schema=SQLQueryInput)
def run_sql_query(sql_query: float) -> dict:
    """
    Execute a SQL query on a PostgreSQL database and return the results as a dictionary.

    Parameters:
    - sql_query: The SQL query to be executed. the sql query must end with a semicolon.

    Returns:
    A list of dictionaries where each dictionary represents a row of the result set.
    """
    connection_params = {
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'lol',
        'port': 5433
    }

    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(**connection_params)

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    connection.set_session(readonly=True)

    # Execute the SQL query
    try:
        cursor.execute(sql_query)
    except psycopg2.errors.UndefinedFunction:
       return f"""
            This query resulted in an Undefined Function exception in postgres.
            Try tweaking the prompt (use alternative postgres SQL syntax).
            The SQL Query used is:
            {sql_query}"""
    except psycopg2.errors.SyntaxError:
       return f"""
            This query resulted in an Syntax error exception in postgres.
            Try tweaking the prompt (use alternative postgres SQL syntax).
            The SQL Query used is:
            {sql_query}"""
    # Fetch all rows from the result set
    rows = cursor.fetchall()

    # Get the column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Create a list of dictionaries where each dictionary represents a row
    result_set = [dict(zip(column_names, row)) for row in rows]

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    return result_set
    


@cl.on_chat_start
def agent():    

    tools = [run_sql_query]
    functions = [format_tool_to_openai_function(f) for f in tools]
    model = ChatOpenAI(temperature=0,openai_api_key=openai.api_key).bind(functions=functions)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You're given the schema for various tables in a relational database. 
        you will have to generate SQL queries that query for inputs given to you.
        If any syntax error or undefined function error is encountered, re run the query with alternate Postgres SQL syntax.
         
        CREATE TABLE public.transactions_orderdetails (
    id integer NOT NULL,
    sku character varying(255) NOT NULL,
    hsn character varying(255),
    sku_description character varying(255) NOT NULL,
    quantity integer NOT NULL,
    shipment_id character varying(255) NOT NULL,
    tax_exclusive_gross double precision NOT NULL,
    principal_amount_basis double precision NOT NULL,
    total_tax_amount double precision NOT NULL,
    compensatory_cess_tax double precision NOT NULL,
    cgst_rate double precision NOT NULL,
    cgst_amount double precision NOT NULL,
    sgst_rate double precision NOT NULL,
    sgst_amount double precision NOT NULL,
    igst_rate double precision NOT NULL,
    igst_amount double precision NOT NULL,
    tcs_cgst_rate double precision NOT NULL,
    tcs_cgst_amount double precision NOT NULL,
    tcs_sgst_rate double precision NOT NULL,
    tcs_sgst_amount double precision NOT NULL,
    tcs_utgst_rate double precision NOT NULL,
    tcs_utgst_amount double precision NOT NULL,
    tcs_igst_rate double precision NOT NULL,
    tcs_igst_amount double precision NOT NULL,
    shipping_amount_basis double precision NOT NULL,
    shipping_promo_discount_basis double precision NOT NULL,
    shipping_promo_tax double precision NOT NULL,
    shipping_cgst_tax double precision NOT NULL,
    shipping_sgst_tax double precision NOT NULL,
    shipping_igst_tax double precision NOT NULL,
    gift_wrap_amount_basis double precision NOT NULL,
    gift_wrap_promo_discount_basis double precision NOT NULL,
    gift_wrap_promo_tax double precision NOT NULL,
    gift_wrap_cgst_tax double precision NOT NULL,
    gift_wrap_sgst_tax double precision NOT NULL,
    gift_wrap_igst_tax double precision NOT NULL,
    item_promo_discount_basis double precision NOT NULL,
    item_promo_tax double precision NOT NULL,
    warehouse_id character varying(255),
    updated timestamp with time zone NOT NULL,
    created timestamp with time zone NOT NULL,
    order_table_id integer NOT NULL,
    line_item_id character varying(255) NOT NULL,
    is_inactive boolean NOT NULL,
    khaata_modified boolean NOT NULL
);
        
        CREATE TABLE public.transactions_orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    order_id character varying(255) NOT NULL,
    business_type character varying(255) NOT NULL,
    seller_gstin character varying(255),
    transaction_type character varying(255) NOT NULL,
    invoice_number character varying(255) NOT NULL,
    invoice_date date NOT NULL,
    order_date date NOT NULL,
    invoice_amount double precision NOT NULL,
    ship_from_state character varying(255),
    ship_to_state character varying(255),
    credit_note_no character varying(255),
    credit_note_date date,
    customer_name character varying(255),
    customer_phone character varying(255),
    customer_address character varying(255),
    customer_email character varying(255),
    payment_method_code character varying(255),
    updated timestamp with time zone NOT NULL,
    created timestamp with time zone NOT NULL,
    customer_country character varying(255),
    customer_pincode character varying(255),
    customer_state character varying(255),
    dispatch_carrier character varying(255),
    dispatch_date character varying(255),
    dispatch_destination character varying(255),
    dispatch_doc_no character varying(255)
);
    
    """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent_chain = RunnablePassthrough.assign(
        agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
    ) | prompt | model | OpenAIFunctionsAgentOutputParser()

    from langchain.memory import ConversationBufferMemory
    memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history")
    
    agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True, memory=memory)

    cl.user_session.set("agent_executor", agent_executor)
    return agent_executor


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.AppUser]:
  # Fetch the user matching username from your database
  # and compare the hashed password with the value stored in the database
  if (username, password) == ("mitalee@khaata.in", "admin"):
    return cl.AppUser(username="Mitalee", role="ADMIN", provider="credentials")
  else:
    return None


@cl.on_message
async def main(message: str):
    # Agent creation
    agent = cl.user_session.get("agent_executor")

    # Run model 
    result = agent.invoke({"input": message})
    answer = result['output'] 

    # Send a response back to the user
    await cl.Message(
        content=answer,
    ).send()
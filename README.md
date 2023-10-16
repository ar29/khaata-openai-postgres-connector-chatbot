# Installation
```
pip install -r requirements.txt
```

# To Execute, run:
```
chainlit run chatbot.py --port 8001
```

# Information
1. LLM used - LLama2 hosted on Baseten

# Test Plan

I have integrated ChatGPT with fintech APIs, with example prompts and responses, using LangChain, Alpha Vantage API, and Llama2 LLM.

Please find the github repository below with my code and execution instructions. https://github.com/ar29/demo-bind

Example prompts and responses - 

1.

1. User | 18:43:13 | what is the current stock price of INFY?
Chatbot |18:43:17 | According to the latest data from Alpha Vantage, the current stock price of Infosys Limited (INFY) is $13.45 USD per share.
2. 

User | 18:44:43 | What is the analyst buy/sell rating for INFY?
Chatbot | 18:44:51 |Based on the latest analysis from various financial institutions, the consensus buying rating for Infosys Ltd. (INFY) is currently neutral with a target price range of $12-$14 per share. It's important to note that these ratings may change over time and may differ among analysts, so it's always advisable to consult multiple sources before making investment decisions.
3.

User | 18:45:55 | what is the stock price of goog?
Chatbot | 18:46:00 | According to Alpha Vantage, the current intraday quote for Google (GOOGL) is $1342.50 USD per share.
4.

User | 18:46:21 | what is the historical performance of NASDAQ?
Chatbot | 18:46:28 | Based on the historical data retrieved from Alpha Vantage, the NASDAQ Composite Index has shown a strong upward trend over the past few decades, with some notable fluctuations along the way. Here are some key statistics:
As of March 2023, the all-time high of the NASDAQ Composite Index was reached in February 2023, at around 14,500 points.
Since its inception in 1971, the NASDAQ Composite Index has grown.


# Code Description
```
This code is a Python script for creating a chatbot or agent that can answer questions related to the stock market using a Llama2 language model (LLM) and external tools. Let's break down the code and explain what is happening in as much detail as possible:

1. Import Statements:
   - The script starts by importing various modules and libraries, including:
     - `langchain.agents`: Modules related to agents and tool execution.
     - `langchain.prompts`: Modules for defining prompts.
     - `langchain.utilities.alpha_vantage`: A wrapper for the Alpha Vantage API.
     - `langchain.llms`: Modules related to language models (LLMs).
     - `langchain`: The main LangChain library.
     - `typing`: The typing module for type hints.
     - `re`: The regular expressions module.
     - `os`: The operating system module.
     - `chainlit`: A library for defining chain of responsibility patterns.
   
2. Environment Variables:
   - The script sets environment variables for API keys related to Alpha Vantage and Llama2. These keys are used to authenticate with external services.

3. Prompt Template:
   - A template for questions and responses is defined as a multi-line string. This template includes placeholders for questions, actions, action inputs, and final answers.

4. `CustomPromptTemplate` Class:
   - A custom class is defined, which inherits from `StringPromptTemplate`. This class is responsible for formatting the template and populating it with dynamic content.
   - It overrides the `format` method to create a formatted prompt using the provided data. This includes information about available tools and previous intermediate steps in the conversation.

5. `CustomOutputParser` Class:
   - Another custom class is defined, which inherits from `AgentOutputParser`. This class is responsible for parsing the output generated by the language model.
   - It has a `parse` method that extracts information from the output, including agent actions and action inputs.

6. `@cl.on_chat_start` Decorator:
   - A decorator function is defined to create the agent when the chat session starts.
   - Inside this function, the following steps are performed:
     - An output parser is instantiated using the `CustomOutputParser` class.
     - An LLM (Language Model) instance is created using the `Baseten` class with a specific model identifier.
     - An instance of `AlphaVantageAPIWrapper` is created to access the Alpha Vantage API.
     - A list of tools is defined. In this case, there is a single tool named "Alpha Vantage" with a description.
     - A custom prompt template is created using the `CustomPromptTemplate` class.
     - An instance of `LLMChain` is created, combining the LLM, prompt template, and tools.
     - The tool names are extracted from the list of tools.
     - An instance of `LLMSingleActionAgent` is created, using the LLM chain, an output parser, and other configurations.
     - Finally, an `AgentExecutor` is created from the agent and tools, and it is stored in the user session.

7. `@cl.on_message` Decorator:
   - This decorator function handles incoming messages in the chat.
   - Inside this function, the following steps are performed:
     - The agent executor is retrieved from the user session.
     - The agent is run with the incoming message as input.
     - The response from the agent is generated.
     - The response is sent back to the user.

In summary, this code sets up an agent that uses a Llama2 language model and external tools (in this case, the Alpha Vantage API) to answer questions about the stock market. It defines custom classes for formatting prompts and parsing responses, and it handles user interactions in a chat session. The agent can generate final answers in a specific format.
```
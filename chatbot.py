from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.utilities.alpha_vantage import AlphaVantageAPIWrapper
from langchain.llms import Baseten

from langchain import LLMChain


from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
import re
import os
import chainlit as cl


import langchain
langchain.debug = True

os.environ["ALPHAVANTAGE_API_KEY"] = "7MHWTAWCKY3TLYOF"





os.environ["OPENAI_API_KEY"] = "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"

template = """
Answer the following questions as best you can, but speaking as a passionate stock market expert. You have access to the following tools:

{tools}

Use the following format:

Question: The question you have to answer
Thought: Your thought process in approaching the question
Action: Choose one of the available tools in [{tool_names}] for your action
Action Input: Provide the input required for the chosen tool
Observation: Describe the result obtained from the action
...(Repeat several times of the Thought/Action/Action Input/Observation as needed)
Thought: Now I have the final answer!
Final Answer: Provide your final answer from the perspective of an experienced stock market professional

Let's get started!
Question: {input}
{agent_scratchpad}"""

class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)



class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(llm_output)
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)



@cl.on_chat_start
def agent():
    output_parser = CustomOutputParser()
    llm = Baseten(model="qvv71eq")

    alpha_vantage = AlphaVantageAPIWrapper()

    tools = [
        Tool.from_function(
        func=alpha_vantage.run,
        name="Alpha Vantage",
        description="Use this to get currency exchange rates. Alpha Vantage provides realtime and historical financial market data through a set of powerful and developer-friendly data APIs and spreadsheets."
    )
    ]

    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"]
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]


    agent = LLMSingleActionAgent(llm_chain=llm_chain, verbose = True, handle_parsing_errors=True, output_parser=output_parser, stop=["\nObservation:"], allowed_tools=tool_names)

    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                    tools=tools,
                                                    verbose=True)
    
    cl.user_session.set("agent_executor", agent_executor)
    return agent_executor




@cl.on_message
async def main(message: str):
    # Retrieve the chain from the user session
    # Send the response

    # Agent creation
    agent = cl.user_session.get("agent_executor")

    # Run model 
    response = agent.run(message)

    # Send a response back to the user
    await cl.Message(
        content=response,
    ).send()
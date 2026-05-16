from langchain_classic.agents import initialize_agent, AgentType
from langchain_anthropic import ChatAnthropic

from tools.stock_signal_tool import stock_signal_tool

llm = ChatAnthropic(model="claude-opus-4-7")

tools = [stock_signal_tool]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
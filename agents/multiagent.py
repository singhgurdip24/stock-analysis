from langchain_classic.agents import initialize_agent, AgentType
from langchain_anthropic import ChatAnthropic

from tools.fundamentals_tool import fundamentals_tool
from tools.stock_signal_tool import stock_signal_tool
from tools.news_sentiment_tool import news_sentiment_tool

llm = ChatAnthropic(model="claude-opus-4-7")

tools = [
    stock_signal_tool,
    news_sentiment_tool,
    fundamentals_tool
]

multiagent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)

parser = PydanticOutputParser(pydantic_object=ResearchResponse)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use necessary tools. Use the save_text_to_file tool to save research data.
            Remove the word json from the output value.  
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())
tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can i help you with?")
raw_response = agent_executor.invoke({"query": query})
# print(raw_response)
try:
    structured_response = parser.parse(raw_response.get("output"))
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)

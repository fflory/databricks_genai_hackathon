import functools
import os
from typing import Any, Generator, Literal, Optional

import mlflow
from databricks.sdk import WorkspaceClient
from databricks_langchain import (
    ChatDatabricks,
    UCFunctionToolkit,
    DatabricksFunctionClient,
    set_uc_function_client
)
client = DatabricksFunctionClient()
set_uc_function_client(client) 
from databricks_langchain.genie import GenieAgent
from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from mlflow.langchain.chat_agent_langgraph import ChatAgentState
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import (
    ChatAgentChunk,
    ChatAgentMessage,
    ChatAgentResponse,
    ChatContext,
)
from pydantic import BaseModel

###################################################
## Create a GenieAgent with access to a Genie Space
###################################################

# TODO add GENIE_SPACE_ID and a description for this space
# You can find the ID in the URL of the genie room /genie/rooms/<GENIE_SPACE_ID>
# Example description: This Genie agent can answer questions based on a database containing tables related to enterprise software sales, including accounts, opportunities, opportunity history, fiscal periods, quotas, targets, teams, and users. Use Genie to fetch and analyze data from these tables by specifying the relevant columns and filters. Genie can execute SQL queries to provide precise data insights based on your questions.
GENIE_SPACE_ID = "01f098d550c5118ab93a29fcf099a33f"
genie_agent_description = """This agent is designed to analyze financial data across two related tables: balance_sheet and income_statement, both located in the databricks_genai_hackathon schema. These tables are linked by the columns TICKER (company identifier) and YEAR (financial year), enabling cross-table analysis for the same company and year. Use Genie to fetch and analyze data from these tables by specifying the relevant columns and filters. Genie can execute SQL queries to provide precise data insights based on your questions.

The balance_sheet table contains data on assets, liabilities, and equity.
The income_statement table provides information on income, expenses, and cash flow.
The agent can answer questions that require joining or comparing data across these tables, such as evaluating financial health, profitability, or year-over-year changes for a specific company."""

genie_agent = GenieAgent(
    genie_space_id=GENIE_SPACE_ID,
    genie_agent_name="Genie",
    description=genie_agent_description,
    client=WorkspaceClient(
        host=os.getenv("DB_MODEL_SERVING_HOST_URL"),
        token=os.getenv("DATABRICKS_GENIE_PAT"),
    ),
)


############################################
# Define your LLM endpoint and system prompt
############################################

# TODO: Replace with your model serving endpoint
# multi-agent Genie works best with claude 3.7 or gpt 4o models.
LLM_ENDPOINT_NAME = "databricks-claude-sonnet-4"
llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)


############################################################
# Create a code agent
# You can also create agents with access to additional tools
############################################################
tools = []

# TODO if desired, add additional tools and update the description of this agent
uc_tool_names = ["system.ai.*"]
uc_toolkit = UCFunctionToolkit(function_names=uc_tool_names)
tools.extend(uc_toolkit.tools)
code_agent_description = (
    "The Coder agent specializes in solving programming challenges, generating code snippets, debugging issues, and explaining complex coding concepts.",
)
code_agent = create_react_agent(llm, tools=tools)

#############################
# Define the supervisor agent
#############################

# TODO update the max number of iterations between supervisor and worker nodes
# before returning to the user
MAX_ITERATIONS = 3

worker_descriptions = {
    "Genie": genie_agent_description,
    "Coder": code_agent_description,
}

formatted_descriptions = "\n".join(
    f"- {name}: {desc}" for name, desc in worker_descriptions.items()
)

system_prompt = f"Decide between routing between the following workers or ending the conversation if an answer is provided. \n{formatted_descriptions}"
options = ["FINISH"] + list(worker_descriptions.keys())
FINISH = {"next_node": "FINISH"}

def supervisor_agent(state):
    count = state.get("iteration_count", 0) + 1
    if count > MAX_ITERATIONS:
        return FINISH
    
    class nextNode(BaseModel):
        next_node: Literal[tuple(options)]

    preprocessor = RunnableLambda(
        lambda state: [{"role": "system", "content": system_prompt}] + state["messages"]
    )
    supervisor_chain = preprocessor | llm.with_structured_output(nextNode)
    next_node = supervisor_chain.invoke(state).next_node
    
    # if routed back to the same node, exit the loop
    if state.get("next_node") == next_node:
        return FINISH
    return {
        "iteration_count": count,
        "next_node": next_node
    }

#######################################
# Define our multiagent graph structure
#######################################


def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {
        "messages": [
            {
                "role": "assistant",
                "content": result["messages"][-1].content,
                "name": name,
            }
        ]
    }


def final_answer(state):
    prompt = "Using only the content in the messages, respond to the previous user question using the answer given by the other assistant messages."
    preprocessor = RunnableLambda(
        lambda state: state["messages"] + [{"role": "user", "content": prompt}]
    )
    final_answer_chain = preprocessor | llm
    return {"messages": [final_answer_chain.invoke(state)]}


class AgentState(ChatAgentState):
    next_node: str
    iteration_count: int


code_node = functools.partial(agent_node, agent=code_agent, name="Coder")
genie_node = functools.partial(agent_node, agent=genie_agent, name="Genie")

workflow = StateGraph(AgentState)
workflow.add_node("Genie", genie_node)
workflow.add_node("Coder", code_node)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("final_answer", final_answer)

workflow.set_entry_point("supervisor")
# We want our workers to ALWAYS "report back" to the supervisor when done
for worker in worker_descriptions.keys():
    workflow.add_edge(worker, "supervisor")

# Let the supervisor decide which next node to go
workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next_node"],
    {**{k: k for k in worker_descriptions.keys()}, "FINISH": "final_answer"},
)
workflow.add_edge("final_answer", END)
multi_agent = workflow.compile()

###################################
# Wrap our multi-agent in ChatAgent
###################################


class LangGraphChatAgent(ChatAgent):
    def __init__(self, agent: CompiledStateGraph):
        self.agent = agent

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> ChatAgentResponse:
        request = {
            "messages": [m.model_dump_compat(exclude_none=True) for m in messages]
        }

        messages = []
        for event in self.agent.stream(request, stream_mode="updates"):
            for node_data in event.values():
                messages.extend(
                    ChatAgentMessage(**msg) for msg in node_data.get("messages", [])
                )
        return ChatAgentResponse(messages=messages)

    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> Generator[ChatAgentChunk, None, None]:
        request = {
            "messages": [m.model_dump_compat(exclude_none=True) for m in messages]
        }
        for event in self.agent.stream(request, stream_mode="updates"):
            for node_data in event.values():
                yield from (
                    ChatAgentChunk(**{"delta": msg})
                    for msg in node_data.get("messages", [])
                )


# Create the agent object, and specify it as the agent object to use when
# loading the agent back for inference via mlflow.models.set_model()
mlflow.langchain.autolog()
AGENT = LangGraphChatAgent(multi_agent)
mlflow.models.set_model(AGENT)

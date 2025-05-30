import functools
import os
from typing import Any, Generator, Literal, Optional

import mlflow
import uuid
from databricks.sdk import WorkspaceClient
from databricks_langchain import (
    ChatDatabricks,
    UCFunctionToolkit,
    VectorSearchRetrieverTool,
)
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

multi_agent_config = mlflow.models.ModelConfig(development_config="../configs/rag_genie_agent.yaml")


###################################################
## Create a GenieAgent with access to a Genie Space
###################################################

# TODO add GENIE_SPACE_ID and a description for this space
# You can find the ID in the URL of the genie room /genie/rooms/<GENIE_SPACE_ID>
GENIE_SPACE_ID = multi_agent_config.get("genie_agent_config").get("genie_space_id")
genie_agent_description = multi_agent_config.get("genie_agent_config").get("genie_agent_description")

genie_agent = GenieAgent(
    genie_space_id=GENIE_SPACE_ID,
    genie_agent_name="Genie",
    description=genie_agent_description,
    # DB_MODEL_SERVING_HOST_URL is set on an agent endpoints but doesn't exist in the notebook
    client=WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST") or os.getenv("DB_MODEL_SERVING_HOST_URL"),
        token=os.getenv("DATABRICKS_GENIE_PAT"),
    ),
)


############################################
# Define your LLM endpoint and system prompt
############################################

# TODO: Replace with your model serving endpoint, multi-agent Genie works best with GPT 4o and GPT o1 models.
LLM_ENDPOINT_NAME = multi_agent_config.get("databricks_resources").get("llm_endpoint_name")
llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)


############################################################
# Create a code agent
# You can also create agents with access to additional tools
############################################################
tools = []

# TODO if desired, add additional tools and update the description of this agent
# uc_tool_names = ["system.ai.*"]
# uc_toolkit = UCFunctionToolkit(function_names=uc_tool_names)
# tools.extend(uc_toolkit.tools)


# TODO: Add vector search indexes
index_name = multi_agent_config.get("retriever_config").get("vector_search_index")

vector_search_tools = [
        VectorSearchRetrieverTool(
        index_name=index_name,
        tool_description=multi_agent_config.get("retriever_config").get("tool_description")
        # filters="..."
        # query_type="ANN" # "HYBRID"
    )
]
tools.extend(vector_search_tools)


code_agent_description = multi_agent_config.get("retriever_config").get("tool_description")

code_agent = create_react_agent(llm, tools=tools)

#############################
# Define the supervisor agent
#############################

# TODO update the max number of iterations between supervisor and worker nodes
# before returning to the user
MAX_ITERATIONS = 5

worker_descriptions = {
    "Genie": genie_agent_description,
    "Retriever": code_agent_description,
}

formatted_descriptions = "\n".join(
    f"- {name}: {desc}" for name, desc in worker_descriptions.items()
)

system_prompt = multi_agent_config.get("multi_agent_config").get("system_prompt").format(
    formatted_descriptions=formatted_descriptions)

options = ["FINISH"] + list(worker_descriptions.keys())


def supervisor_agent(state):
    count = state.get("iteration_count", 0) + 1
    print('iteration count', count)
    if count > MAX_ITERATIONS:
        return {"next_node": "FINISH"}
    
    class nextNode(BaseModel):
        next_node: Literal[tuple(options)]

    preprocessor = RunnableLambda(
        lambda state: [{"role": "system", "content": system_prompt}] + state["messages"]
    )
    supervisor_chain = preprocessor | llm.with_structured_output(nextNode)
    next_node = supervisor_chain.invoke(state).next_node
    print(type(next_node), next_node)
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
    system_prompt = "Using only the content in the messages, respond to the user's question using the answer given by the other agents."
    preprocessor = RunnableLambda(
        lambda state: [{"role": "system", "content": system_prompt}] + state["messages"]
    )
    final_answer_chain = preprocessor | llm
    return {"messages": [final_answer_chain.invoke(state)]}


class AgentState(ChatAgentState):
    next_node: str
    iteration_count: int


code_node = functools.partial(agent_node, agent=code_agent, name="Retriever")
genie_node = functools.partial(agent_node, agent=genie_agent, name="Genie")

workflow = StateGraph(AgentState)
workflow.add_node("Genie", genie_node)
workflow.add_node("Retriever", code_node)
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
        request = {"messages": self._convert_messages_to_dict(messages)}
        response_id = str(uuid.uuid4())
        
        for event in self.agent.stream(request, stream_mode="messages"):
            # Event is a tuple: (AIMessageChunk, metadata)
            if isinstance(event, tuple) and len(event) >= 2:
                message_chunk, metadata = event[0], event[1]
                # Extract content from AIMessageChunk
                content = message_chunk.content
                idid = message_chunk.id
                # AIMessageChunk typically doesn’t have role in stream_mode="messages", default to "assistant"
                role = getattr(message_chunk, "role", "assistant") if hasattr(message_chunk, "role") else "assistant"
            else:
                print("Unexpected event format:", event)
                continue
            
            if not content:  # Skip empty chunks
                continue

            # response_id = str(uuid.uuid4())

            chunk = ChatAgentChunk(
                delta=ChatAgentMessage(
                        **{
                            "role": role,
                            "content": content,
                            "id": response_id,
                        }
                    )
            )
            yield chunk

# Create the agent object, and specify it as the agent object to use when
# loading the agent back for inference via mlflow.models.set_model()
mlflow.langchain.autolog()
AGENT = LangGraphChatAgent(multi_agent)
mlflow.models.set_model(AGENT)

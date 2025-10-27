from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.redis import RedisSaver  
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import getpass
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key is None:
    raise ValueError("API_KEY not found in environment variables")

#if "GOOGLE_API_KEY" not in os.environ:
#    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

model = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)

DB_URI = "redis://default:3SolwARPOGOCSqGRfNPwkHxJlo3DsXPq@redis-17541.c8.us-east-1-3.ec2.redns.redis-cloud.com:17541"
with RedisSaver.from_conn_string(DB_URI) as checkpointer:  
    checkpointer.setup()

    def call_model(state: MessagesState):
        response = model.invoke(state["messages"])
        return {"messages": response}

    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")

    graph = builder.compile(checkpointer=checkpointer)  

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "hi! I'm hania"}]},
        config,  
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()

    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "what's my name?"}]},
        config,  
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
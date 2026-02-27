import json
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import uuid
from src.ollama_deep_researcher.state import reportState
from src.ollama_deep_researcher.graph import graph
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Global structures
query_map = {}
query_lock = threading.Lock()
subquery_queue = Queue()

def load_prompt(key: str) -> str:
    prompt_path = Path(__file__).parent.parent.parent / "prompts" / f"{key}.md"
    return prompt_path.read_text(encoding="utf-8")

def split_query(user_query: str) -> list:
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that splits a user's compound query into independent subqueries and returns them as a flat JSON array."),
        ("human", load_prompt("query_split"))
    ])
    llm = ChatOllama(model="llama3.2", temperature=0.2)
    chain = prompt_template | llm
    response = chain.invoke({"user_query": user_query})

    content = response.content.strip()
    if content.startswith("```") and content.endswith("```"):
        content = "\n".join(content.split("\n")[1:-1]).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("❌ Could not parse JSON. Raw output:\n", response.content)
        return []

def process_subquery(query_id: str, subquery: str, callback=None):
    state = reportState(research_topic=subquery)
    config = RunnableConfig(configurable={
        "llm_provider": "ollama",
        "search_api": "google",
        "fetch_full_page": False
    })
    final_state = graph.invoke(state, config)
    result = final_state.get("running_report")

    with query_lock:
        query_map[query_id]["results"][json.dumps(subquery, sort_keys=True)] = result
        query_map[query_id]["remaining"] -= 1
        print(f"✅ Subquery done: {subquery} — Remaining: {query_map[query_id]['remaining']}")

        if callback:
            callback(query_id, subquery, result)

        if query_map[query_id]["remaining"] == 0:
            print(f"🎯 All subqueries complete for query: {query_id}")

def worker():
    while True:
        item = subquery_queue.get()
        if item is None:
            break
        query_id, subquery, callback = item
        process_subquery(query_id, subquery, callback)
        subquery_queue.task_done()

def run_batch_query(user_query: str, callback=None) -> dict:
    subqueries = split_query(user_query)
    if not subqueries:
        print("No valid queries extracted.")
        return {}

    query_id = str(uuid.uuid4())
    with query_lock:
        query_map[query_id] = {
            "query": user_query,
            "subqueries": subqueries,
            "remaining": len(subqueries),
            "results": {}
        }

    for subquery in subqueries:
        subquery_queue.put((query_id, subquery, callback))

    num_threads = min(4, len(subqueries))
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    subquery_queue.join()

    for _ in threads:
        subquery_queue.put(None)
    for t in threads:
        t.join()

    return query_map[query_id]["results"]
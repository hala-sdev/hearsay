from hearsay.pipeline import State, extract, verify_next_claim, route
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

calls = {"n": 0}

def flaky_verify(state):
    calls["n"] += 1                   
    if calls["n"] == 2:                 
        raise RuntimeError("simulated crash")  
    return verify_next_claim(state) 


builder = StateGraph(State)
builder.add_node("Extract", extract)
builder.add_node("Verify", flaky_verify)
builder.add_edge(START, "Extract")
builder.add_conditional_edges("Extract", route)
builder.add_conditional_edges("Verify", route)
graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":

    config = {
    "configurable": {"thread_id": "check-1"},
    "recursion_limit": 100,
    }
    
    starting = {"text": "Marie Curie was born in Warsaw in 1867. She won two Nobel Prizes.", "claims": [], "results": []}

    try:
            state = graph.invoke(starting, config)
    except RuntimeError as e:
        print("Crashed:", e)
    saved = graph.get_state(config)
    print("Saved:", len(saved.values["results"]), saved.next)

    state = graph.invoke(None, config)
    print("Results:", len(state["results"]))
    for r in state["results"]:
        print(r["claim"], "→", r["label"])
    print("Verify calls:", calls["n"])


from typing import TypedDict
from hearsay.extraction.extractor import extract_statements
from hearsay.verification.verifier import verify_claim
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from hearsay.extraction.checks import ungrounded_terms, leftover_pronouns, remove_duplicates

class State(TypedDict):
    text: str
    claims: list[str]
    results: list[dict]
    report: dict

def extract(state: State) -> dict:
    statements = extract_statements(state["text"])
    cleaned_stats = remove_duplicates(statements)
    return {"claims": cleaned_stats}


def verify_next_claim(state: State) -> dict:
    prev_results = state["results"]
    len_results = len(state["results"])
    current_claim = state["claims"][len_results]
    result = verify_claim(current_claim)
    result["warnings"] = {"ungrounded": ungrounded_terms(current_claim, state["text"]), "pronouns": leftover_pronouns(current_claim)}
    return {"results": prev_results + [result]}

def route(state: State) -> str:
    if len(state["claims"]) > len(state["results"]):
        return "Verify"
    else:
        return "Report"

def report(state: State) -> dict:
    error= 0
    not_enough_info = 0 
    support = 0 
    refute = 0
    for r in state["results"]:
        if r["label"] == "SUPPORTS":
            support+=1
        elif r["label"] == "NOT ENOUGH INFO":
            not_enough_info+=1

        elif r["label"] == "REFUTES":
            refute+=1

        elif r["label"] == "ERROR":
            error+=1
    return {"report": {"total": len(state["results"]), "SUPPORTS": support, "REFUTES": refute, "NOT ENOUGH INFO": not_enough_info, "ERROR": error }}

builder = StateGraph(State)
builder.add_node("Extract", extract)
builder.add_node("Verify", verify_next_claim)
builder.add_node("Report", report)
builder.add_edge(START, "Extract")
builder.add_conditional_edges("Extract", route)
builder.add_conditional_edges("Verify", route)
builder.add_edge("Report", END)

graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":

    fake = {"text": "", "claims": [], "results": [
       {"label": "SUPPORTS"}, {"label": "REFUTES"}, {"label": "SUPPORTS"}, {"label": "ERROR"}]}
    print(report(fake))

    config = {
    "configurable": {"thread_id": "check-1"},
    "recursion_limit": 100,
    }
    starting = {"text": "Marie Curie was born in Warsaw in 1867. She won two Nobel Prizes.", "claims": [], "results": []}
    state = graph.invoke(starting, config)
    print(state["report"])
    for r in state["results"]:
        print(r["claim"], "→", r["label"], r["warnings"])
    #print("Results: ", len(state["results"]))
    #for snapshot in graph.get_state_history(config):
     
     #   print(len(snapshot.values.get("results", [])), snapshot.next)



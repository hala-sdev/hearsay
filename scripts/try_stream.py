from hearsay.pipeline import builder
from hearsay.config import db_url
from langgraph.checkpoint.postgres import PostgresSaver
import uuid
from sqlalchemy.orm import Session
from hearsay.db.models import Check, Claim
from hearsay.db.session import engine

check_id = uuid.uuid4()
threat_id = str(check_id)
text = "Marie Curie was born in Warsaw in 1867. She won two Nobel Prizes."
with Session(engine) as session:
    check = Check(
        check_id=check_id,
        text=text,
    )
    session.add(check)
    session.commit()

with PostgresSaver.from_conn_string(db_url) as checkpointer:

    graph = builder.compile(checkpointer=checkpointer)
    
    config = {
    "configurable": {"thread_id": threat_id},
    "recursion_limit": 100,
    }
    starting = {"text": text, "claims": [], "results": []}
    for update in graph.stream(starting, config=config, stream_mode = "updates"):
        print(update)
        if "Verify" in update:
            result = update["Verify"]["results"]

            new_result = result[-1]
            index_result = len(result) - 1

            with Session(engine) as session:
                claim = Claim(
                    check_id=check_id,
                    claim_index=index_result,
                    claim=new_result["claim"],
                    label=new_result["label"],
                    reasoning=new_result["reasoning"],
                    cited=new_result.get("cited", []),
                    retried=new_result.get("retried", False),
                    first_pass=new_result.get("first_pass")["label"] if new_result.get("first_pass") else None,
                    warnings=new_result.get("warnings", {}),
                )
                session.add(claim)
                session.commit()


from hearsay.pipeline import builder
from hearsay.config import db_url
from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy.orm import Session
from hearsay.db.models import Check, Claim
from hearsay.db.session import engine
from sqlalchemy import select, update
import asyncio
new_check = asyncio.Event()
def run_check(check_id):
    with Session(engine) as session:
        check = session.get(Check, check_id)
        text = check.text

    try:
        with PostgresSaver.from_conn_string(db_url) as checkpointer:

            graph = builder.compile(checkpointer=checkpointer)
            
            config = {
            "configurable": {"thread_id": str(check_id)},
            "recursion_limit": 100,
            }
            starting = {"text": text, "claims": [], "results": []}
            state = graph.get_state(config)
            inputs = None if state.next else starting
            for step in graph.stream(inputs, config=config, stream_mode = "updates"):
                print(step)
                if "Verify" in step:
                    result = step["Verify"]["results"]

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

        with Session(engine) as session:
            check = session.get(Check, check_id)
            check.status = "done"
            session.commit()

    except Exception as e:
        with Session(engine) as session:
            check = session.get(Check, check_id)
            check.status = "error"
            check.error = str(e)
            print(check.error)
            session.commit()

def claim_next():
    with Session(engine) as session:
        qur = select(Check).where(Check.status == "queued").order_by(Check.created_at).limit(1).with_for_update(skip_locked=True)
        check = session.scalars(qur).first()

        if not check:
            return None
        else:
            check.status = "running"
            session.commit()
            return check.check_id


def requeue_stuck():
    with Session(engine) as session:
        session.execute(update(Check).where(Check.status == "running").values(status="queued"))
        session.commit()

async def worker_loop():
    while True:
        check_id = await asyncio.to_thread(claim_next)
        if check_id is None:
            try:
                await asyncio.wait_for(new_check.wait(), timeout=60)
            except TimeoutError:
                pass
            new_check.clear()
            continue
        await asyncio.to_thread(run_check, check_id)



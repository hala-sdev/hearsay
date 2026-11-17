from hearsay.pipeline import builder
from hearsay.config import db_url, max_attempts
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
                    results = step["Verify"]["results"]

                    new_result = results[-1]
                    index_result = len(results) - 1
                    save_claim(check_id, index_result, new_result)
                if "Extract" in step:
                    total_claim = len(step["Extract"]["claims"])
                    with Session(engine) as session:
                        check = session.get(Check, check_id)
                        check.total_claims = total_claim
                        session.commit()
            final_results = graph.get_state(config).values["results"]
            final_claims = graph.get_state(config).values["claims"]

            for index, result in enumerate(final_results):
                save_claim(check_id, index, result)

        with Session(engine) as session:
            check = session.get(Check, check_id)
            check.total_claims = len(final_claims)
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
            check.attempts +=1
            session.commit()
            return check.check_id

def save_claim(check_id, index, result):
    with Session(engine) as session:
        claim = Claim(
                    check_id=check_id,
                    claim_index=index,
                    claim=result["claim"],
                    label=result["label"],
                    reasoning=result["reasoning"],
                    cited=result.get("cited", []),
                    retried=result.get("retried", False),
                    first_pass=result.get("first_pass")["label"] if result.get("first_pass") else None,
                    warnings=result.get("warnings", {}),
                    )
        session.merge(claim)
        session.commit()


def requeue_stuck():
    with Session(engine) as session:

        session.execute(update(Check)
            .where(Check.status == "running", Check.attempts >= max_attempts)
            .values(status="error", error=f"Gave up after {max_attempts} attempts"))
        
        session.execute(update(Check)
            .where(Check.status == "running")
            .values(status="queued"))
        session.commit()

async def worker_loop():
    while True:
        try:
            check_id = await asyncio.to_thread(claim_next)
            if check_id is None:
                try:
                    await asyncio.wait_for(new_check.wait(), timeout=3600)
                except TimeoutError:
                    pass
                new_check.clear()
                continue
            await asyncio.to_thread(run_check, check_id)
        except Exception as e:
            print("worker error:", e)
            await asyncio.sleep(5)
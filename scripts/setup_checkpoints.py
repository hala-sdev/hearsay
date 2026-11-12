from langgraph.checkpoint.postgres import PostgresSaver
from hearsay.config import db_url

with PostgresSaver.from_conn_string(db_url) as checkpointer:
    checkpointer.setup()
    print("Checkpoints setup completed ")
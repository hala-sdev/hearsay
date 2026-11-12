import asyncio
import time

async def worker():
    for i in range(3):
        print(f"{time.strftime('%X')} worker: judging claim {i}")
        await asyncio.to_thread(time.sleep, 2)

async def api():
    for i in range(6):
        print(f"{time.strftime('%X')} api: answered GET #{i}")
        await asyncio.sleep(1)      # pretend: next request 1 s later

async def main():
    await asyncio.gather(worker(), api())   # run both at the same time

asyncio.run(main())
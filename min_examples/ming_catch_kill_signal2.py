
import signal
import asyncio

def main():
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    print ("before loop")
    asyncio.set_event_loop(loop)


    asyncio.run(asyncio.sleep(20))
    try:
        print("loop forever")
        asyncio.run(run())
    finally:
        loop.close()
        print("Successfully shutdown the Mayhem service.")

async def run():
    print("let's run")
    #await asyncio.gather(forever(),forever())
    await asyncio.sleep(20)

async def forever():
    print("forever")
    await asyncio.sleep(300)


async def shutdown(signal, loop):
    print ("gotcha")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks)
    loop.stop()


main()

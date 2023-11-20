
import signal
import asyncio

def main():
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    asyncio.set_event_loop(loop)

    try:
        print("loop forever")

        loop.run_until_complete(asyncio.gather(asyncio.sleep(20),
                                               asyncio.sleep(20)))
        #asyncio.run(asyncio.sleep(20))
    finally:
        loop.close()
        print("Successfully shutdown the Mayhem service.")



async def shutdown(signal, loop):
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks)
    loop.stop()


main()

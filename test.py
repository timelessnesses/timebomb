import asyncio

async def main():
    loop = asyncio.get_event_loop()
    async def test():
        await asyncio.sleep(2)
        print("slept for 2 seconds")
    loop.create_task(test()) # you shall NOT await this.
    print("printed!")
    await asyncio.sleep(5)

asyncio.run(main())
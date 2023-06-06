import asyncio
import sys

from loguru import logger
from loguru._defaults import LOGURU_FORMAT
import requests

def setup_loguru():
    LOG_FORMAT = LOGURU_FORMAT + " | <g><d>{extra}</d></g>"
    logger.remove()
    logger.add(sink=sys.stderr, format=LOG_FORMAT, colorize=True)


async def async_web_request(url):
    """ Run a synchronous web request in a task, making it async.
    Example:
    ```
    async def main():
        url = 'https://example.com'

        # Start the web request in the background
        request_task = asyncio.create_task(async_web_request(url))

        # Perform other tasks in the meantime
        print("Doing other work...")

        # Wait for the web request to complete
        response = await request_task

        # Process the response
        print(response)

    asyncio.run(main())
    ```
    """
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, url)
    return response.text

import asyncio
from ws_thread import WsThread
from mq_thread import MqThread

main_loop = asyncio.get_event_loop()

if __name__ == '__main__':

    ws_thread = WsThread(main_loop)
    ws_thread.start()

    mq_thread = MqThread(main_loop)
    mq_thread.start()

    main_loop.run_forever()

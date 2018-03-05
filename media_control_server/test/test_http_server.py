
# pip install aiohttp
from aiohttp import web

DEVICE_ID = 0


async def getID(request):
    global DEVICE_ID
    DEVICE_ID += 1
    return web.Response(text=str(DEVICE_ID))


def setup_routers(app):
    app.router.add_get('/getID', getID)


if __name__ == '__main__':
    app = web.Application()
    setup_routers(app)
    web.run_app(app, host='127.0.0.1', port=8080)


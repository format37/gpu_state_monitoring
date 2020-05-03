#!/usr/bin/env python3
import GPUtil
import asyncio
from aiohttp import web

async def get_gpu_state(request):
	temps=[]
	for gpu in GPUtil.getGPUs():
		temps.append(float(gpu.temperature))
	return web.Response(text=str(max(temps)),content_type="text/html")

app = web.Application()
app.router.add_route('GET', '/gpustate', get_gpu_state)

loop = asyncio.get_event_loop()
handler = app.make_handler()
f = loop.create_server(handler, port='8080')
srv = loop.run_until_complete(f)

print('serving on', srv.sockets[0].getsockname())
try:
	loop.run_forever()
except KeyboardInterrupt:
	print("serving off...")
finally:
	loop.run_until_complete(handler.finish_connections(1.0))
	srv.close()
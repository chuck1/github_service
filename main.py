import asyncio
import argparse
import json
from pprint import pprint

import requests
import aiohttp.web

def hex_color(r, g, b):
    r, g, b = int(r), int(g), int(b)
    v = r * 256**2 + g * 256 + b

    return hex(v)

def map_range(x, x0, x1, y0, y1):
    i = (x-x0)/(x1-x0)
    return y0 * (1-i) + y1 * i

def color_scale(i):

    return hex_color(func_red(i), func_green(i), 0)

def func_red(i):
    r = 200
    return min(r, 2 * r * (1 - i))

def func_green(i):
    g = 200
    return min(g, 2 * g * i)

async def what_lines(user, repo, branch):
    url = 'https://codecov.io/api/gh/{}/{}/branch/{}'.format(user, repo, branch)

    r = requests.get(url)
    
    d = r.json()
    d = d['commit']
    
    lines = d['totals']['n']
    hit = d['totals']['h']
    
    i = map_range(hit/lines, 0.7, 1.0, 0, 1)
    print('i',i)

    hc = color_scale(i)
    
    text = json.dumps(d, indent=8) + '\n' + hc

    pprint(text)

    url = 'https://img.shields.io/badge/{}-{}%2F{}-{}.svg'.format('lines', hit, lines, hc[2:])

    return aiohttp.web.HTTPFound(url)

async def handle(request):
    user = request.match_info.get('user')
    repo = request.match_info.get('repo')
    branch = request.match_info.get('branch')
    what = request.match_info.get('what')
    
    print('user  ',user)
    print('repo  ',repo)
    print('branch',branch)
    print('what  ',what)

    text = "You are asking for user={} repo={} branch={} what={}".format(
            user, repo, branch, what)

    if what == 'lines':
        return await what_lines(user, repo, branch)

async def create_app(loop, args):

    app = aiohttp.web.Application()
    
    app.router.add_get('/{user}/{repo}/{branch}/{what}/', handle)

    return app

async def runserver(loop, args):
    
    app = await create_app(loop, args)

    future = loop.create_future()

    async with aiohttp.web.run_app_context(app, loop=loop) as web:
        await future

#############################################

parser = argparse.ArgumentParser()

args = parser.parse_args()

loop = asyncio.get_event_loop()

loop.run_until_complete(runserver(loop, vars(args)))

loop.close()


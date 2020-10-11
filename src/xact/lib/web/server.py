# -*- coding: utf-8 -*-
"""
Simple ASGI server component.

Based on starlette and uvicorn.

"""


import asyncio
import collections
import copy
import multiprocessing
import queue
import time
import uuid

import dill
import loguru
import sse_starlette.sse
import starlette.applications
import starlette.background
import starlette.exceptions
import starlette.middleware
import starlette.middleware.sessions
import starlette.responses
import starlette.routing
import starlette.websockets
import uvicorn


#------------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Start the ASGI server and connect it to the xact network.``

    """
    if 'interactions' in outputs:
        outputs['interactions'].clear()
        outputs['interactions']['ena']  = False
        outputs['interactions']['list'] = list()

    if 'analytics' in outputs:
        outputs['analytics'].clear()
        outputs['analytics']['ena']  = False
        outputs['analytics']['list'] = list()

    map_queues = dict(
        queue_resources    = multiprocessing.Queue(),  # From xact to client
        queue_interactions = multiprocessing.Queue(),  # From client to xact
        queue_analytics    = multiprocessing.Queue()   # From client to xact
    )
    for (key, value) in map_queues.items():
        state[key] = value

    state['process_server'] = multiprocessing.Process(
                                                target = _asgi_server_process,
                                                args   = (cfg, map_queues),
                                                name   = 'xact-asgi-server',
                                                daemon = True)
    state['process_server'].start()


#------------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Update the ASGI server and pass on any new interactions and analytics.

    """
    if 'time' in inputs and inputs['time']['ena']:
        gmtime = inputs['time']['gmtime']
        ts     = inputs['time']['ts']
    else:
        gmtime = None
        ts     = None

    # Updated resources from xact-backend to ASGI-server.
    for (key, val) in inputs.items():
        if key.startswith('resources'):
            if inputs[key]['ena']:
                try:
                    state['queue_resources'].put(inputs[key], block = False)
                except queue.Full:
                    pass # TODO: LOG SOME SORT OF ERROR?

    # User interactions from ASGI-server to xact-backend.
    if 'interactions' in outputs:
        outputs['interactions']['ena'] = False
        outputs['interactions']['list'].clear()
    while True:
        try:
            interaction = state['queue_interactions'].get(block = False)
            if 'interactions' in outputs:
                outputs['interactions']['ena']    = True
                outputs['interactions']['ts']     = ts
                outputs['interactions']['gmtime'] = gmtime
                outputs['interactions']['list'].append(interaction)
        except queue.Empty:
            break

    # Analytics from ASGI-server to xact-backend.
    if 'analytics' in outputs:
        outputs['analytics']['ena'] = False
        outputs['analytics']['list'].clear()
    while True:
        try:
            analytics_item = state['queue_analytics'].get(block = False)
            if 'analytics' in outputs:
                outputs['analytics']['ena']    = True
                outputs['analytics']['ts']     = ts
                outputs['analytics']['gmtime'] = gmtime
                outputs['analytics']['list'].append(analytics_item)
        except queue.Empty:
            break


#------------------------------------------------------------------------------
def _asgi_server_process(cfg, map_queues):
    """
    Run the ASGI server process. (Runs until killed by a signal)

    """

    #--------------------------------------------------------------------------
    async def get_resource(request = None):
        """
        Return a response for the specified id_resource param.

        """
        _update_and_notify()
        tasks = starlette.background.BackgroundTasks()
        tasks.add_task(_update_and_notify_task)

        if request is None:
            id_resource = 'default'
            # print('NEW UID AND SID')
            # id_user     = uuid.uuid4()
            # id_session  = uuid.uuid4()
        else:
            id_resource = request.path_params.get(
                                    'id_resource', request.url.path.strip('/'))
            map_cookie  = getattr(request, 'cookies', dict())
            id_user     = map_cookie.get('xw_uid', uuid.uuid4())
            id_session  = map_cookie.get('xw_sid', uuid.uuid4())
            # print('OLD? UID AND SID')
            # print(id_user)
            # print(id_session)
            # print(map_cookie)
            # print(request.cookies)

        (media_type, content) = _lookup_resource(id_resource)
        if media_type == 'callable':
            (media_type, content) = dill.loads(content)(request)

        if request is not None:
            _enqueue_interactions(request.query_params)
            _enqueue_analytics(request, id_user, id_session)

        response = starlette.responses.Response(media_type = media_type,
                                                content    = content,
                                                background = tasks)
        response.set_cookie('xw_uid', id_user,
                            max_age  = 32000000, # About a year.
                            secure   = False,    # TODO: FIX HTTPS
                            httponly = True,
                            samesite = 'strict')
        response.set_cookie('xw_sid', id_session,
                            max_age  = 43000,   # About 12 hours
                            secure   = False,   # TODO: FIX HTTPS
                            httponly = True,
                            samesite = 'strict')
        return response



    #--------------------------------------------------------------------------
    async def _update_and_notify_task():
        """
        Continually update resource table and notify listeners of changes.

        """
        staleout = 2.0  # seconds
        is_stale = time.time() > (app.state.ts_last_update + staleout)
        if not is_stale:
            return

        while True:
            await asyncio.sleep(0.1)
            app.state.ts_last_update = time.time()
            _update_and_notify()

    #--------------------------------------------------------------------------
    def _update_and_notify():
        """
        Update resource table and notify listeners of changes.

        """
        set_id_resource_changed  = _update_resource_table()
        _notify_change_listeners(set_id_resource_changed)

    #--------------------------------------------------------------------------
    def _update_resource_table():
        """
        Bring the resource table up to date with the latest changes from XACT.

        """
        set_id_resource_changed = set()
        while True:
            try:
                resource_update = app.state.queue_resources.get(block = False)
                app.state.map_resources.update(resource_update)
            except queue.Empty:
                break
            set_id_resource_changed |= set(resource_update.keys())

        if 'default' in set_id_resource_changed:
            app.state.default = resource_update['default']

        return set_id_resource_changed

    #--------------------------------------------------------------------------
    def _notify_change_listeners(set_id_resource_changed):
        """
        Distribute change notifications to all SSE event source queues.

        """
        for id_resource in set_id_resource_changed:
            list_queue_notify = app.state.map_queue_notify[id_resource]
            for queue_notify in list_queue_notify:
                queue_notify.put_nowait({
                    'event': id_resource,
                    'data': 'updated'})

    #--------------------------------------------------------------------------
    def _lookup_resource(id_resource):
        """
        Return the resource corresponding to the specified id_resource.

        """
        if id_resource == 'ena':
            if app.state.default is not None:
                return app.state.default
            else:
                raise starlette.exceptions.HTTPException(
                                            status_code = 204)  # No content
        try:
            return app.state.map_resources[id_resource]
        except KeyError:
            if app.state.default is not None:
                return app.state.default
            else:
                raise starlette.exceptions.HTTPException(
                                            status_code = 204)  # No content

    #--------------------------------------------------------------------------
    def _enqueue_interactions(query_params):
        """
        Enqueue urlencoded user interactions for xact.

        """
        dict_params = dict()
        for key in query_params.keys():
            dict_params[key] = query_params.getlist(key)

        if dict_params:
            try:
                app.state.queue_interactions.put(dict_params, block = False)
            except queue.Full:
                pass # TODO: LOGGING

    #--------------------------------------------------------------------------
    def _enqueue_analytics(request, id_user, id_session):
        """
        Enqueue analytics data.

        """
        headers   = dict(request.headers)
        analytics = dict(id_user         = str(id_user),
                         id_session      = str(id_session),
                         client_ip       = request['client'][0],
                         url             = str(request.url),
                         accept          = headers['accept'],
                         accept_encoding = headers['accept-encoding'],
                         accept_language = headers['accept-language'],
                         user_agent      = headers['user-agent'])

        try:
            app.state.queue_analytics.put(analytics, block = False)
        except queue.Full:
            pass # TODO: LOGGING

    #--------------------------------------------------------------------------
    async def subscribe_sse_notify(request):
        """
        Return sse event source for notifications of changes to id_resource.

        """
        id_resource  = request.path_params['id_resource']
        queue_notify = asyncio.Queue()
        app.state.map_queue_notify[id_resource].append(queue_notify)
        return sse_starlette.sse.EventSourceResponse(
                        _generate_change_notifications(request, queue_notify))

    #--------------------------------------------------------------------------
    async def _generate_change_notifications(request, queue_notify):
        """
        Yield items from the specified change notification queue.

        Until request is disconnected.

        """
        while True:

            if (await request.is_disconnected()):
                # print('DISCONNECT')
                break

            try:
                item = queue_notify.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.001)
                continue
            yield item

    #--------------------------------------------------------------------------
    async def handle_websocket(websocket):
        """
        Handle websocket communications with the specified id_resource param.

        !!! WORK IN PROGRESS !!!

        """
        print('WEBSOCKET!')

        # id_resource = websocket.path_params['id_resource']
        # (media_type, handler) = _lookup_resource(id_resource)

        # if media_type != 'callable':
        #     raise starlette.exceptions.HTTPException(status_code = 404)

        await websocket.accept()
        print('WSS ACCEPTED')

        # while True:
        #     await websocket.send_text(handler(await websocket.receive_text()))

        await websocket.close()
        print('WSS CLOSED')

    Middleware        = starlette.middleware.Middleware
    SessionMiddleware = starlette.middleware.sessions.SessionMiddleware
    list_middleware   = [Middleware(SessionMiddleware,
                                    secret_key = cfg['session_key'])]
    route             = starlette.routing.Route
    list_routes       = [route('/req/{id_resource}', get_resource),
                         route('/sub/{id_resource}', subscribe_sse_notify),
                         route('/wss/{id_resource}', handle_websocket),
                         route('/{id_resource}',     get_resource),
                         route('/',                  get_resource)]
    exceptions        = { 404: get_resource,
                          500: get_resource }

    app = starlette.applications.Starlette(debug              = True,
                                           routes             = list_routes,
                                           exception_handlers = exceptions,
                                           middleware         = list_middleware)

    app.state.map_queue_notify = collections.defaultdict(list)
    app.state.map_resources    = dict()
    for (key, value) in map_queues.items():
        setattr(app.state, key, value)
    app.state.ts_last_update = 0.0
    app.state.default        = None

    uvicorn.run(app, host = cfg['host'],
                     port = cfg['port'],
                     debug = True)



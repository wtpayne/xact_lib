# -*- coding: utf-8 -*-
"""
Xact component for web UI layout.

"""


import base64
import datetime
import json
import string
import time
import uuid

import psutil

import xact.lib.ui.web.markup.html as html
import xact.lib.ui.web.markup.svg as svg
import xact.lib.ui.web.util
import xact.lib.web.util
import xact.util


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the xact component.

    """
    state['history_secs']   = 120
    state['id_data']        = 'cpudata'
    state['id_tag']         = 'datastream_cpu'


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the xact component.

    """
    xact.util.clear_outputs(
                    outputs             = outputs,
                    list_name_output    = ('id_ui', 'id_subs', 'resources'),
                    list_field_to_clear = ('list', ))

    if not inputs['clock']['ena']:
        return

    ts           = inputs['clock']['ts']
    microseconds = int(1000000 * (ts % 1))
    tup_time     = (*inputs['clock']['gmtime'][:6], microseconds)
    timestamp    = datetime.datetime(*tup_time).isoformat()

    vega_lite_spec = {
        'autosize': {'resize': True},
        'data':     {'name':   state['id_data']},
        'mark':     'bar',
        'encoding': {'x': {'field':     'iso_time',
                           'type':      'temporal',
                           'timeunit':  'utcminutes'},
                     'y': {'field':     'cpu',
                           'type':      'quantitative',
                           'aggregate': 'max',
                           'scale':     {'domain': [0, 100]}}}}


    cpu          = psutil.cpu_percent()
    map_res      = xact.lib.web.util.ResMap()
    id_res_data  = 'datastream_cpu'
    map_res.js(datastream_cpu = json.dumps({'ts':       ts,
                                            'iso_time': timestamp,
                                            'cpu':      cpu}))

    datacard = html.div(
        id               = id_res_data,
        data_xact        = vega_lite_timeseries(
                                    vega_lite_spec = vega_lite_spec,
                                    id_data        = state['id_data'],
                                    id_tag         = state['id_tag'],
                                    history_secs   = state['history_secs']),
        data_hx_trigger  = 'sse:{id}'.format(id = id_res_data),
        data_hx_sse      = 'listen:{id}'.format(id = id_res_data),
        _class           = ('shadow-xl',
                            'rounded-3xl',
                            'bg-white',
                            'text-gray-900',
                            'hover:bg-gray-100',
                            'hover:text-black',
                            'p-5'))
    map_res.htm(datacard = datacard)

    # Resource IDs for parent UI component to load.
    outputs['id_ui']['ena']  = True
    outputs['id_ui']['list'] = ['datacard']

    # Resource IDs for the page to subscribe to.
    outputs['id_subs']['ena']  = True
    outputs['id_subs']['list'] = ['datacard', 'datastream_cpu']

    # Resources to publish.
    outputs['resources']['ena']  = True
    outputs['resources']['list'] = [dict(map_res)]


# -----------------------------------------------------------------------------
def vega_lite_timeseries(vega_lite_spec, id_data, id_tag, history_secs):
    """
    """
    return string.Template("""
    (function() {

        var xact_node = {
            reset: reset,
            step:  step,
            state: {},
        };

        function reset(name_evt_tgt) {
            this.state.view = new vega.View(
                    vega.parse(vegaLite.compile(${vega_lite_spec}).spec))
                        .renderer('svg')
                        .initialize(document.querySelector('#${id_tag}'))
                        .run();
        }

        function step(evt) {
            var item = JSON.parse(evt.detail.data);
            var ts_min = item.ts - ${history_secs};
            var changes = vega.changeset()
                            .insert(item)
                            .remove(function(it) {return it.ts < ts_min;});
            window.xact[evt.type].state.view.change(
                                                '${id_data}', changes).run();
        }

        return xact_node;

    }())""").substitute(id_tag         = id_tag,
                        id_data        = id_data,
                        vega_lite_spec = json.dumps(vega_lite_spec),
                        history_secs   = str(history_secs))
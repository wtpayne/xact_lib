# -*- coding: utf-8 -*-
"""
Functional specification for xact tee.

"""


import socket

import xact.cfg.validate
import xact.lib.test.component


# =============================================================================
class SpecifyUnreliablecomms:
    """
    Spec for the unreliablecomms simulation component.

    """

    #--------------------------------------------------------------------------
    def it_can_do_a_lossless_round_trip(self):
        """
        Round trip test for the unreliablecomms simulation component.

        """
        cfg = xact.lib.test.component.chain_test(
                list_pipeline_modules = [
                        'xact.lib.util.packer',
                        'xact.lib.encryption.obfuscator',
                        'xact.lib.comms.sockettx',
                        'xact.lib.simulation.unreliablecomms',
                        'xact.lib.comms.socketrx',
                        'xact.lib.encryption.deobfuscator',
                        'xact.lib.util.unpacker'],
                list_pipeline_node_config = [
                        {'fields': ('foo', 'bar'),        # packer
                         'format': 'BB'},
                        {'key':    'ik4ofdebn478dxhb'},   # obfuscator
                        {'test':   True,                  # sockettx
                         'family': int(socket.AF_INET),
                         'type':   int(socket.SOCK_DGRAM),
                         'ip':     '<broadcast>',
                         'port':   1234},
                        {},                                # tx medium
                        {'test':   True,                   # sockettx
                         'family': int(socket.AF_INET),
                         'type':   int(socket.SOCK_DGRAM),
                         'ip':     '1.2.3.4',
                         'port':   1234},
                        {'key':    'ik4ofdebn478dxhb'},   # deobfuscator
                        {'fields': ('foo', 'bar'),        # unpacker
                         'format': 'BB'}],
                list_pipeline_edge_info = [
                        [('packed', 'data',   'python_dict')],  # packer->obfuscator
                        [('data',   'data',   'python_dict')],  # obfuscator->sockettx
                        [('data',   'data',   'python_dict')],  # sockettx->unreliablecomms
                        [('data',   'data',   'python_dict')],  # unreliablecomms->socketrx
                        [('data',   'data',   'python_dict')],  # socketrx->deobfuscator
                        [('data',   'packed', 'python_dict')]], # deobfuscator->unpacker
                list_test_vectors = [
                        {'path':   ['data',  'values'],
                         'signal': [{'foo': 0,   'bar': 0},
                                    {'foo': 255, 'bar': 255}]}],
                list_expected_outputs = [
                        {'path':   ['data', 'values'],
                         'signal': [{'foo':   0, 'bar':   0},
                                    {'foo': 255, 'bar': 255}]}])
        xact.cfg.validate.normalized(cfg)  # Sanity check
        xact.cli.util.run_test(cfg)
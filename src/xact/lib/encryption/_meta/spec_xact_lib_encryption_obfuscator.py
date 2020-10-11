# -*- coding: utf-8 -*-
"""
Functional specification for xact tee.

"""


import xact.lib.test.component
import xact.cli.util


# =============================================================================
class SpecifyObfuscator:
    """
    Spec for obfuscator module.

    """

    #--------------------------------------------------------------------------
    def it_can_do_a_lossless_round_trip(self):
        """
        Round trip test for the obfuscator component.

        """
        cfg = xact.lib.test.component.chain_test(
                list_pipeline_modules = [
                        'xact.lib.util.packer',
                        'xact.lib.encryption.obfuscator',
                        'xact.lib.encryption.deobfuscator',
                        'xact.lib.util.unpacker'],
                list_pipeline_node_config = [
                        {'fields': ('foo', 'bar'), 'format': 'BB'},
                        {'key':    'ik4ofdebn478dxhb'},
                        {'key':    'ik4ofdebn478dxhb'},
                        {'fields': ('foo', 'bar'), 'format': 'BB'}],
                list_pipeline_edge_info = [
                        [('packed', 'data',   'python_dict')],
                        [('data',   'data',   'python_dict')],
                        [('data',   'packed', 'python_dict')]],
                list_test_vectors = [
                        {'path':   ['data',  'values'],
                         'signal': [{'foo': 0,   'bar': 0},
                                    {'foo': 255, 'bar': 255}]}],
                list_expected_outputs = [
                        {'path':   ['data', 'values'],
                         'signal': [{'foo':   0, 'bar':   0},
                                    {'foo': 255, 'bar': 255}]}])

        xact.cli.util.run_test(cfg,
                               expected_exit_code = 0,
                               do_expect_stdout   = False,
                               do_expect_stderr   = False)
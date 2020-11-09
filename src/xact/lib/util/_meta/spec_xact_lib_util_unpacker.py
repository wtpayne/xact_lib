# -*- coding: utf-8 -*-
"""
Functional specification for the xact data unpacker component.

"""


import xact.lib.test.component


# =============================================================================
class SpecifyUnpacker:
    """
    Spec for unpacker module.

    """
    #--------------------------------------------------------------------------
    def it_unpacks_data(self):
        """
        Test that the packer component packs data.

        """
        cfg = xact.lib.test.component.pipeline_test(
                list_pipeline_modules = [
                        'xact.lib.util.unpacker'],
                list_pipeline_node_config = [
                        {'fields': ('foo', 'bar'), 'format': 'BB'}],
                list_test_vectors = [
                        {'path':   ['packed',  'buffer'],
                         'signal': [b'\x00\x00',
                                    b'\xFF\xFF']}],
                list_expected_outputs = [
                        {'path':   ['data', 'values'],
                         'signal': [{'foo':   0, 'bar':   0},
                                    {'foo': 255, 'bar': 255}]}])
        xact.cli.util.run_test(cfg)

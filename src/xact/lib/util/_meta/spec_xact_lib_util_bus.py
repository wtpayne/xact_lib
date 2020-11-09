# -*- coding: utf-8 -*-
"""
Functional specification for xact bus component.

"""


import xact.lib.test.component


# =============================================================================
class SpecifyBus:
    """
    Spec for bus component.

    """
    #--------------------------------------------------------------------------
    def it_buses_data(self):
        """
        Test that the bus component buses data.

        """
        cfg = xact.lib.test.component.pipeline_test(
                list_pipeline_modules = [
                        'xact.lib.util.bus'],
                list_pipeline_node_config = [
                        None],
                list_test_vectors = [
                        {'path':   ['in1'],
                         'signal': [{'it': 1},
                                    {'it': 2},
                                    {'it': 3},
                                    {'it': 4}]},
                        {'path':   ['in2'],
                         'signal': [{'it': 5},
                                    {'it': 6},
                                    {'it': 7},
                                    {'it': 8}]}],
                list_expected_outputs = [
                        {'path':   ['bus'],
                         'signal': [{ 'in1': {'it': 1}, 'in2': {'it': 5}},
                                    { 'in1': {'it': 2}, 'in2': {'it': 6}},
                                    { 'in1': {'it': 3}, 'in2': {'it': 7}},
                                    { 'in1': {'it': 4}, 'in2': {'it': 8}}]}])
        xact.cli.util.run_test(cfg)


    #--------------------------------------------------------------------------
    def it_can_roundtrip_with_debus(self):
        """
        Round trip test for the bus component.

        """
        cfg = xact.lib.test.component.pipeline_test(
                list_pipeline_modules = [
                        'xact.lib.util.bus',
                        'xact.lib.util.debus'],
                list_pipeline_node_config = [
                        None,
                        None],
                list_pipeline_edge_info = [
                        [('bus', 'bus', 'python_dict')]],
                list_test_vectors = [
                        {'path':   ['in1'],
                         'signal': [{'it': 1},
                                    {'it': 2},
                                    {'it': 3},
                                    {'it': 4}]},
                        {'path':   ['in2'],
                         'signal': [{'it': 5},
                                    {'it': 6},
                                    {'it': 7},
                                    {'it': 8}]}],
                list_expected_outputs = [
                        {'path':   ['in1'],
                         'signal': [{'it': 1},
                                    {'it': 2},
                                    {'it': 3},
                                    {'it': 4}]},
                        {'path':   ['in2'],
                         'signal': [{'it': 5},
                                    {'it': 6},
                                    {'it': 7},
                                    {'it': 8}]}])
        xact.cli.util.run_test(cfg)

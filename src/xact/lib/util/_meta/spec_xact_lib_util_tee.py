# -*- coding: utf-8 -*-
"""
Functional specification for xact tee.

"""


import xact.lib.test.component


# =============================================================================
class SpecifyTee:
    """
    Spec for tee module.

    """
    #--------------------------------------------------------------------------
    def it_duplicates_outputs(self):
        """
        Test that the tee component duplicates outputs.

        """
        cfg = xact.lib.test.component.pipeline_test(
                list_pipeline_modules = [
                        'xact.lib.util.tee'],
                list_id_node_nocontrol = [
                        'pipeline_node_000'],
                list_pipeline_node_config = [{}],
                list_test_vectors = [
                        {'path':   ['signal', 'values'],
                         'signal': [0, 10, 20, 30, 40, 50]}],
                list_expected_outputs = [
                        {'path':   ['first_copy',  'values'],
                         'signal': [0, 10, 20, 30, 40, 50]},
                        {'path':   ['second_copy',  'values'],
                         'signal': [0, 10, 20, 30, 40, 50]}])
        xact.cli.util.run_test(cfg)

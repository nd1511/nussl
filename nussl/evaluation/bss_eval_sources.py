#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import numpy as np
import mir_eval

import bss_eval_base


class BSSEvalSources(bss_eval_base.BSSEvalBase):
    """

    """

    def __init__(self, true_sources_list, estimated_sources_list, source_labels=None, algorithm_name=None,
                 do_mono=False, compute_permutation=True):
        super(BSSEvalSources, self).__init__(true_sources_list=true_sources_list,
                                             estimated_sources_list=estimated_sources_list,
                                             source_labels=source_labels, do_mono=do_mono,
                                             compute_permutation=compute_permutation)

        self.mir_eval_func = mir_eval.separation.bss_eval_sources


    def _preprocess_sources(self):
        reference, estimated = super(BSSEvalSources, self)._preprocess_sources()

        # TODO: Check this - not sure what's going on...
        if self.num_channels != 1:
            reference = np.sum(reference, axis=-1)
            estimated = np.sum(estimated, axis=-1)

        mir_eval.separation.validate(reference, estimated)

        return reference, estimated


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class the will run your source separation algorithm on a number of files then evaluate using a  

"""

import warnings

import nussl.utils
import nussl.separation
import evaluation_base
from precision_recall_fscore import PrecisionRecallFScore
from nussl.separation.ideal_mask import IdealMask


def run_and_evaluate(evaluation_object, evaluation_kwargs,
                     separation_object, separation_kwargs,
                     mixture_list, true_sources_list_of_lists):
    """
    
    Args:
        evaluation_object: (EvaluationBase-derived object)
        evaluation_kwargs: (dict)
        separation_object: (SeparationBase-derived object)
        separation_kwargs: (dict)
        mixture_list: 
        true_sources_list_of_lists: 

    Returns:

    """

    mixture_list = nussl.utils._verify_audio_signal_list_lax(mixture_list)
    assert issubclass(separation_object, nussl.separation.SeparationBase), 'Expected a SeparationBase derived class!'
    assert issubclass(evaluation_object, evaluation_base.EvaluationBase), 'Expected an EvaluationBase derived class!'

    # is_prf = issubclass(evaluation_object, nussl.PrecisionRecallFScore)

    scores = {}
    for i, mixture in enumerate(mixture_list):

        true_sources_list = nussl.utils._verify_audio_signal_list_strict(true_sources_list_of_lists[i])

        assert mixture.signal_length == true_sources_list[0].signal_length, \
            'Mixture signal_length does not match true sources at idx {}'.format(i)

        assert mixture.num_channels == true_sources_list[0].num_channels, \
            'Mixture num_channels does not match true sources at idx {}'.format(i)

        sep = separation_object(input_audio_signal=mixture, *separation_kwargs)
        sep.run()
        est_sources = sep.make_audio_signals()

        eval_ = evaluation_object(true_sources_list=true_sources_list, estimated_sources_list=est_sources)
        cur_score = eval_.evaluate()
        scores[mixture.file_name] = cur_score

    return scores


def run_and_eval_prf(separation_list, separation_kwargs,
                     mixture_list, true_sources_list_of_lists,
                     skip_errors=False, name_list=None):
    """
    This is a helper method to run a :ref:`MaskSeparationBase`-derived source separation algorithm on a list of 
    mixtures (provided in `mixture_list`)
    Run and evaluate :ref:`PrecisionRecallFScore` for each 
    Args:
        separation_list: 
        separation_kwargs: 
        mixture_list: (list) List of :ref:`AudioSignal` objects that contain mixtures.
        true_sources_list_of_lists: (list) List of lists of AudioSignal objects that contain true sources
        skip_errors: (bool) 
        name_list: (list) 

    Returns:

    """
    mixture_list = nussl.utils._verify_audio_signal_list_lax(mixture_list)
    separation_list = nussl.utils._verify_mask_separation_list(separation_list)

    scores = {}
    for separation_object in separation_list:
        for i, mixture in enumerate(mixture_list):

            true_sources_list = nussl.utils._verify_audio_signal_list_strict(true_sources_list_of_lists[i])

            if mixture.signal_length != true_sources_list[0].signal_length:
                error = 'Mixture signal_length does not match true sources at idx {}'.format(i)
                if skip_errors:
                    warnings.warn(error)
                    continue
                else:
                    raise RuntimeError(error)

            if mixture.num_channels != true_sources_list[0].num_channels:
                error = 'Mixture num_channels does not match true sources at idx {}'.format(i)
                if skip_errors:
                    warnings.warn(error)
                    continue
                else:
                    raise RuntimeError(error)

            # Setup and run the user provided algorithm
            sep = separation_object(input_audio_signal=mixture, mask_type=nussl.MaskSeparationBase.BINARY_MASK,
                                    *separation_kwargs)

            est_mask_list = sep.run()

            # Setup and run the ideal mask
            ideal_mask_sep = IdealMask(input_audio_mixture=mixture, sources_list=true_sources_list,
                                       mask_type=nussl.MaskSeparationBase.BINARY_MASK)

            ideal_mask_list = ideal_mask_sep.run()

            prf = PrecisionRecallFScore(true_sources_mask_list=ideal_mask_list,
                                        estimated_sources_mask_list=est_mask_list)
            cur_score = prf.evaluate()

            # TODO: This is a kludge because AudioSignal objects are not named uniquely
            score_name = mixture.file_name + '_{}'.format(id(mixture))
            scores[score_name] = cur_score

    return scores

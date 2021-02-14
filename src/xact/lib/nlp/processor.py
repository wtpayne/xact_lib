# -*- coding: utf-8 -*-
"""
NLP processor component.

"""


import spacy


# -----------------------------------------------------------------------------
def reset(runtime, cfg, inputs, state, outputs):
    """
    Reset the NLP processor component.

    """
    state['nlp'] = spacy.load('en_core_web_sm')
    # state['nlp'] = spacy.load('en_core_web_trf')


# -----------------------------------------------------------------------------
def step(inputs, state, outputs):
    """
    Step the NLP processor component.

    """
    return
    if not inputs['chunk']['ena']:
        return

    for doc in state['nlp'].pipe(
                            _iter_text(
                                    list_chunk = inputs['chunk']['list'])):

        print('')
        print('')
        print('#' * 160)
        print('')
        print('')
        print([(ent.text, ent.label_) for ent in doc.ents])


# -----------------------------------------------------------------------------
def _iter_text(list_chunk):
    """
    """
    for chunk in list_chunk:
        yield chunk['text']


        # if not list_slices:
        #     continue

        # print('')
        # print(map_document['filepath'])
        # print('=' * len(map_document['filepath']))

        # first_page = list_slices[0]
        # for (idx, ent) in enumerate(first_page.ents):
        #     print(repr(ent.text))
        #     if idx > 30:
        #         break



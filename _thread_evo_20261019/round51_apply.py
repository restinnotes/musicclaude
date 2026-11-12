"""Apply approved R51 edits mechanically, retaining the final choice verbatim."""
import sys
import experiment_batch as B
import round50_apply as A
import round34_restore as R
import round51_continue as C


def apply(tag):
    answers = {w: A.checked(w, 'r49b', f'sc{tag}_{w}_A5') for w in B.F.WORKS}
    for w, answer in answers.items():
        graph = B.V.graph_of(w, 'r49b')
        final = graph['segments'][-1]['items'][-1]
        assert not any(e['id'] == final['id'] for e in answer['edits']), 'final choice changed'
        assert not (B.V.OUT / f'{w}_{tag}.json').exists(), 'target exists'
    for w, answer in answers.items():
        R.apply(w, tag, 'r49b', answer)
    receipt = {'tag': tag, 'base': 'r49b', 'body_source': 'fully read approved model output only',
               'calls': 0, 'final_choice_verbatim': True,
               'length_target_deviation_chars': {w: a['_length_target_deviation'] for w, a in answers.items()},
               'output_hashes': {w: B.digest((B.V.OUT / f'{w}_{tag}.json').read_text(encoding='utf-8')) for w in B.F.WORKS}}
    B.write_frozen(C.ROOT / f'{tag}_applied.json', B.json_text(receipt))
    print(B.json_text(receipt))


if __name__ == '__main__':
    apply(sys.argv[1])

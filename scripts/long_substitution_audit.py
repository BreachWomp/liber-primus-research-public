"""Independent final substitution candidates/neighborhoods, shared by unknown audit."""
from collections import Counter
import itertools
import time
from verify_terminated_benchmark import Reference,to_indices
from liberprimus.alphabet import transliterate

class SubstitutionVerifier(Reference):
    def __init__(self):
        super().__init__();self.counts=Counter();self.deadline=time.perf_counter()+900

    def check_score(self,p,ends,s):
        assert time.perf_counter()<self.deadline
        assert abs(self.score(p,ends)-s)<1e-9
        self.counts['independent_candidate_scores']+=1

    def result(self,cipher,ends,result):
        assert 1<=len(result['restarts'])<=24
        assert len(result['restarts'])==len(result['warmup']['restarts'])
        for final,warm in zip(result['restarts'],result['warmup']['restarts']):
            assert final['restart']==warm['restart']
            key=final['mapping_cipher_to_plain'];assert sorted(key)==list(range(29))
            plain=[key[x] for x in cipher];assert plain==to_indices(final['plaintext_runes'])
            assert transliterate(plain)==final['transliteration'];self.check_score(plain,ends,final['score'])
            inverse=[key.index(x) for x in range(29)];assert [inverse[x] for x in plain]==cipher
            self.counts['reencryptions']+=1
            wkey=warm['mapping_cipher_to_plain'];assert sorted(wkey)==list(range(29))
            wp=[wkey[x] for x in cipher];assert wp==to_indices(warm['plaintext_runes'])
            assert abs(self.old.character_model.score(wp)-warm['score'])<1e-9
            assert final['score']>=self.score(wp,ends)-1e-9
            steps=final['word_accepted_swaps'];assert 0<=steps<=40
            assert final['word_evaluations']==1+406*(steps+int(steps<40))
            if steps<40:
                for a,b in itertools.combinations(range(29),2):
                    trial=key[:];trial[a],trial[b]=trial[b],trial[a]
                    q=[trial[x] for x in cipher]
                    assert self.score(q,ends)<=final['score']+1e-9
                    self.counts['independent_final_neighbor_scores']+=1
        top=max(result['restarts'],key=lambda x:x['score']);assert result['top']==top
        found=to_indices(top['plaintext_runes'])
        return top

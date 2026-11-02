"""Frozen E036 substitution search with the new word objective only."""
from boundary_substitution import solve as previous_solve
from ngram_arrays import dense_tables
from terminated_word_arrays import TerminatedArrays


class SearchArrays(TerminatedArrays):
    def __init__(self,model,old):
        super().__init__(model)
        self.lookup=dense_tables(old.character_model)


def solve(values,ends,model,arrays,seed,deadline):
    return previous_solve(values,ends,model,arrays,seed,deadline)

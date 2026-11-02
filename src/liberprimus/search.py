"""Bounded seeded search building blocks. Higher objective values are better.

Callbacks must terminate, be deterministic, and must not mutate their inputs.
Budgets count objective evaluations (annealing/genetic) or visited candidates
(beam/constraints). These are finite work bounds, not wall-clock guarantees.
No search result is automatically promoted to a decipherment.
"""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from math import exp, isfinite, log
from random import Random

State = tuple[int, ...]
Objective = Callable[[State], float]


def _positive(value: int, name: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _seed(seed: int) -> Random:
    if type(seed) is not int:
        raise ValueError("seed must be an explicit integer")
    return Random(seed)


def _score(objective: Objective, state: State) -> float:
    value = float(objective(state))
    if not isfinite(value):
        raise ValueError("objective must return a finite score")
    return value


@dataclass(frozen=True)
class SearchResult:
    state: State
    score: float
    evaluations: int
    seed: int
    algorithm: str


def swap_mutation(state: State, rng: Random) -> State:
    """Permutation-preserving move for substitution or column-order keys."""
    if len(state) < 2:
        return state
    a, b = rng.sample(range(len(state)), 2)
    result = list(state)
    result[a], result[b] = result[b], result[a]
    return tuple(result)


def residue_mutation(state: State, rng: Random, modulus: int = 29) -> State:
    _positive(modulus, "modulus")
    if modulus == 1:
        raise ValueError("modulus must exceed 1")
    if not state:
        raise ValueError("cannot mutate an empty key")
    if any(type(x) is not int or not 0 <= x < modulus for x in state):
        raise ValueError("key values must be residues within the modulus")
    result = list(state)
    position = rng.randrange(len(result))
    result[position] = (result[position] + rng.randrange(1, modulus)) % modulus
    return tuple(result)


def permutation_crossover(left: State, right: State, rng: Random) -> State:
    """Order crossover with an inherited contiguous slice."""
    if len(left) != len(right) or len(set(left)) != len(left) or set(left) != set(right):
        raise ValueError("parents must be permutations of the same distinct elements")
    if len(left) < 2:
        return left
    a, b = sorted(rng.sample(range(len(left) + 1), 2))
    retained = set(left[a:b])
    remainder = iter(x for x in right if x not in retained)
    return tuple(left[i] if a <= i < b else next(remainder) for i in range(len(left)))


def simulated_annealing(initial: Sequence[int], objective: Objective, *,
                        evaluations: int, seed: int,
                        mutate: Callable[[State, Random], State] = swap_mutation,
                        start_temperature: float = 1.0,
                        end_temperature: float = 0.01) -> SearchResult:
    _positive(evaluations, "evaluations")
    if any(not isfinite(t) or t <= 0 for t in (start_temperature, end_temperature)):
        raise ValueError("temperatures must be finite and positive")
    rng, state = _seed(seed), tuple(initial)
    current = _score(objective, state)
    best, best_score = state, current
    for iteration in range(1, evaluations):
        fraction = (iteration - 1) / max(1, evaluations - 2)
        temperature = exp(log(start_temperature) * (1 - fraction) + log(end_temperature) * fraction)
        candidate = tuple(mutate(state, rng))
        score = _score(objective, candidate)
        difference = score - current
        if difference >= 0 or rng.random() < exp(difference / temperature):
            state, current = candidate, score
        if score > best_score:
            best, best_score = candidate, score
    return SearchResult(best, best_score, evaluations, seed, "simulated_annealing")


def genetic_search(initial_population: Iterable[Sequence[int]], objective: Objective, *,
                   evaluations: int, seed: int,
                   crossover: Callable[[State, State, Random], State] = permutation_crossover,
                   mutate: Callable[[State, Random], State] = swap_mutation,
                   mutation_rate: float = 0.2) -> SearchResult:
    """Steady-state elitist GA, selecting parents by two-way tournament.

    Each child costs exactly one evaluation. The best of population+child
    survives, so poor children cannot erase the current best candidate.
    """
    _positive(evaluations, "evaluations")
    if not isfinite(mutation_rate) or not 0 <= mutation_rate <= 1:
        raise ValueError("mutation_rate must be in [0,1]")
    rng = _seed(seed)
    # Avoid consuming an unbounded initial-population iterator.
    population = []
    for individual in initial_population:
        if len(population) >= evaluations:
            raise ValueError("population size must not exceed evaluation budget")
        population.append(tuple(individual))
    if len(population) < 2 or any(len(s) != len(population[0]) for s in population):
        raise ValueError("population needs at least two equal-length states")
    ranked = [(state, _score(objective, state)) for state in population]
    used = len(ranked)
    while used < evaluations:
        left = max(rng.sample(ranked, 2), key=lambda pair: pair[1])[0]
        right = max(rng.sample(ranked, 2), key=lambda pair: pair[1])[0]
        child = tuple(crossover(left, right, rng))
        if rng.random() < mutation_rate:
            child = tuple(mutate(child, rng))
        ranked.append((child, _score(objective, child)))
        used += 1
        ranked.sort(key=lambda pair: pair[1], reverse=True)
        ranked.pop()
    best, score = max(ranked, key=lambda pair: pair[1])
    return SearchResult(best, score, used, seed, "genetic_search")


@dataclass(frozen=True)
class BeamResult:
    candidates: tuple[tuple[State, float], ...]
    visited: int
    evaluations: int
    completed_depth: int
    exhausted_budget: bool


def beam_search(initial: Sequence[int], expand: Callable[[State], Iterable[State]],
                objective: Objective, *, depth: int, width: int, max_nodes: int,
                constraint: Callable[[State], bool] = lambda state: True) -> BeamResult:
    """Deterministic layer search with a hard bound on visited candidates.

    Constraints run before scoring. Candidate iteration order breaks ties.
    completed_depth excludes any partially expanded last layer. On budget
    exhaustion candidates may belong to that partial next layer.
    """
    if type(depth) is not int or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    _positive(width, "width")
    _positive(max_nodes, "max_nodes")
    initial = tuple(initial)
    if not constraint(initial):
        return BeamResult((), 1, 0, 0, False)
    frontier = [(initial, _score(objective, initial))]
    visited, evaluations, completed = 1, 1, 0
    for _ in range(depth):
        candidates, seen = [], set()
        for state, _ in frontier:
            children = iter(expand(state))
            while True:
                if visited >= max_nodes:
                    candidates.sort(key=lambda pair: pair[1], reverse=True)
                    return BeamResult(tuple(candidates[:width] or frontier), visited,
                                      evaluations, completed, True)
                try:
                    child = tuple(next(children))
                except StopIteration:
                    break
                visited += 1
                if child in seen or not constraint(child):
                    continue
                seen.add(child)
                candidates.append((child, _score(objective, child)))
                evaluations += 1
        candidates.sort(key=lambda pair: pair[1], reverse=True)
        frontier = candidates[:width]
        completed += 1
        if not frontier:
            break
    return BeamResult(tuple(frontier), visited, evaluations, completed, False)


@dataclass(frozen=True)
class ConstraintResult:
    solutions: tuple[State, ...]
    visited: int
    complete: bool


def solve_constraints(domains: Sequence[Sequence[int]], consistent: Callable[[State], bool], *,
                      max_nodes: int, max_solutions: int) -> ConstraintResult:
    """Finite-domain depth-first enumeration, pruning inconsistent prefixes.

    complete=False means stopped at a supplied bound; it never means that
    the remaining assignments are impossible. consistent must accept ().
    """
    _positive(max_nodes, "max_nodes")
    _positive(max_solutions, "max_solutions")
    choices = [tuple(domain) for domain in domains]
    stack, found, visited = [()], [], 0
    while stack and visited < max_nodes and len(found) < max_solutions:
        prefix = stack.pop()
        visited += 1
        if not consistent(prefix):
            continue
        if len(prefix) == len(choices):
            found.append(prefix)
        else:
            stack.extend(prefix + (value,) for value in reversed(choices[len(prefix)]))
    return ConstraintResult(tuple(found), visited, not stack)

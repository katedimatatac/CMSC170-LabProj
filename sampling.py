import random
from typing import List, Tuple

from dataloading import Scenario

def sample_scenarios_systematic(
    scenarios: List[Scenario],
    target_count: int = 100,
    seed: int = 67,
) -> List[Tuple[int, Scenario]]:
    """Systematically samples `target_count` valid scenarios across the entire .scen file

    using step size k = round(total_valid / target_count).

    Returns a list of (scenario_index, Scenario) tuples sorted by scenario index.
    """
    # 1. Filter out trivial start == goal cases while keeping original 0-based indices
    valid_scenarios: List[Tuple[int, Scenario]] = [
        (idx, scen) for idx, scen in enumerate(scenarios) if scen.optimal_length > 0
    ]

    total_valid = len(valid_scenarios)
    if total_valid <= target_count:
        return valid_scenarios

    # 2. Compute rounded step size k = round(N / 200)
    k = max(1, round(total_valid / target_count))

    # 3. Pick a random starting offset within the first interval [0, k - 1]
    rng = random.Random(seed)
    start_offset = rng.randint(0, k - 1)

    # 4. Step through the dataset every k-th scenario
    sampled = [
        valid_scenarios[i]
        for i in range(start_offset, total_valid, k)
    ][:target_count]

    # 5. If rounding k upward left fewer than 200 items, top up evenly from remaining indices
    if len(sampled) < target_count:
        sampled_indices = {idx for idx, _ in sampled}
        remaining = [item for item in valid_scenarios if item[0] not in sampled_indices]
        needed = target_count - len(sampled)
        sampled.extend(rng.sample(remaining, needed))
        sampled.sort(key=lambda item: item[0])

    return sampled
"""
Full bracket generation for Kyorugi.
Builds all rounds (R16 → QF → SF → F) with left/right halves converging on the Final.
Only the first round is populated with athletes. Later rounds are empty slots
(no competitor) so the layout can render properly.
"""
from math import log2, ceil
from collections import defaultdict

from .models import Competitor, DrawEntry

def _next_power_of_two(n):
    if n <= 2:
        return 2
    return 2 ** ceil(log2(n))

def _round_names(bracket_size):
    names = {2: 'F', 4: 'SF', 8: 'QF', 16: 'R16', 32: 'R32', 64: 'R64'}
    rounds = []
    size = bracket_size
    while size >= 2:
        rounds.append(names.get(size, f'R{size}'))
        size //= 2
    return rounds

def _place_athletes(athletes, bracket_size):
    """
    Place athletes so that any two athletes who are BOTH seeded OR
    from the SAME school are placed on opposite halves of the bracket
    (so they can only meet in the final).

    When there are more than 2 conflicting athletes, best-effort is used
    and a warning is emitted at the generate_draw level.
    """
    slots = [None] * bracket_size
    half = bracket_size // 2


    ordered = sorted(athletes, key=lambda a: (not a.is_seeded, a.full_name))

    def conflicts(a, b):
        """True if a and b should be kept on opposite halves."""
        if a is None or b is None:
            return False
        if a.is_seeded and b.is_seeded:
            return True
        if a.school == b.school:
            return True
        return False

    def has_conflict_in_slots(athlete, slot_indices):
        """Would placing athlete at any of these slots conflict with an already-placed athlete?"""
        return any(slots[i] is not None and conflicts(athlete, slots[i]) for i in slot_indices)

    for athlete in ordered:

        left_indices = list(range(0, half))
        right_indices = list(range(half, bracket_size))

        left_safe = not has_conflict_in_slots(athlete, left_indices)
        right_safe = not has_conflict_in_slots(athlete, right_indices)


        left_count = sum(1 for i in left_indices if slots[i] is not None)
        right_count = sum(1 for i in right_indices if slots[i] is not None)

        candidates = []
        if left_safe:
            candidates.append(('L', left_count, left_indices))
        if right_safe:
            candidates.append(('R', right_count, right_indices))


        if not candidates:
            candidates = [
                ('L', left_count, left_indices),
                ('R', right_count, right_indices),
            ]


        candidates.sort(key=lambda t: t[1])
        chosen_half = candidates[0][2]

        for i in chosen_half:
            if slots[i] is None:
                slots[i] = athlete
                break

    return slots

def generate_draw():
    """
    Wipe and regenerate the full bracket for every (gender, weight) category.
    Only first-round matches are populated. Later rounds contain empty slots.
    """
    DrawEntry.objects.all().delete()

    warnings = {}
    groups = defaultdict(list)
    for c in Competitor.objects.all():
        groups[(c.gender, c.weight_category)].append(c)        

    for (gender, weight), athletes in groups.items():
        n = len(athletes)
        if n == 0:
            continue
        
        bracket_size = _next_power_of_two(n)
        rounds = _round_names(bracket_size)
        slots = _place_athletes(athletes, bracket_size)


        school_counts = defaultdict(int)
        for a in athletes:
            school_counts[a.school] += 1
        max_same = max(school_counts.values())

        seed_count = sum(1 for a in athletes if a.is_seeded)

        warnings_list = []
        if max_same > 2:
            warnings_list.append(
                f"{max_same} athletes from the same school — "
                f"some will meet before the final."
            )
        if seed_count > 2:
            warnings_list.append(
                f"{seed_count} seeded athletes — "
                f"some will meet before the final."
            )
        if warnings_list:
            warnings[(gender, weight)] = " | ".join(warnings_list)

        first_round = rounds[0]
        num_first_matches = bracket_size // 2
        half = num_first_matches // 2

        match_num = 1
        for i in range(0, bracket_size, 2):
            side = 'L' if match_num <= half else 'R'
            DrawEntry.objects.create(
                gender=gender, weight_category=weight,
                round_name=first_round, match_number=match_num, slot=1,
                side=side, competitor=slots[i]
            ) 
            DrawEntry.objects.create(
                gender=gender, weight_category=weight,
                round_name=first_round, match_number=match_num, slot=2,
                side=side, competitor=slots[i + 1]
            )
            match_num += 1

        for r_idx in range(1, len(rounds)):
            round_name = rounds[r_idx]
            matches_in_round = bracket_size // (2 ** (r_idx + 1))
            half = matches_in_round // 2
            for m in range(1, matches_in_round + 1):
                side = 'L' if m <= half else 'R'
                for s in (1, 2):
                    DrawEntry.objects.create(
                        gender=gender, weight_category=weight,
                        round_name=round_name, match_number=m, slot=s,
                        side=side, competitor=None
                    )
    return warnings
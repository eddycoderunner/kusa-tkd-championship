from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import CompetitorForm
from .models import Competitor, DrawEntry
from .draw import generate_draw
from collections import defaultdict

def register_competitor(request):
    if request.method == 'POST':
        form = CompetitorForm(request.POST)
        if form.is_valid():
            form.save()
            warnings = generate_draw()

            if warnings:
                for (g, w), msg in warnings.items():
                    messages.warning(request, f"[{g}/{w}] {msg}")

            return redirect('success')
    else:
        form = CompetitorForm()
    return render(request, 'register.html', {'form': form})

def success_view(request):
    return render(request, 'success.html')

def competitors_list(request):
    competitors = Competitor.objects.all()
    return render(request, 'competitors.html', {'competitors': competitors})

def draws_view(request):
    """Render the mirrored bracket for each category."""
    all_draws = _build_draw_tree()
    return render(request, 'draws.html', {'all_draws': all_draws})



def _build_draw_tree():
    """
    Group DrawEntry rows into a mirrored bracket structure.

    For now, only the FIRST round contains athletes. Later rounds are
    empty placeholders we skip in the output. The template renders only
    the populated first round + an empty Final.
    """

    from collections import defaultdict

    raw = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for e in DrawEntry.objects.select_related('competitor').all():
        raw[(e.gender, e.weight_category)][e.round_name][e.match_number][e.slot] = e.competitor

    order = ['R64', 'R32', 'R16', 'QF', 'SF', 'F']

    all_draws = []
    for (gender, weight), rounds_dict in raw.items():
        gender_display = dict(Competitor.GENDER_CHOICES).get(gender, gender).upper()
        title = f"{gender_display} {weight.upper()}"

        round_names = sorted(rounds_dict.keys(), key=lambda r: order.index(r) if r in order else 99)

        first_round_name = round_names[0]
        first_round = rounds_dict[first_round_name]
        sorted_match_nums = sorted(first_round.keys())

        half = len(sorted_match_nums) // 2
        left_nums = sorted_match_nums[:half]
        right_nums = sorted_match_nums[half:]

        def match_obj(mnum):
            slots = first_round[mnum]
            return {'number': mnum, 'c1': slots.get(1), 'c2': slots.get(2)}

        left_matches = [match_obj(m) for m in left_nums]
        right_matches = [match_obj(m) for m in right_nums]


        left_rounds = []
        right_rounds = []

        all_draws.append({
            'title': title,
            'first_rond_name': first_round_name,
            'left_matches': left_matches,
            'right_matches': right_matches,
            'final': {'c1': None, 'c2': None},
        })

    all_draws.sort(key=lambda d: d['title'])
    return all_draws
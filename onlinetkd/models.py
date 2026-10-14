from django.db import models

class Competitor(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    WEIGHT_CHOICES = [
        ('fin', 'Fin'),
        ('fly', 'Fly'),
        ('bantam', 'Bantam'),
        ('feather', 'Feather'),
        ('light', 'Light'),
        ('welter', 'Welter'),
        ('middle', 'Middle'),
        ('heavy', 'Heavy'),
    ]
    SCHOOL_CHOICES = [
        ('KU', 'KU'),
        ('JKUAT', 'JKUAT'),
        ('USIU', 'USIU'),
        ('MKU', 'MKU'),
        ('SPU', 'SPU'),
    ]

    full_name = models.CharField(max_length=255)
    reg_no = models.CharField(max_length=50, unique=True)
    weight_category = models.CharField(max_length=10, choices=WEIGHT_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    school = models.CharField(max_length=10, choices=SCHOOL_CHOICES)
    phone = models.CharField(max_length=15)
    is_seeded = models.BooleanField(default=False)

    class  Meta:
        ordering = ['weight_category', 'gender', 'full_name']

    def __str__(self):
        suffix = " (S)" if self.is_seeded else ""
        return f"{self.full_name}{suffix}"

    @property
    def short_school(self):
        """Return the school code (already short, no truncation)."""
        return self.school if self.school else "___"

class DrawEntry(models.Model):
    """One slot in a generated bracket for a given (gender, weight) category."""
    gender = models.CharField(max_length=1, choices=Competitor.GENDER_CHOICES)
    weight_category = models.CharField(max_length=10, choices=Competitor.WEIGHT_CHOICES)
    round_name = models.CharField(max_length=10)
    match_number = models.IntegerField()
    slot = models.IntegerField()
    side = models.CharField(max_length=5, default='L')
    competitor = models.ForeignKey(
        Competitor, on_delete=models.CASCADE,
        null=True, blank=True, related_name='draw_entries'
    )

    class Meta:
        unique_together = ('gender', 'weight_category', 'round_name', 'match_number', 'slot')
        ordering = ['gender', 'weight_category', 'round_name', 'match_number', 'slot']

    def __str__(self):
        c = self.competitor.full_name if self.competitor else "BYE"
        return f"{self.gender}/{self.weight_category}/{self.round_name}/M{self.match_number}/S{self.slot}: {c}"
        
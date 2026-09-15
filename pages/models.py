import uuid
from django.db import models


class RSVP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    event = models.CharField(max_length=255)
    guests = models.PositiveIntegerField(default=1)
    visit_date = models.DateField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rsvps"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Partner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    partner_type = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "partners"
        ordering = ["-created_at"]

    def __str__(self):
        return self.brand_name if self.brand_name else self.name


class Newsletter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "newsletter"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contacts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class WeeklyEvent(models.Model):
    DAY_CHOICES = [
        ("Monday", "Monday"), ("Tuesday", "Tuesday"), ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"), ("Friday", "Friday"), ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    title = models.CharField(max_length=255)
    tag = models.CharField(max_length=100)
    description = models.TextField()
    time = models.CharField(max_length=100)

    class Meta:
        db_table = "weekly_events"
        ordering = ["id"]

    def __str__(self):
        return f"{self.day} - {self.title}"


class Quiz(models.Model):
    quiz_id = models.CharField(max_length=20, unique=True)
    question = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    points = models.PositiveIntegerField(default=10)

    class Meta:
        db_table = "quiz_bank"

    def __str__(self):
        return self.question


class Puzzle(models.Model):
    puzzle_id = models.CharField(max_length=20, unique=True)
    clue = models.TextField()
    answer = models.CharField(max_length=255)
    points = models.PositiveIntegerField(default=10)

    class Meta:
        db_table = "puzzle_bank"

    def __str__(self):
        return self.clue

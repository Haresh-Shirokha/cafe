from django.contrib import admin
from .models import RSVP, Partner, Newsletter, Contact, WeeklyEvent, Quiz, Puzzle

admin.site.register(RSVP)
admin.site.register(Partner)
admin.site.register(Newsletter)
admin.site.register(Contact)
admin.site.register(WeeklyEvent)
admin.site.register(Quiz)
admin.site.register(Puzzle)

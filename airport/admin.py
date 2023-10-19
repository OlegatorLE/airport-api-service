from django.contrib import admin

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)

admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Order)
admin.site.register(Ticket)

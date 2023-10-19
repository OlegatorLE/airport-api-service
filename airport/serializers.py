from rest_framework import serializers
from .models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, \
    Ticket


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Airport.objects.all(),
    )
    destination = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Airport.objects.all(),
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ('id', 'name')


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=AirplaneType.objects.all()
    )

    class Meta:
        model = Airplane
        fields = ('id', 'name', 'rows', 'seats_in_row', 'airplane_type')


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ('id', 'first_name', 'last_name')


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightListSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(
        slug_field="get_route",
        queryset=Route.objects.all()
    )
    airplane = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Airplane.objects.all()
    )
    crew = CrewSerializer(many=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            'id',
            'route',
            'airplane',
            'departure_time',
            'arrival_time',
            'crew',
            "tickets_available"
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    pass


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'created_at', 'user')


class TicketSerializer(serializers.ModelSerializer):
    flight = serializers.SlugRelatedField(
        slug_field='id', queryset=Flight.objects.all()
    )
    order = serializers.SlugRelatedField(
        slug_field='id', queryset=Order.objects.all()
    )

    class Meta:
        model = Ticket
        fields = ('id', 'row', 'seat', 'flight', 'order')

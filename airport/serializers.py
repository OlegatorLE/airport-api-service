from django.utils import timezone
from rest_framework import serializers

from .models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)


class RouteSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["source"] = instance.source.name
        representation["destination"] = instance.destination.name
        representation["distance"] = f"{instance.distance} km."
        return representation

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )


class RouteSourceDestinationSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "country")


class AirportListSerializer(AirportSerializer):
    pass


class AirportDetailSerializer(AirportSerializer):
    departure_routes = RouteSourceDestinationSerializer(
        many=True, read_only=True
    )
    arrival_routes = RouteSourceDestinationSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city",
            "departure_routes",
            "arrival_routes"
        ]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all()
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["airplane_type"] = instance.airplane_type.name
        return representation

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "airplane_type",
            "rows",
            "seats_in_row",
            "capacity",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.StringRelatedField()
    tickets_available = serializers.IntegerField(read_only=True)
    crew = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(), many=True, required=False
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        crew_representation = [crew.full_name for crew in instance.crew.all()]
        representation["crew"] = crew_representation

        departure_time_representation = timezone.localtime(
            instance.departure_time
        ).strftime("%d-%m-%Y %H:%M")
        arrival_time_representation = timezone.localtime(
            instance.arrival_time
        ).strftime("%d-%m-%Y %H:%M")
        representation["departure_time"] = departure_time_representation
        representation["arrival_time"] = arrival_time_representation

        return representation

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "tickets_available",
            "crew",
        )


class FlightDetailSerializer(FlightSerializer):
    airplane = AirplaneSerializer(read_only=True)
    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "taken_seats",
        )

    def get_taken_seats(self, obj) -> list:
        return [
            f"Row {ticket.row}, Seat {ticket.seat}"
            for ticket in obj.tickets.all()
        ]


class FlightCreateSerializer(serializers.ModelSerializer):
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.select_related("source", "destination"))

    class Meta:
        model = Flight
        fields = [
            "id", "route", "airplane", "departure_time", "arrival_time", "crew"
        ]


class TicketSerializer(serializers.ModelSerializer):
    flight = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(), write_only=True
    )
    flight_representation = serializers.SerializerMethodField()

    def get_flight_representation(self, obj):
        return str(obj.flight.route.route)

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        flight = attrs.get("flight", None)
        if flight is None:
            raise serializers.ValidationError("Flight field is required.")
        Ticket.validate_ticket(
            attrs["row"],
            attrs["flight"].airplane.rows,
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            serializers.ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "flight_representation")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        created_at_representation = timezone.localtime(
            instance.created_at
        ).strftime("%d-%m-%Y %H:%M")
        representation["created_at"] = created_at_representation

        return representation

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import (
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Crew,
    Flight,
    Order,
)
from .serializers import (
    AirportSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    RouteSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    FlightCreateSerializer,
    OrderSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        closest_big_city = self.request.query_params.get("closest_big_city")

        if name:
            queryset = queryset.filter(name__icontains=name)
        if closest_big_city:
            queryset = queryset.filter(
                closest_big_city__icontains=closest_big_city
            )

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by airport name (ex. ?name=Heathrow)",
            ),
            OpenApiParameter(
                "closest_big_city",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by closest big city (ex. ?closest_big_city=Kyiv)"
                ),
            ),
        ]
    )
    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return self.serializer_class


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = (
                queryset.select_related("airplane").annotate(
                    tickets_available=F("airplane__rows")
                    * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            ).order_by("id")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        if self.action == "create":
            return FlightCreateSerializer
        return self.serializer_class


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomAPIRootView(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            return Response(
                {
                    "Airport-API": {
                        "airports": reverse(
                            "airport:airport-list",
                            request=request,
                            format=format,
                        ),
                        "routes": reverse(
                            "airport:route-list",
                            request=request,
                            format=format,
                        ),
                        "airplane_types": reverse(
                            "airport:airplanetype-list",
                            request=request,
                            format=format,
                        ),
                        "airplanes": reverse(
                            "airport:airplane-list",
                            request=request,
                            format=format,
                        ),
                        "crews": reverse(
                            "airport:crew-list", request=request, format=format
                        ),
                        "flights": reverse(
                            "airport:flight-list",
                            request=request,
                            format=format,
                        ),
                        "orders": reverse(
                            "airport:order-list",
                            request=request,
                            format=format,
                        ),
                    },
                    "User-API": {
                        "user_register": reverse(
                            "user:create", request=request, format=format
                        ),
                        "token_obtain_pair": reverse(
                            "user:token_obtain_pair",
                            request=request,
                            format=format,
                        ),
                        "token_refresh": reverse(
                            "user:token_refresh",
                            request=request,
                            format=format,
                        ),
                        "token_verify": reverse(
                            "user:token_verify", request=request, format=format
                        ),
                        "manage_user": reverse(
                            "user:manage", request=request, format=format
                        ),
                    },
                    "Documentation": {
                        "schema": reverse(
                            "schema", request=request, format=format
                        ),
                        "swagger": reverse(
                            "swagger-ui", request=request, format=format
                        ),
                        "redoc": reverse(
                            "redoc", request=request, format=format
                        ),
                    },
                }
            )
        else:
            return Response(
                {
                    "User-API": {
                        "user_register": reverse(
                            "user:create", request=request, format=format
                        ),
                        "token_obtain_pair": reverse(
                            "user:token_obtain_pair",
                            request=request,
                            format=format,
                        ),
                        "token_refresh": reverse(
                            "user:token_refresh",
                            request=request,
                            format=format,
                        ),
                        "token_verify": reverse(
                            "user:token_verify", request=request, format=format
                        ),
                        "manage_user": reverse(
                            "user:manage", request=request, format=format
                        ),
                    },
                    "Documentation": {
                        "schema": reverse(
                            "schema", request=request, format=format
                        ),
                        "swagger": reverse(
                            "swagger-ui", request=request, format=format
                        ),
                        "redoc": reverse(
                            "redoc", request=request, format=format
                        ),
                    },
                }
            )

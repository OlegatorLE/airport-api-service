from django.db.models import F, Count, Q, Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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
from .permissions import IsAdminOrIfAuthenticatedReadOnly
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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = Q()
        name = self.request.query_params.get("name")
        closest_big_city = self.request.query_params.get("closest_big_city")
        country = self.request.query_params.get("country")
        if name:
            query &= Q(name__icontains=name)
        if closest_big_city:
            query &= Q(closest_big_city__icontains=closest_big_city)
        if country:
            query &= Q(country__icontains=country)

        queryset = (
            queryset.filter(query)
            .distinct()
        )

        if self.action == "retrieve":
            departure_routes = Route.objects.select_related("source", "destination")
            arrival_routes = Route.objects.select_related("source", "destination")
       
            queryset = queryset.prefetch_related(
                Prefetch("departure_routes", queryset=departure_routes),
                Prefetch("arrival_routes", queryset=arrival_routes),
           )
        return queryset

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
            OpenApiParameter(
                "country",
                type=OpenApiTypes.STR,
                description=("Filter by country (ex. ?country=China)"),
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
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomAPIRootView(APIView):
    def get_user_api(self, request):
        return {
            "user_register": reverse("user:create", request=request),
            "token_obtain_pair": reverse(
                "user:token_obtain_pair", request=request
            ),
            "token_refresh": reverse("user:token_refresh", request=request),
            "token_verify": reverse("user:token_verify", request=request),
            "manage_user": reverse("user:manage", request=request),
        }

    def get_documentation(self, request):
        return {
            "schema": reverse("schema", request=request),
            "swagger": reverse("swagger-ui", request=request),
            "redoc": reverse("redoc", request=request),
        }

    def get_airport_api(self, request):
        return {
            "airports": reverse("airport:airport-list", request=request),
            "routes": reverse("airport:route-list", request=request),
            "airplane_types": reverse(
                "airport:airplanetype-list", request=request
            ),
            "airplanes": reverse("airport:airplane-list", request=request),
            "crews": reverse("airport:crew-list", request=request),
            "flights": reverse("airport:flight-list", request=request),
            "orders": reverse("airport:order-list", request=request),
        }

    def get(self, request):
        data = {
            "User-API": self.get_user_api(request),
            "Documentation": self.get_documentation(request),
        }

        if request.user.is_authenticated:
            data["Airport-API"] = self.get_airport_api(request)

        return Response(data)

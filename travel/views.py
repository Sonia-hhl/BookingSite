from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Hotel, Flight, Room, HotelReservation, FlightReservation, TourReservation, Tour, Airline
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Hotel, Room, HotelReservation
from .serializers import UserSerializer, HotelSerializer, RoomSerializer, HotelReservationSerializer
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrAdmin
from travel import serializers

def user_bookings(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to view your bookings.')
        return redirect('auth')

    hotel_reservations = HotelReservation.objects.filter(user_id=user_id).select_related('room__hotel')
    flight_reservations = FlightReservation.objects.filter(user_id=user_id).select_related('flight__airline')
    tour_reservations = TourReservation.objects.filter(user_id=user_id).select_related('tour')

    context = {
        'hotel_reservations': hotel_reservations,
        'flight_reservations': flight_reservations,
        'tour_reservations': tour_reservations,
    }

    return render(request, 'listings/booking_list.html', context)

def booking_detail(request, type, booking_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to view booking details.')
        return redirect('auth')

    booking = None
    type = type.lower()

    if type == 'hotel':
        booking = get_object_or_404(HotelReservation, id=booking_id, user_id=user_id)
    elif type == 'flight':
        booking = get_object_or_404(FlightReservation, id=booking_id, user_id=user_id)
    elif type == 'tour':
        booking = get_object_or_404(TourReservation, id=booking_id, user_id=user_id)
    else:
        messages.error(request, 'Invalid booking type.')
        return redirect('user_bookings')

    return render(request, 'listings/booking_detail.html', {'booking': booking, 'type': type})

def flight_list(request):
    flights = Flight.objects.all()

    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    passengers = request.GET.get('passengers')
    sort = request.GET.get('sort', 'date')
    page_number = request.GET.get('page', 1)

    if origin:
        flights = flights.filter(origin__icontains=origin)
    if destination:
        flights = flights.filter(destination__icontains=destination)
    if passengers:
        flights = flights.filter(available_seats__gte=passengers)

    if sort == 'price_asc':
        flights = flights.order_by('price')
    elif sort == 'price_desc':
        flights = flights.order_by('-price')
    else:
        flights = flights.order_by('departure_time')

    paginator = Paginator(flights, 5)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'flights': page_obj.object_list,
        'page_obj': page_obj,
        'search_params': {
            'origin': origin,
            'destination': destination,
            'passengers': passengers,
            'sort': sort
        }
    }
    return render(request, 'listings/flight_list.html', context)

def hotel_list(request):
    hotels = Hotel.objects.all()

    city = request.GET.get('city')
    if city and city.lower() != 'all':
        hotels = hotels.filter(location_city__icontains=city)

    sort = request.GET.get('sort', 'default')
    if sort == 'price_asc':
        hotels = hotels.order_by('rooms__price_per_night').distinct()
    elif sort == 'price_desc':
        hotels = hotels.order_by('-rooms__price_per_night').distinct()
    elif sort == 'rating_desc':
        hotels = hotels.order_by('-star_rating')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(hotels, 3)

    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'hotels': page_obj.object_list,
        'page_obj': page_obj,
        'search_params': {
            'city': city,
            'sort': sort
        }
    }
    return render(request, 'listings/hotel_list.html', context)

def tour_list(request):
    tours = Tour.objects.all()

    destination = request.GET.get('destination')
    sort = request.GET.get('sort', 'default')
    page_number = request.GET.get('page', 1)

    if destination:
        tours = tours.filter(destination__icontains=destination)

    if sort == 'price_asc':
        tours = tours.order_by('price')
    elif sort == 'price_desc':
        tours = tours.order_by('-price')
    elif sort == 'rating_desc':
        tours = tours.order_by('-rating')

    paginator = Paginator(tours, 4)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    context = {
        'tours': page_obj.object_list,
        'page_obj': page_obj,
        'search_params': {
            'destination': destination,
            'sort': sort
        }
    }
    return render(request, 'listings/tour_list.html', context)

def user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to view your profile.')
        return redirect('auth')

    try:
        user = User.objects.get(id=user_id)
        context = {'user': user}
        return render(request, 'listings/profile.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('auth')

def auth_view(request):
    if request.session.get('user_id'):
        return redirect('profile')

    is_signup = request.GET.get('action') == 'signup'

    if request.method == 'POST':
        if is_signup:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone_number = request.POST.get('phone_number', '')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
            else:
                user = User(
                    username=username,
                    email=email,
                    phone_number=phone_number,
                    is_customer=True
                )
                user.password = make_password(password)
                user.save()
                request.session['user_id'] = user.id
                messages.success(request, 'Registration successful.')
                return redirect('profile')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['user_id'] = user.id
                    messages.success(request, 'Login successful.')
                    return redirect('profile')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(request, 'Username not found.')

    return render(request, 'auth.html', {'is_signup': is_signup})

#CRUDS
#hotel
def hotel_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        address = request.POST.get('address')
        description = request.POST.get('description')
        rating = request.POST.get('star_rating')
        contact_email = request.POST.get('contact_email')
        manager_id = request.session.get('user_id')

        if not manager_id:
            messages.error(request, "You must be logged in to add a hotel.")
            return redirect('auth')

        manager = get_object_or_404(User, id=manager_id)

        Hotel.objects.create(
            name=name,
            location_city=city,
            location_address=address,
            description=description,
            star_rating=rating,
            contact_email=contact_email,
            manager=manager
        )
        messages.success(request, "Hotel created successfully.")
        return redirect('hotel_list')

    return render(request, 'listings/hotel_create.html')

def hotel_update(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        hotel.name = request.POST.get('name')
        hotel.location_city = request.POST.get('city')
        hotel.location_address = request.POST.get('address')
        hotel.description = request.POST.get('description')
        hotel.star_rating = request.POST.get('star_rating')
        hotel.contact_email = request.POST.get('contact_email')
        hotel.save()
        messages.success(request, "Hotel updated successfully.")
        return redirect('hotel_detail', hotel_id=hotel.id)

    return render(request, 'listings/hotel_create.html', {'hotel': hotel})

def hotel_delete(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        hotel.delete()
        messages.success(request, "Hotel deleted successfully.")
    
    return redirect('hotel_list')


#flight
def flight_create(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        airline_id = request.POST.get('airline')
        seat_count = request.POST.get('seat_count')
        available_seats = request.POST.get('available_seats')
        price = request.POST.get('price')

        airline = get_object_or_404(Airline, id=airline_id)

        Flight.objects.create(
            flight_number=flight_number,
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            airline=airline,
            seat_count=seat_count,
            available_seats=available_seats,
            price=price
        )

        messages.success(request, 'Flight created successfully.')
        return redirect('flight_list')

    airlines = Airline.objects.all()  
    return render(request, 'listings/flight_create.html', {'airlines': airlines})


def flight_update(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        flight.flight_number = request.POST.get('flight_number')
        flight.origin = request.POST.get('origin')
        flight.destination = request.POST.get('destination')
        flight.departure_time = request.POST.get('departure_time')
        flight.arrival_time = request.POST.get('arrival_time')
        airline_id = request.POST.get('airline')
        flight.airline = get_object_or_404(Airline, id=airline_id)
        flight.seat_count = request.POST.get('seat_count')
        flight.available_seats = request.POST.get('available_seats')
        flight.price = request.POST.get('price')
        flight.save()

        messages.success(request, 'Flight updated successfully.')
        return redirect('flight_list')

    airlines = Airline.objects.all()
    return render(request, 'listings/flight_create.html', {'flight': flight, 'airlines': airlines})

def flight_delete(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    flight.delete()
    messages.success(request, 'Flight deleted successfully.')
    return redirect('flight_list')

#Tour
def tour_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        destination = request.POST.get('destination')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        price = request.POST.get('price')
        max_participants = request.POST.get('max_participants')
        available_slots = request.POST.get('available_slots')
        guide_name = request.POST.get('guide_name')
        image = request.FILES.get('image')

        Tour.objects.create(
            name=name,
            description=description,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            price=price,
            max_participants=max_participants,
            available_slots=available_slots,
            guide_name=guide_name,
            image=image
        )

        messages.success(request, "Tour created successfully.")
        return redirect('tour_list')

    return render(request, 'listings/tour_create.html')

def tour_update(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == 'POST':
        tour.name = request.POST.get('name')
        tour.description = request.POST.get('description')
        tour.destination = request.POST.get('destination')
        tour.start_date = request.POST.get('start_date')
        tour.end_date = request.POST.get('end_date')
        tour.price = request.POST.get('price')
        tour.max_participants = request.POST.get('max_participants')
        tour.available_slots = request.POST.get('available_slots')
        tour.guide_name = request.POST.get('guide_name')

        if 'image' in request.FILES:
            tour.image = request.FILES['image']

        tour.save()
        messages.success(request, "Tour updated successfully.")
        return redirect('tour_list')

    return render(request, 'listings/tour_create.html', {'tour': tour})

def tour_delete(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    tour.delete()
    messages.success(request, "Tour deleted successfully.")
    return redirect('tour_list')



# Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'count'
    max_page_size = 100

# User Management
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

# Authentication
class SignupView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Hotel Management
class HotelListView(generics.ListAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

class HotelDetailView(generics.RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [AllowAny]

class RoomListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return Room.objects.filter(hotel_id=hotel_id)

class RoomDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

# Reservation Management
class ReservationListView(generics.ListAPIView):
    serializer_class = HotelReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return HotelReservation.objects.filter(user=self.request.user)

class ReservationCreateView(generics.CreateAPIView):
    serializer_class = HotelReservationSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        room_id = self.request.data.get('room_id')
        room = Room.objects.get(id=room_id)
        if not room.is_available:
            raise serializers.ValidationError("Room is not available")
        serializer.save(user=self.request.user, room=room)
        room.is_available = False
        room.save()

class ReservationCancelView(APIView):
    permission_classes = [IsOwnerOrAdmin]
    def post(self, request, id):
        print(f"Current user: {request.user}, Is authenticated: {request.user.is_authenticated}")
        try:
            reservation = HotelReservation.objects.get(id=id)
            print(f"Reservation ID: {id}, Reservation user: {reservation.user}, Room: {reservation.room}")
        except HotelReservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            reservation.room.is_available = True
            reservation.room.save()
            reservation.delete()
            return Response({'message': 'Reservation cancelled'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Failed to cancel reservation: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            
class ReservationDetailView(generics.RetrieveAPIView):
    queryset = HotelReservation.objects.all()
    serializer_class = HotelReservationSerializer
    permission_classes = [IsOwnerOrAdmin]
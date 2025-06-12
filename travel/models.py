from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_customer = models.BooleanField(default=True)
    is_hotel_manager = models.BooleanField(default=False)
    is_airline_manager = models.BooleanField(default=False)


class Airline(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    fleet_size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Flight(models.Model):
    flight_number = models.CharField(max_length=255, unique=True)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    seat_count = models.IntegerField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.flight_number} ({self.origin} → {self.destination})"


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 'fas fa-wifi'")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location_city = models.CharField(max_length=100)
    location_address = models.TextField()
    description = models.TextField(blank=True)
    star_rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    contact_email = models.EmailField(blank=True)
    main_image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_hotels')

    def __str__(self):
        return f"{self.name} ({self.location_city})"


class RoomType(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Single, Double, Suite, Deluxe King")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    room_number = models.CharField(max_length=10, help_text="e.g., '101', 'A-203'")
    capacity = models.PositiveSmallIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='rooms')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.name if self.room_type else 'N/A'}) - {self.hotel.name}"

    class Meta:
        unique_together = ('hotel', 'room_number')


class BaseReservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=6,
        choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')],
        default='Paid'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"Reservation #{self.pk} - {self.user.username}"

class HotelReservation(BaseReservation):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"Hotel Reservation #{self.pk} - Room: {self.room} - User: {self.user.username}"

class FlightReservation(BaseReservation):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)

    def __str__(self):
        return f"Flight Reservation #{self.pk} - Flight: {self.flight} - User: {self.user.username}"

class TourReservation(BaseReservation):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE)

    def __str__(self):
        return f"Tour Reservation #{self.pk} - Tour: {self.tour} - User: {self.user.username}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Credit Card', 'Credit Card'),
        ('PayPal', 'PayPal'),
        ('ApplePay/Google Pay', 'ApplePay/Google Pay'),
    ]
    hotel_reservation = models.OneToOneField(
        HotelReservation, on_delete=models.CASCADE, null=True, blank=True, related_name='payment'
    )
    flight_reservation = models.OneToOneField(
        FlightReservation, on_delete=models.CASCADE, null=True, blank=True, related_name='payment'
    )
    tour_reservation = models.OneToOneField(
        TourReservation, on_delete=models.CASCADE, null=True, blank=True, related_name='payment'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Credit Card')
    status = models.CharField(max_length=6, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Paid')

    def __str__(self):
        return f"Payment for Reservation #{self.pk}"
    
class Tour(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_participants = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()
    guide_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='tour_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.destination})"

class Review(models.Model):
    REVIEW_TYPE_CHOICES = [('HOTEL', 'Hotel'), ('FLIGHT', 'Flight'), ('TOUR', 'Tour'),]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_type = models.CharField(max_length=6, choices=REVIEW_TYPE_CHOICES, default='HOTEL')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=True, blank=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True, blank=True)
    
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review ({self.review_type})"

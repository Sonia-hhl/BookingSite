from rest_framework import serializers
from .models import User, Hotel, Room, HotelReservation, RoomType, Amenity

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'is_customer', 'is_hotel_manager', 'is_airline_manager']
        read_only_fields = ['id']

class HotelSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'location_city', 'location_address', 'description', 'star_rating', 'contact_email', 'main_image', 'manager']
        read_only_fields = ['id', 'manager']

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon_class']
        read_only_fields = ['id']

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class RoomSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    room_type = RoomTypeSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = ['id', 'hotel', 'room_type', 'room_number', 'capacity', 'price_per_night', 'amenities', 'is_available']
        read_only_fields = ['id', 'hotel']

class HotelReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = HotelReservation
        fields = ['id', 'user', 'room', 'reservation_date', 'payment_status']
        read_only_fields = ['id', 'user', 'reservation_date']
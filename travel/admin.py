from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError

class HotelReservationInline(admin.TabularInline):
    model = HotelReservation
    extra = 0
    can_delete = True
    show_change_link = True

class FlightReservationInline(admin.TabularInline):
    model = FlightReservation
    extra = 0
    can_delete = True
    show_change_link = True

class TourReservationInline(admin.TabularInline):
    model = TourReservation
    extra = 0
    can_delete = True
    show_change_link = True

class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)

class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') 
    search_fields = ('name',)

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1  
    fields = ('room_number', 'room_type', 'capacity', 'price_per_night', 'is_available')
    fk_name = 'hotel' 
    show_change_link = True

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'rating', 'comment', 'created_at')
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.parent_object_id:
            return qs.filter(room__hotel__id=self.parent_object_id, review_type='HOTEL').order_by('-created_at')
        return qs.none()
    
    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object_id = obj.id if obj else None
        return super().get_formset(request, obj, **kwargs)
    
class HotelReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'review_type', 'rating', 'comment', 'created_at')  # اضافه کردن created_at به fields
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.parent_object_id:
            return qs.filter(room__hotel__id=self.parent_object_id, review_type='HOTEL').order_by('-created_at')
        return qs.none()

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object_id = obj.id if obj else None
        return super().get_formset(request, obj, **kwargs)
    
class FlightReviewInline(admin.TabularInline):
    model = Review
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.parent_object_id:
            return qs.filter(flight__id=self.parent_object_id, review_type='FLIGHT')
        return qs.none()

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_object_id = obj.id if obj else None
        return super().get_formset(request, obj, **kwargs)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hotel', 'room_type', 'price_per_night', 'capacity', 'is_available')
    list_filter = ('hotel', 'room_type', 'is_available', 'capacity')
    search_fields = ('room_number', 'hotel__name', 'room_type__name')
    filter_horizontal = ('amenities',) 
    fieldsets = (
        (None, {
            'fields': ('hotel', 'room_number', 'room_type')
        }),
        ('Details & Pricing', {
            'fields': ('capacity', 'price_per_night', 'amenities')
        }),
        ('Availability', {
            'fields': ('is_available',)
        }),
    )
    inlines = [HotelReviewInline]
admin.site.register(Room, RoomAdmin)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_city', 'star_rating', 'contact_email')
    list_filter = ('star_rating', 'location_city')
    search_fields = ('name', 'location_city', 'contact_email')
    inlines = [RoomInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'main_image', 'description')
        }),
        ('Location & Contact', {
            'fields': ('location_city', 'location_address', 'contact_email')
        }),
        ('Details', {
            'fields': ('star_rating','manager')
        }),
    )

@admin.register(HotelReservation)
class HotelReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'reservation_date', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('user__username', 'user__email', 'room__room_number', )
    date_hierarchy = 'reservation_date'

@admin.register(FlightReservation)
class FlightReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'flight', 'seat_number', 'reservation_date', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('user__username', 'user__email', 'flight__flight_number', 'flight__origin', 'flight__destination')
    date_hierarchy = 'reservation_date'

@admin.register(TourReservation)
class TourReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'reservation_date', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('user__username', 'user__email', 'tour__name')
    date_hierarchy = 'reservation_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'review_type', 'rating', 'created_at')
    list_filter = ('rating','review_type')
    search_fields = ('user__email',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    actions = ['delete_selected']

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = [HotelReservationInline, FlightReservationInline, TourReservationInline]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_customer', 'is_hotel_manager', 'is_airline_manager'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Roles', {'fields': ('is_customer', 'is_hotel_manager', 'is_airline_manager')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'is_customer', 'is_hotel_manager', 'is_airline_manager', 'is_superuser')
    list_filter = ('is_customer', 'is_hotel_manager', 'is_airline_manager')
    search_fields = ('username', 'email')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'origin', 'destination', 'departure_time', 'arrival_time', 'airline', 'available_seats', 'price')
    list_filter = ('airline', 'origin', 'destination')
    search_fields = ('flight_number', 'origin', 'destination')
    ordering = ('departure_time',)
    inlines = [FlightReviewInline]


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'contact_number', 'fleet_size')

admin.site.register(Amenity, AmenityAdmin)
admin.site.register(RoomType, RoomTypeAdmin)


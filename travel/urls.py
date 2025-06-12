from django.urls import path, re_path
from . import views

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),
    path('bookings/', views.user_bookings, name='booking_list'),
    path('booking/<str:type>/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('flights/', views.flight_list, name='flight_list'),
    path('tours/', views.tour_list, name='tour_list'),
    path('profile/', views.user_profile, name='profile'),

    re_path(r'^bookings/hotels/(?P<page>\d+)/$', views.hotel_list, name='hotel_list_page'),
    re_path(r'^bookings/flights/(?P<page>\d+)/$', views.flight_list, name='flight_list_page'),
    
    path('hotels/create/', views.hotel_create, name='hotel_create'),
    path('hotels/<int:hotel_id>/edit/', views.hotel_update, name='hotel_update'),
    path('hotels/<int:hotel_id>/delete/', views.hotel_delete, name='hotel_delete'),

    path('flights/create/', views.flight_create, name='flight_create'),
    path('flights/<int:flight_id>/edit/', views.flight_update, name='flight_update'),
    path('flights/<int:flight_id>/delete/', views.flight_delete, name='flight_delete'),

    path('tours/create/', views.tour_create, name='tour_create'),
    path('tours/<int:tour_id>/edit/', views.tour_update, name='tour_update'),
    path('tours/<int:tour_id>/delete/', views.tour_delete, name='tour_delete'),

    #APIs
    # User Management
    path('api/user/', views.UserListView.as_view(), name='user-list'),
    path('api/user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('api/user/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    path('api/user/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    
    # Authentication
    path('api/auth/signup/', views.SignupView.as_view(), name='signup'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    
    # Hotel Management
    path('api/hotel/', views.HotelListView.as_view(), name='hotel-list'),
    path('api/hotel/<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail'),
    path('api/hotel/<int:hotel_id>/room/', views.RoomListView.as_view(), name='room-list'),
    path('api/room/<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    
    # Reservation Management
    path('api/reservation/', views.ReservationListView.as_view(), name='reservation-list'),
    path('api/reservation/create/', views.ReservationCreateView.as_view(), name='reservation-create'),
    path('api/reservation/<int:id>/cancel/', views.ReservationCancelView.as_view(), name='reservation-cancel'),
    path('api/reservation/<int:pk>/', views.ReservationDetailView.as_view(), name='reservation-detail'),
]


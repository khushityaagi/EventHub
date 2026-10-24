
from django.db import transaction
from rest_framework import serializers

from .models import Event, Reservation


class EventSerializer(serializers.ModelSerializer):
    reservations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'venue',
            'date',
            'total_seats',
            'available_seats',
            'status',
            'created_at',
            'reservations_count',
        ]

    def get_reservations_count(self, obj):
        return obj.reservations.filter(status='confirmed').count()

    def validate(self, data):
        total = data.get(
            'total_seats',
            getattr(self.instance, 'total_seats', None),
        )
        available = data.get(
            'available_seats',
            getattr(self.instance, 'available_seats', None),
        )

        if total is not None and total < 1:
            raise serializers.ValidationError({
                'total_seats': 'Total seats must be at least 1.'
            })

        if available is not None and available < 0:
            raise serializers.ValidationError({
                'available_seats': 'Available seats cannot be negative.'
            })

        if total is not None and available is not None:
            if available > total:
                raise serializers.ValidationError({
                    'available_seats':
                        'Available seats cannot exceed total seats.'
                })

        return data


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id',
            'event',
            'attendee_name',
            'attendee_email',
            'seats_reserved',
            'status',
            'created_at',
        ]
        read_only_fields = ['status', 'created_at']

    def validate_seats_reserved(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Must reserve at least 1 seat.'
            )
        return value

    def validate(self, data):
        event = data.get(
            'event',
            getattr(self.instance, 'event', None),
        )
        seats_reserved = data.get(
            'seats_reserved',
            getattr(self.instance, 'seats_reserved', 0),
        )

        if event is not None:
            if event.status not in ('upcoming', 'ongoing'):
                raise serializers.ValidationError(
                    f'Cannot reserve seats for a {event.status} event.'
                )

            if self.instance is None and seats_reserved > event.available_seats:
                raise serializers.ValidationError(
                    f'Only {event.available_seats} seat(s) available.'
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        event = Event.objects.select_for_update().get(
            pk=validated_data['event'].pk
        )
        seats = validated_data['seats_reserved']

        # Recheck availability after locking the event row.
        if event.status not in ('upcoming', 'ongoing'):
            raise serializers.ValidationError(
                f'Cannot reserve seats for a {event.status} event.'
            )

        if seats > event.available_seats:
            raise serializers.ValidationError(
                f'Only {event.available_seats} seat(s) available.'
            )

        event.available_seats -= seats
        event.save(update_fields=['available_seats'])

        validated_data['event'] = event
        return Reservation.objects.create(**validated_data)

# EventHub API

EventHub is a backend API for an event ticketing platform built with Django and Django REST Framework.

## Setup
1. `python -m venv venv`
2. `venv\Scripts\activate`
3. `pip install django djangorestframework`
4. `python manage.py migrate`
5. `python manage.py runserver`

## Endpoints
- `GET/POST /api/events/`
- `GET/POST /api/reservations/`
- `POST /api/reservations/{id}/cancel/`

## Design Decision
Seat deduction happens directly in `ReservationSerializer.create()` to ensure atomic capacity updates on creation.
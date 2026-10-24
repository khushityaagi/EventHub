# EventHub API

EventHub is a backend REST API for an event ticketing platform built with Django and Django REST Framework (DRF).

It allows users to create and browse events, reserve seats, cancel reservations, and check event availability.

## Features

- Create, retrieve, update, and delete events.
- Filter events by status and venue.
- Create and list reservations.
- Validate reservation seat counts and event status.
- Prevent reservations that exceed the currently available seat count.
- Cancel reservations and restore seats.
- Filter reservations by event ID.
- Count confirmed reservations for each event.
- Log HTTP requests, response status codes, and request duration.
- Automated API tests using Django REST Framework's `APITestCase`.

## Technology Stack

- Python
- Django
- Django REST Framework
- SQLite
- Django automated testing framework

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/khushityaagi/EventHub.git
cd EventHub
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure the Django secret key

Set the `DJANGO_SECRET_KEY` environment variable if your settings require it.

Generate a development secret key using:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the generated value in your current PowerShell session:

```powershell
$env:DJANGO_SECRET_KEY = "paste-generated-key-here"
```

Never commit your secret key to GitHub.

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API is available at:

`http://127.0.0.1:8000/`

## API Endpoints

All endpoints use the `/api/` prefix.

### Events

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/events/` | List events |
| POST | `/api/events/` | Create an event |
| GET | `/api/events/{id}/` | Retrieve an event |
| PUT/PATCH | `/api/events/{id}/` | Update an event |
| DELETE | `/api/events/{id}/` | Delete an event |

**Filtering examples**

- `/api/events/?status=upcoming`
- `/api/events/?venue=Agra`

The venue filter performs a case-insensitive partial match.

### Reservations

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reservations/` | List reservations |
| POST | `/api/reservations/` | Create a reservation |
| GET | `/api/reservations/{id}/` | Retrieve a reservation |
| PUT/PATCH | `/api/reservations/{id}/` | Update a reservation |
| DELETE | `/api/reservations/{id}/` | Delete a reservation |
| POST | `/api/reservations/{id}/cancel/` | Cancel a reservation |

**Filtering example**

`/api/reservations/?event_id=1`

### Create an Event

Request: `POST /api/events/`

```json
{
  "title": "Django Conference",
  "venue": "Agra Convention Centre",
  "date": "2027-03-20",
  "total_seats": 100,
  "available_seats": 100,
  "status": "upcoming"
}
```

### Create a Reservation

Request: `POST /api/reservations/`

```json
{
  "event": 1,
  "attendee_name": "Asha Sharma",
  "attendee_email": "asha@example.com",
  "seats_reserved": 2
}
```

A successful reservation returns `201 Created` and deducts the requested seats from the event's availability.

### Cancel a Reservation

Request: `POST /api/reservations/1/cancel/`

No request body is required.

A successful cancellation returns the updated reservation and restores its reserved seats. Repeated cancellation requests return `400 Bad Request`.

## Validation and Error Handling

The API validates seat counts and event status before accepting reservations.

Examples of rejected requests include:

- Reserving fewer than one seat.
- Reserving more seats than are available.
- Reserving seats for an event that is not upcoming or ongoing.
- Creating an event with zero total seats.
- Providing negative available seats.
- Setting available seats above total seats.
- Cancelling an already-cancelled reservation.

Invalid requests return an appropriate `400 Bad Request` response.

## Automated Testing

Run the automated API tests with:

```bash
python manage.py test events
```

The current test suite contains 14 tests covering event listing, filtering, seat validation, reservation creation, overbooking, cancellation, seat restoration, and reservation counts.

The tests have passed in the development environment. Run them again after making changes to verify the current code.

## Request Logging Middleware

`RequestLoggingMiddleware` records the HTTP method, request path, response status code, and request duration. Logs are written to the configured console logger.

## Design Decision

Seat availability is updated as part of reservation creation rather than being managed separately by the API view. This keeps the booking operation close to the reservation's validation and creation logic.

Database transactions and row-locking queries are used to improve consistency during reservation creation and cancellation. Row-level locking behavior depends on the database backend; SQLite does not provide the same row-level locking guarantees as PostgreSQL. Concurrent booking safety should therefore be verified against the intended production database.

## Limitations

- The project uses SQLite for local development.
- Authentication and authorization are not currently part of the assignment's required feature set.
- Production deployment requires appropriate secret management, security settings, and database configuration.

## Author

Khushi Tyagi

GitHub: https://github.com/khushityaagi/EventHub

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from restaurants.models import Restaurant, Table
from reservations.models import Reservation, Notification


def chatbot_page(request):
    return render(request, "chatbot/chatbot.html")


class ChatbotView(View):

    def post(self, request):

        message = request.POST.get("message", "").strip()

        if not message:
            return JsonResponse({
                "response": "Please enter a message."
            })

        message_lower = message.lower()

        # Get current chatbot state
        state = request.session.get("chatbot_state", {})

        # =====================================================
        # RESET / START
        # =====================================================

        if message_lower in ["hi", "hello", "hey", "start", "menu"]:

            request.session["chatbot_state"] = {}

            return JsonResponse({
                "response": """
                    <b>👋 Welcome to DineEase!</b><br><br>
                    I'm your restaurant reservation assistant.
                    <br><br>

                    I can help you with:
                    <br><br>

                    🍽️ <b>Find restaurants</b><br>
                    📅 <b>Make a reservation</b><br>
                    🪑 <b>Check available tables</b><br>
                    📋 <b>View my reservations</b><br>
                    ❌ <b>Cancel a reservation</b>
                """
            })

        # =====================================================
        # SHOW RESTAURANTS
        # =====================================================

        if (
            "restaurant" in message_lower
            and (
                "show" in message_lower
                or "list" in message_lower
                or "find" in message_lower
                or message_lower == "restaurants"
            )
        ):

            restaurants = Restaurant.objects.filter(
                is_active=True
            )

            if not restaurants.exists():

                return JsonResponse({
                    "response":
                        "Sorry, there are no active restaurants available."
                })

            response = "<b>🍽️ Available Restaurants</b><br><br>"

            for restaurant in restaurants:

                response += f"""
                    <div class="restaurant-card">

                        <div class="restaurant-name">
                            🍽️ {restaurant.name}
                        </div>

                        <div class="restaurant-info">

                            📍 {restaurant.address}<br>

                            📞 {restaurant.phone}<br>

                            ✉️ {restaurant.email}<br>

                            🕐 {restaurant.opening_time.strftime("%I:%M %p")}
                            -
                            {restaurant.closing_time.strftime("%I:%M %p")}

                        </div>

                    </div>
                """

            return JsonResponse({
                "response": response
            })

        # =====================================================
        # MY RESERVATIONS
        # =====================================================

        if (
            "my reservation" in message_lower
            or "my reservations" in message_lower
            or "my booking" in message_lower
            or "my bookings" in message_lower
        ):

            if not request.user.is_authenticated:

                return JsonResponse({
                    "response": """
                        🔐 Please <b>login</b> first to view
                        your reservations.
                    """
                })

            reservations = Reservation.objects.filter(
                user=request.user
            ).exclude(
                status="cancelled"
            ).order_by(
                "-reservation_date",
                "-reservation_time"
            )

            if not reservations.exists():

                return JsonResponse({
                    "response":
                        "📋 You don't have any active reservations."
                })

            response = "<b>📋 Your Reservations</b><br><br>"

            for reservation in reservations:

                response += f"""
                    <div class="restaurant-card">

                        <div class="restaurant-name">
                            🍽️ {reservation.restaurant.name}
                        </div>

                        <div class="restaurant-info">

                            📅
                            {reservation.reservation_date.strftime("%d %B %Y")}
                            <br>

                            🕐
                            {reservation.reservation_time.strftime("%I:%M %p")}
                            <br>

                            🪑
                            Table {reservation.table.table_number}
                            <br>

                            👥
                            {reservation.guests} guests
                            <br>

                            📌
                            {reservation.status.title()}

                        </div>

                    </div>
                """

            return JsonResponse({
                "response": response
            })

        # =====================================================
        # CANCEL RESERVATION
        # =====================================================

        if "cancel" in message_lower:

            if not request.user.is_authenticated:

                return JsonResponse({
                    "response":
                        "🔐 Please login before cancelling a reservation."
                })

            reservations = Reservation.objects.filter(
                user=request.user,
                status__in=["pending", "confirmed"]
            ).order_by(
                "reservation_date",
                "reservation_time"
            )

            if not reservations.exists():

                return JsonResponse({
                    "response":
                        "You don't have any reservations that can be cancelled."
                })

            request.session["chatbot_state"] = {
                "stage": "cancel_reservation"
            }

            response = "<b>❌ Which reservation would you like to cancel?</b><br><br>"

            for index, reservation in enumerate(reservations, start=1):

                response += (
                    f"<b>{index}.</b> "
                    f"{reservation.restaurant.name} — "
                    f"{reservation.reservation_date.strftime('%d %b')} "
                    f"at "
                    f"{reservation.reservation_time.strftime('%I:%M %p')}"
                    f"<br>"
                )

            response += (
                "<br>Please type the <b>number</b> of the reservation."
            )

            return JsonResponse({
                "response": response
            })

        # =====================================================
        # CANCEL RESERVATION SELECTION
        # =====================================================

        if state.get("stage") == "cancel_reservation":

            if not request.user.is_authenticated:

                request.session["chatbot_state"] = {}

                return JsonResponse({
                    "response": "Please login first."
                })

            reservations = list(
                Reservation.objects.filter(
                    user=request.user,
                    status__in=["pending", "confirmed"]
                ).order_by(
                    "reservation_date",
                    "reservation_time"
                )
            )

            try:
                selected_number = int(message)
                reservation = reservations[selected_number - 1]

            except (
                ValueError,
                IndexError
            ):

                return JsonResponse({
                    "response":
                        "Please enter a valid reservation number."
                })

            reservation.status = "cancelled"
            reservation.save()

            Notification.objects.create(
                user=request.user,
                message=(
                    f"Your reservation at "
                    f"{reservation.restaurant.name} on "
                    f"{reservation.reservation_date} at "
                    f"{reservation.reservation_time} "
                    f"has been cancelled."
                )
            )

            request.session["chatbot_state"] = {}

            return JsonResponse({
                "response": f"""
                    <b>✅ Reservation cancelled successfully.</b>
                    <br><br>

                    🍽️ {reservation.restaurant.name}<br>
                    📅 {reservation.reservation_date.strftime("%d %B %Y")}<br>
                    🕐 {reservation.reservation_time.strftime("%I:%M %p")}<br><br>

                    Your reservation has been cancelled.
                """
            })

        # =====================================================
        # START RESERVATION
        # =====================================================

        if (
            "book" in message_lower
            or "booking" in message_lower
            or "reservation" in message_lower
            or "reserve" in message_lower
        ):

            if not request.user.is_authenticated:

                return JsonResponse({
                    "response": """
                        🔐 You need to <b>login</b> before
                        making a reservation.
                    """
                })

            restaurants = Restaurant.objects.filter(
                is_active=True
            )

            if not restaurants.exists():

                return JsonResponse({
                    "response":
                        "Sorry, there are no restaurants available."
                })

            request.session["chatbot_state"] = {
                "stage": "restaurant"
            }

            response = (
                "<b>📅 Let's make your reservation!</b>"
                "<br><br>"
                "Which restaurant would you like?"
                "<br><br>"
            )

            for restaurant in restaurants:

                response += (
                    f"🍽️ <b>{restaurant.name}</b><br>"
                )

            return JsonResponse({
                "response": response
            })

        # =====================================================
        # RESERVATION - RESTAURANT
        # =====================================================

        if state.get("stage") == "restaurant":

            restaurant = Restaurant.objects.filter(
                name__icontains=message,
                is_active=True
            ).first()

            if not restaurant:

                return JsonResponse({
                    "response": """
                        ❌ I couldn't find that restaurant.
                        <br><br>
                        Please type the restaurant name exactly
                        as shown in the list.
                    """
                })

            state["restaurant_id"] = restaurant.id
            state["restaurant_name"] = restaurant.name
            state["stage"] = "date"

            request.session["chatbot_state"] = state

            return JsonResponse({
                "response": f"""
                    <b>🍽️ {restaurant.name}</b> selected.
                    <br><br>

                    📅 What date would you like?
                    <br><br>

                    Please use:
                    <b>YYYY-MM-DD</b>
                    <br>

                    Example:
                    <b>2026-10-05</b>
                """
            })

        # =====================================================
        # RESERVATION - DATE
        # =====================================================

        if state.get("stage") == "date":

            try:

                reservation_date = datetime.strptime(
                    message,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return JsonResponse({
                    "response": """
                        ❌ Invalid date.
                        <br><br>
                        Please use:
                        <b>YYYY-MM-DD</b>
                        <br>
                        Example:
                        <b>2026-10-05</b>
                    """
                })

            if reservation_date < timezone.localdate():

                return JsonResponse({
                    "response":
                        "❌ You cannot make a reservation for a past date."
                })

            state["reservation_date"] = str(
                reservation_date
            )

            state["stage"] = "time"

            request.session["chatbot_state"] = state

            return JsonResponse({
                "response": """
                    🕐 What time would you like?
                    <br><br>

                    Please use:
                    <b>HH:MM</b>
                    <br><br>

                    Example:
                    <b>19:00</b>
                """
            })

        # =====================================================
        # RESERVATION - TIME
        # =====================================================

        if state.get("stage") == "time":

            try:

                reservation_time = datetime.strptime(
                    message,
                    "%H:%M"
                ).time()

            except ValueError:

                return JsonResponse({
                    "response": """
                        ❌ Invalid time.
                        <br><br>

                        Please use:
                        <b>HH:MM</b>

                        <br><br>

                        Example:
                        <b>19:00</b>
                    """
                })

            restaurant = Restaurant.objects.get(
                id=state["restaurant_id"]
            )

            if not (
                restaurant.opening_time
                <= reservation_time
                <= restaurant.closing_time
            ):

                return JsonResponse({
                    "response": f"""
                        ❌ The restaurant is open from
                        <b>
                        {restaurant.opening_time.strftime("%I:%M %p")}
                        </b>
                        to
                        <b>
                        {restaurant.closing_time.strftime("%I:%M %p")}
                        </b>.
                        <br><br>
                        Please choose another time.
                    """
                })

            state["reservation_time"] = message
            state["stage"] = "guests"

            request.session["chatbot_state"] = state

            return JsonResponse({
                "response": """
                    👥 How many guests will be attending?
                    <br><br>

                    Example:
                    <b>4</b>
                """
            })

        # =====================================================
        # RESERVATION - GUESTS
        # =====================================================

        if state.get("stage") == "guests":

            try:

                guests = int(message)

            except ValueError:

                return JsonResponse({
                    "response":
                        "❌ Please enter the number of guests. Example: 4"
                })

            if guests <= 0:

                return JsonResponse({
                    "response":
                        "❌ Number of guests must be at least 1."
                })

            restaurant = Restaurant.objects.get(
                id=state["restaurant_id"]
            )

            reservation_date = datetime.strptime(
                state["reservation_date"],
                "%Y-%m-%d"
            ).date()

            reservation_time = datetime.strptime(
                state["reservation_time"],
                "%H:%M"
            ).time()

            # Find tables that are large enough
            tables = Table.objects.filter(
                restaurant=restaurant,
                capacity__gte=guests,
                is_available=True
            )

            available_table = None

            for table in tables:

                already_reserved = Reservation.objects.filter(
                    table=table,
                    reservation_date=reservation_date,
                    reservation_time=reservation_time,
                    status__in=["pending", "confirmed"]
                ).exists()

                if not already_reserved:

                    available_table = table
                    break

            if not available_table:

                state["stage"] = "guests"
                request.session["chatbot_state"] = state

                return JsonResponse({
                    "response": """
                        ❌ Sorry, there is no suitable table
                        available for that date, time and number
                        of guests.
                        <br><br>

                        Please try another time or date.
                    """
                })

            # Store reservation details
            state["guests"] = guests
            state["table_id"] = available_table.id
            state["stage"] = "confirmation"

            request.session["chatbot_state"] = state

            return JsonResponse({
                "response": f"""
                    <b>🎉 Table available!</b>
                    <br><br>

                    <b>Reservation Details</b>
                    <br><br>

                    🍽️ Restaurant:
                    {restaurant.name}
                    <br>

                    📅 Date:
                    {reservation_date.strftime("%d %B %Y")}
                    <br>

                    🕐 Time:
                    {reservation_time.strftime("%I:%M %p")}
                    <br>

                    👥 Guests:
                    {guests}
                    <br>

                    🪑 Table:
                    {available_table.table_number}
                    <br><br>

                    Would you like to confirm this reservation?
                    <br><br>

                    Type <b>YES</b> to confirm.
                    <br>
                    Type <b>NO</b> to cancel.
                """
            })

        # =====================================================
        # CONFIRM RESERVATION
        # =====================================================

        if state.get("stage") == "confirmation":

            if message_lower in ["yes", "y", "confirm", "confirmed"]:

                if not request.user.is_authenticated:

                    request.session["chatbot_state"] = {}

                    return JsonResponse({
                        "response":
                            "Please login before confirming the reservation."
                    })

                restaurant = Restaurant.objects.get(
                    id=state["restaurant_id"]
                )

                table = Table.objects.get(
                    id=state["table_id"]
                )

                reservation_date = datetime.strptime(
                    state["reservation_date"],
                    "%Y-%m-%d"
                ).date()

                reservation_time = datetime.strptime(
                    state["reservation_time"],
                    "%H:%M"
                ).time()

                # Final availability check
                already_reserved = Reservation.objects.filter(
                    table=table,
                    reservation_date=reservation_date,
                    reservation_time=reservation_time,
                    status__in=["pending", "confirmed"]
                ).exists()

                if already_reserved:

                    request.session["chatbot_state"] = {}

                    return JsonResponse({
                        "response": """
                            ❌ Sorry, this table was just
                            reserved by someone else.
                            <br><br>
                            Please start another reservation.
                        """
                    })

                reservation = Reservation.objects.create(
                    user=request.user,
                    restaurant=restaurant,
                    table=table,
                    reservation_date=reservation_date,
                    reservation_time=reservation_time,
                    guests=state["guests"],
                    status="confirmed"
                )

                Notification.objects.create(
                    user=request.user,
                    message=(
                        f"Your reservation at {restaurant.name} "
                        f"for {reservation_date} at "
                        f"{reservation_time} is confirmed."
                    )
                )

                request.session["chatbot_state"] = {}

                return JsonResponse({
                    "response": f"""
                        <b>🎉 Reservation Confirmed!</b>
                        <br><br>

                        🍽️ <b>{restaurant.name}</b><br>

                        📅
                        {reservation_date.strftime("%d %B %Y")}
                        <br>

                        🕐
                        {reservation_time.strftime("%I:%M %p")}
                        <br>

                        👥
                        {state["guests"]} guests
                        <br>

                        🪑
                        Table {table.table_number}
                        <br>

                        📌 Status:
                        <b>Confirmed</b>
                        <br><br>

                        Thank you for choosing
                        <b>DineEase</b>! 😊
                    """
                })

            if message_lower in ["no", "n", "cancel"]:

                request.session["chatbot_state"] = {}

                return JsonResponse({
                    "response": """
                        Reservation cancelled.
                        <br><br>
                        No changes were made to your account.
                        <br><br>
                        Type <b>Hi</b> whenever you want to start again.
                    """
                })

            return JsonResponse({
                "response": """
                    Please type <b>YES</b> to confirm
                    or <b>NO</b> to cancel.
                """
            })

        # =====================================================
        # AVAILABLE TABLES
        # =====================================================

        if (
            "available table" in message_lower
            or "available tables" in message_lower
        ):

            restaurants = Restaurant.objects.filter(
                is_active=True
            )

            request.session["chatbot_state"] = {
                "stage": "table_restaurant"
            }

            response = (
                "<b>🪑 Check Available Tables</b>"
                "<br><br>"
                "Which restaurant?"
                "<br><br>"
            )

            for restaurant in restaurants:

                response += (
                    f"🍽️ {restaurant.name}<br>"
                )

            return JsonResponse({
                "response": response
            })

        # =====================================================
        # TABLE RESTAURANT
        # =====================================================

        if state.get("stage") == "table_restaurant":

            restaurant = Restaurant.objects.filter(
                name__icontains=message,
                is_active=True
            ).first()

            if not restaurant:

                return JsonResponse({
                    "response":
                        "❌ Restaurant not found. Please try again."
                })

            tables = Table.objects.filter(
                restaurant=restaurant,
                is_available=True
            )

            if not tables.exists():

                return JsonResponse({
                    "response":
                        "❌ No tables are currently marked available."
                })

            response = (
                f"<b>🪑 Tables at {restaurant.name}</b>"
                "<br><br>"
            )

            for table in tables:

                response += (
                    f"🪑 Table {table.table_number} "
                    f"— Capacity: {table.capacity}<br>"
                )

            request.session["chatbot_state"] = {}

            return JsonResponse({
                "response": response
            })

        # =====================================================
        # DEFAULT
        # =====================================================

        return JsonResponse({
            "response": """
                🤖 I can help you with:
                <br><br>

                🍽️ <b>Show restaurants</b><br>
                📅 <b>Make a reservation</b><br>
                🪑 <b>Check available tables</b><br>
                📋 <b>Show my reservations</b><br>
                ❌ <b>Cancel my reservation</b>
                <br><br>

                What would you like to do?
            """
        })
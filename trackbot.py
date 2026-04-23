"""
Lost Package Tracking Chatbot - CLI Version
eGain Take-Home Assignment
"""

import random
import re
import time

# ── Mock package database ────────────────────────────────────────────────────

MOCK_PACKAGES = {
    "ORD-1001": {
        "status": "in_transit",
        "carrier": "FedEx",
        "last_location": "Chicago, IL",
        "estimated_delivery": "Tomorrow, Apr 21",
        "tracking_number": "7489234823948",
    },
    "ORD-2002": {
        "status": "delivered",
        "carrier": "UPS",
        "delivered_on": "Apr 18, 2026",
        "delivered_to": "Front door",
        "tracking_number": "1Z999AA10123456784",
    },
    "ORD-3003": {
        "status": "delayed",
        "carrier": "USPS",
        "last_location": "Memphis, TN",
        "reason": "Weather delay",
        "estimated_delivery": "Apr 24, 2026",
        "tracking_number": "9400111899223397910495",
    },
    "ORD-4004": {
        "status": "lost",
        "carrier": "DHL",
        "last_location": "Los Angeles, CA",
        "last_seen": "Apr 10, 2026",
        "tracking_number": "1234567890",
    },
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def slow_print(text, delay=0.018):
    """Print text character by character for a typing effect."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def bot(text):
    """Print a bot message with a prefix."""
    print()
    slow_print(f"  🤖  {text}")


def divider():
    print("\n  " + "─" * 56)


def prompt(question):
    """Show a user input prompt."""
    print()
    return input(f"  You › ").strip()


def validate_order_id(order_id):
    """
    Validate order ID format: must match ORD-XXXX (4 digits).
    Returns (is_valid_format, package_data_or_None)
    """
    # Error handling 1: format check
    pattern = re.compile(r"^ORD-\d{4}$", re.IGNORECASE)
    if not pattern.match(order_id.strip()):
        return False, None

    normalized = order_id.strip().upper()
    package = MOCK_PACKAGES.get(normalized)
    return True, package  # valid format but package may be None (not found)


def normalize_yes_no(answer):
    """
    Error handling 2: handle unexpected yes/no inputs gracefully.
    Returns 'yes', 'no', or 'unknown'.
    """
    answer = answer.lower().strip()
    yes_variants = {"yes", "y", "yeah", "yep", "yup", "sure", "correct", "definitely", "of course", "1"}
    no_variants = {"no", "n", "nope", "nah", "negative", "not really", "0"}

    if answer in yes_variants:
        return "yes"
    if answer in no_variants:
        return "no"
    return "unknown"


def generate_claim_id():
    return f"CLM-{random.randint(10000, 99999)}"


# ── Flow steps ───────────────────────────────────────────────────────────────

def greet():
    divider()
    bot("Hi there! I'm the TrackBot, your package tracking assistant.")
    bot("I can help you locate a lost or delayed package, check delivery")
    bot("status, or file a claim. Let's get started!")


def ask_for_order_id():
    """Ask for order ID with up to 3 retries. Returns package data or None."""
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        bot("Please enter your Order ID (format: ORD-XXXX):")
        order_id = prompt("Order ID")

        if not order_id:
            # Error handling 2: completely empty input
            bot("Hmm, it looks like you didn't enter anything. Let's try again.")
            continue

        valid_format, package = validate_order_id(order_id)

        if not valid_format:
            # Error handling 1: bad format
            remaining = max_attempts - attempt
            if remaining > 0:
                bot(f"That doesn't look like a valid Order ID. It should look like")
                bot(f"ORD-1234. You have {remaining} attempt(s) remaining.")
            else:
                bot("I wasn't able to match that to a valid Order ID format.")
                bot("Please contact support at support@example.com or call 1-800-TRACK-IT.")
                return None
            continue

        if package is None:
            # Valid format but not in system
            remaining = max_attempts - attempt
            if remaining > 0:
                bot(f"I couldn't find Order ID '{order_id.upper()}' in our system.")
                bot(f"Double-check the ID on your confirmation email. {remaining} attempt(s) left.")
            else:
                bot("I still can't locate that order. It may be too new to appear,")
                bot("or there could be a typo. Please reach out to support.")
                return None
            continue

        # Found it!
        bot(f"Got it! I found your order. Let me pull up the details...")
        time.sleep(0.6)
        return package

    return None


def show_status(package):
    """Display package status and route to the right handler."""
    status = package["status"]
    carrier = package["carrier"]
    tracking = package["tracking_number"]

    divider()
    bot(f"Here's what I found:")
    bot(f"  Carrier:         {carrier}")
    bot(f"  Tracking #:      {tracking}")

    if status == "in_transit":
        bot(f"  Status:          📦  In Transit")
        bot(f"  Last seen:       {package['last_location']}")
        bot(f"  Est. delivery:   {package['estimated_delivery']}")
        return handle_in_transit(package)

    elif status == "delivered":
        bot(f"  Status:          ✅  Delivered")
        bot(f"  Delivered on:    {package['delivered_on']}")
        bot(f"  Delivered to:    {package['delivered_to']}")
        return handle_delivered(package)

    elif status in ("delayed", "lost"):
        icon = "⏳" if status == "delayed" else "❓"
        label = "Delayed" if status == "delayed" else "Lost / Missing"
        bot(f"  Status:          {icon}  {label}")
        if status == "delayed":
            bot(f"  Last seen:       {package['last_location']}")
            bot(f"  Reason:          {package.get('reason', 'Unknown')}")
            bot(f"  New est. date:   {package['estimated_delivery']}")
        else:
            bot(f"  Last seen:       {package['last_location']}")
            bot(f"  Last update:     {package.get('last_seen', 'Unknown')}")
        return handle_delayed_or_lost(package)


def handle_in_transit(package):
    bot(f"\nYour package is on its way and should arrive")
    bot(f"{package['estimated_delivery']}. No action needed right now!")
    return ask_anything_else()


def handle_delivered(package):
    bot(f"\nOur records show this package was delivered on {package['delivered_on']}.")

    for attempt in range(3):
        bot("Did you receive it? (yes / no)")
        answer = prompt("Received?")
        result = normalize_yes_no(answer)

        if result == "yes":
            bot("Great! Glad it arrived safely.")
            return ask_anything_else()

        elif result == "no":
            bot("I'm sorry to hear that. I'll file a non-delivery dispute for you.")
            claim_id = generate_claim_id()
            bot(f"Dispute filed! Your claim ID is: {claim_id}")
            bot("Our team will investigate and follow up within 2 business days.")
            bot("You'll receive a confirmation email shortly.")
            return ask_anything_else()

        else:
            # Error handling 2: unexpected response to yes/no question
            remaining = 2 - attempt
            if remaining > 0:
                bot(f"Sorry, I didn't quite catch that. Please reply with 'yes' or 'no'.")
                bot(f"({remaining} attempt(s) left before I offer you other options)")
            else:
                bot("No worries! Let me offer you some options instead:")
                bot("  [1] Yes, I received it — mark as resolved")
                bot("  [2] No, I didn't receive it — file a dispute")
                bot("  [3] I'm not sure — speak to a support agent")
                choice = prompt("Choose 1, 2, or 3")
                if choice == "1":
                    bot("Marked as received. Thanks!")
                elif choice == "2":
                    claim_id = generate_claim_id()
                    bot(f"Dispute filed! Claim ID: {claim_id}")
                else:
                    bot("Connecting you to a support agent... (support@example.com)")
                return ask_anything_else()


def handle_delayed_or_lost(package):
    status = package["status"]

    if status == "delayed":
        bot(f"\nI'm sorry your package is delayed. Here's what you can do:")
    else:
        bot(f"\nI'm sorry — your package appears to be missing. Here's what you can do:")

    bot("  [1] File a claim with the carrier")
    bot("  [2] Contact the carrier directly")
    bot("  [3] Speak to a support agent")

    for attempt in range(3):
        choice = prompt("Choose 1, 2, or 3")

        if choice == "1":
            claim_id = generate_claim_id()
            bot(f"Claim filed successfully! Your claim ID is: {claim_id}")
            bot(f"Carrier: {package['carrier']} will be notified automatically.")
            bot("You'll receive a confirmation email with next steps.")
            return ask_anything_else()

        elif choice == "2":
            carrier_contacts = {
                "FedEx": "1-800-463-3339 / fedex.com",
                "UPS": "1-800-742-5877 / ups.com",
                "USPS": "1-800-275-8777 / usps.com",
                "DHL": "1-800-225-5345 / dhl.com",
            }
            contact = carrier_contacts.get(package["carrier"], "their official website")
            bot(f"You can reach {package['carrier']} at: {contact}")
            bot(f"Have your tracking number ready: {package['tracking_number']}")
            return ask_anything_else()

        elif choice == "3":
            bot("Connecting you to a support agent...")
            bot("Email: support@example.com | Phone: 1-800-TRACK-IT")
            bot("Average wait time: ~5 minutes.")
            return ask_anything_else()

        else:
            # Error handling 2: out-of-range or nonsense input
            remaining = 2 - attempt
            if remaining > 0:
                bot(f"Please enter 1, 2, or 3. ({remaining} attempt(s) remaining)")
            else:
                bot("I'll connect you to a support agent who can assist further.")
                bot("Email: support@example.com | Phone: 1-800-TRACK-IT")
                return ask_anything_else()


def ask_anything_else():
    """Ask if user needs more help; loop back if yes."""
    divider()
    bot("Is there anything else I can help you with today? (yes / no)")

    for attempt in range(3):
        answer = prompt("Another question?")
        result = normalize_yes_no(answer)

        if result == "yes":
            return True   # signal to restart the main loop

        elif result == "no":
            return False  # signal to end

        else:
            # Error handling 2
            if attempt < 2:
                bot("Just say 'yes' or 'no' — do you need help with anything else?")
            else:
                bot("I'll take that as a no. Have a great day!")
                return False

    return False


def farewell():
    divider()
    bot("Thank you for using TrackBot! Have a wonderful day.")
    divider()
    print()


# ── Main loop ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "  " + "═" * 56)
    print("  " + " " * 16 + "T R A C K B O T")
    print("  " + " " * 12 + "Package Tracking Assistant")
    print("  " + "═" * 56)

    greet()

    while True:
        package = ask_for_order_id()

        if package is None:
            # Could not locate package after retries
            bot("I wasn't able to find your package. Please contact support.")
            bot("Email: support@example.com | Phone: 1-800-TRACK-IT")
            divider()
            bot("Would you like to try a different order? (yes / no)")
            answer = prompt("Try again?")
            if normalize_yes_no(answer) != "yes":
                break
            continue

        keep_going = show_status(package)

        if not keep_going:
            break

    farewell()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Session ended. Goodbye!\n")
"""Simple command‑line interface for the subscription manager.

This module provides a text‑based front end for the subscription manager
library. It allows users to add and remove subscriptions, list current
subscriptions, automatically cancel subscriptions due for renewal, renew
cancelled subscriptions and view cost summaries. Dates must be entered in
ISO format (``YYYY‑MM‑DD``).

Run the script directly to start the interactive prompt, e.g.::

    python -m subscription_manager.cli

The underlying logic uses the :class:`subscription_manager.Subscription`
and :class:`subscription_manager.SubscriptionManager` classes. See the
``README.md`` for more details on the subscription management API.
"""

from __future__ import annotations

import datetime
from typing import Optional

from . import Subscription, SubscriptionManager


def parse_date(date_str: str) -> datetime.date:
    """Parse a date string in YYYY‑MM‑DD format into a ``datetime.date``.

    Parameters
    ----------
    date_str: str
        Date string in ISO format (YYYY‑MM‑DD).

    Returns
    -------
    datetime.date
        Parsed date object.

    Raises
    ------
    ValueError
        If the date string is not in the expected format.
    """
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def add_subscription(manager: SubscriptionManager) -> None:
    """Prompt the user to add a new subscription and add it to the manager."""
    name = input("Enter subscription name: ").strip()
    try:
        cost_str = input("Enter monthly cost (e.g. 9.99): ").strip()
        cost = float(cost_str)
    except ValueError:
        print("Invalid cost. Please enter a numeric value.")
        return
    date_input = input("Enter renewal date (YYYY‑MM‑DD): ").strip()
    try:
        renewal_date = parse_date(date_input)
    except ValueError:
        print("Invalid date format. Please use YYYY‑MM‑DD.")
        return
    try:
        manager.add_subscription(Subscription(name=name, cost=cost, renewal_date=renewal_date))
        print(f"Subscription '{name}' added successfully.")
    except ValueError as exc:
        print(exc)


def remove_subscription(manager: SubscriptionManager) -> None:
    """Prompt the user to remove a subscription by name."""
    name = input("Enter subscription name to remove: ").strip()
    try:
        manager.remove_subscription(name)
        print(f"Subscription '{name}' removed.")
    except KeyError:
        print(f"Subscription '{name}' does not exist.")


def list_subscriptions(manager: SubscriptionManager, active_only: bool = False) -> None:
    """Print all subscriptions, optionally filtering to only active ones."""
    subs = manager.list_subscriptions(active_only=active_only)
    if not subs:
        print("No subscriptions found.")
        return
    for sub in subs:
        status = "active" if sub.active else "cancelled"
        print(f"- {sub.name}: ${sub.cost:.2f}/mo, renewal date {sub.renewal_date}, {status}")


def auto_cancel(manager: SubscriptionManager) -> None:
    """Prompt the user for a date and auto‑cancel due subscriptions."""
    date_input = input("Enter today's date (YYYY‑MM‑DD): ").strip()
    try:
        today = parse_date(date_input)
    except ValueError:
        print("Invalid date format. Please use YYYY‑MM‑DD.")
        return
    manager.auto_cancel_subscriptions(today=today)
    print("Subscriptions due for renewal have been cancelled.")


def renew_subscription(manager: SubscriptionManager) -> None:
    """Prompt the user to renew a cancelled subscription."""
    name = input("Enter subscription name to renew: ").strip()
    date_input = input("Enter today's date (YYYY‑MM‑DD): ").strip()
    try:
        today = parse_date(date_input)
    except ValueError:
        print("Invalid date format. Please use YYYY‑MM‑DD.")
        return
    try:
        manager.renew_subscription(name, today=today)
        print(f"Subscription '{name}' renewed. Next renewal date: {manager.get_subscription(name).renewal_date}.")
    except KeyError:
        print(f"Subscription '{name}' does not exist.")


def show_totals(manager: SubscriptionManager) -> None:
    """Display total active monthly cost and total savings from cancelled subscriptions."""
    active_total = manager.total_monthly_cost(active_only=True)
    savings = manager.total_savings()
    print(f"Total monthly cost of active subscriptions: ${active_total:.2f}")
    print(f"Total monthly savings from cancelled subscriptions: ${savings:.2f}")


def main() -> None:
    """Main interactive loop for the CLI."""
    manager = SubscriptionManager()
    actions = {
        "1": ("Add subscription", add_subscription),
        "2": ("Remove subscription", remove_subscription),
        "3": ("List all subscriptions", lambda m: list_subscriptions(m, active_only=False)),
        "4": ("List only active subscriptions", lambda m: list_subscriptions(m, active_only=True)),
        "5": ("Auto cancel due subscriptions", auto_cancel),
        "6": ("Renew a subscription", renew_subscription),
        "7": ("Show totals", show_totals),
        "8": ("Exit", None),
    }
    while True:
        print("\nSubscription Manager CLI")
        for key, (desc, _) in actions.items():
            print(f"{key}. {desc}")
        choice = input("Choose an option: ").strip()
        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please select a valid option.")
            continue
        description, func = action
        if choice == "8":
            print("Goodbye!")
            break
        if func is not None:
            func(manager)


if __name__ == "__main__":
    main()

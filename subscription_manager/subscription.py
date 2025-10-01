"""Subscription and subscription management classes.

This module defines classes to model and manage subscriptions that automatically
cancel at their renewal date. A subscription has a name, cost, renewal date
and a flag indicating whether it is active. The SubscriptionManager class
stores a collection of subscriptions and provides methods to add and remove
subscriptions, automatically cancel subscriptions when they reach their renewal
date, and reactivate (renew) subscriptions on demand.

The design intentionally does not interact with external services. Instead it
provides the core logic needed to build a higher‑level application which
integrates with payment APIs or web automation tools. Unit tests in the
``tests`` directory exercise the expected behaviours.

All dates are expressed as naive ``datetime.date`` instances in UTC. The
SubscriptionManager uses the current date when performing automatic
cancellations unless an override is provided for testing.

"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Subscription:
    """Represents a single subscription.

    Attributes
    ----------
    name: str
        Human‑readable name of the subscription (e.g. ``"Netflix"``).
    cost: float
        Monthly cost of the subscription in USD. Used for savings calculations.
    renewal_date: datetime.date
        The date on which the subscription will renew. Subscriptions renew
        monthly, so this date is updated when the subscription is renewed.
    active: bool
        Whether the subscription is currently active. Inactive subscriptions
        are considered cancelled.
    """

    name: str
    cost: float
    renewal_date: datetime.date
    active: bool = True

    def cancel(self) -> None:
        """Cancel this subscription.

        Cancelling sets ``active`` to False. The renewal date remains
        unchanged so you can still inspect when it was last active.
        """
        self.active = False

    def renew(self, today: Optional[datetime.date] = None) -> None:
        """Renew this subscription.

        Reactivates the subscription and sets its next renewal date to one
        month in the future relative to ``today``. If ``today`` is None the
        current UTC date is used. The concept of "one month" is implemented
        by adding 30 days; this is an approximation but sufficient for the
        purpose of these tests. For more accurate month handling you could
        integrate with ``dateutil.relativedelta``.

        Parameters
        ----------
        today: datetime.date, optional
            Date used as the basis for renewal. Defaults to ``datetime.date.today()``.
        """
        if today is None:
            today = datetime.date.today()
        self.active = True
        # Set the renewal date 30 days ahead of today. In practice months
        # vary in length but this approximation simplifies the logic.
        self.renewal_date = today + datetime.timedelta(days=30)


class SubscriptionManager:
    """Manages a collection of subscriptions.

    The manager stores subscriptions in a dictionary keyed by name and
    exposes methods to add, remove, cancel and renew subscriptions. It also
    provides reporting capabilities for active and cancelled subscriptions
    and computes total costs and savings.
    """

    def __init__(self) -> None:
        self._subscriptions: Dict[str, Subscription] = {}

    def add_subscription(self, subscription: Subscription) -> None:
        """Add a subscription to the manager.

        Raises
        ------
        ValueError
            If a subscription with the same name already exists.
        """
        if subscription.name in self._subscriptions:
            raise ValueError(f"Subscription '{subscription.name}' already exists.")
        self._subscriptions[subscription.name] = subscription

    def remove_subscription(self, name: str) -> None:
        """Remove a subscription by name.

        Raises
        ------
        KeyError
            If no subscription with the given name exists.
        """
        if name not in self._subscriptions:
            raise KeyError(f"Subscription '{name}' does not exist.")
        del self._subscriptions[name]

    def auto_cancel_subscriptions(self, today: Optional[datetime.date] = None) -> None:
        """Automatically cancel subscriptions due to renew today or earlier.

        Iterates over all active subscriptions and cancels those whose
        ``renewal_date`` is less than or equal to ``today``. If ``today`` is
        None the current UTC date is used. Inactive subscriptions are ignored.

        Parameters
        ----------
        today: datetime.date, optional
            Date to treat as the current date. Defaults to ``datetime.date.today()``.
        """
        if today is None:
            today = datetime.date.today()
        for sub in list(self._subscriptions.values()):
            if sub.active and sub.renewal_date <= today:
                sub.cancel()

    def renew_subscription(self, name: str, today: Optional[datetime.date] = None) -> None:
        """Renew a cancelled subscription.

        Reactivates the subscription and sets its next renewal date relative to
        ``today``. Raises ``KeyError`` if the subscription does not exist.

        Parameters
        ----------
        name: str
            Name of the subscription to renew.
        today: datetime.date, optional
            Date used as the basis for renewal. Defaults to ``datetime.date.today()``.
        """
        if name not in self._subscriptions:
            raise KeyError(f"Subscription '{name}' does not exist.")
        self._subscriptions[name].renew(today=today)

    def cancel_subscription(self, name: str) -> None:
        """Manually cancel a subscription by name.

        Raises
        ------
        KeyError
            If no subscription with the given name exists.
        """
        if name not in self._subscriptions:
            raise KeyError(f"Subscription '{name}' does not exist.")
        self._subscriptions[name].cancel()

    def get_subscription(self, name: str) -> Subscription:
        """Return a subscription by name.

        Raises
        ------
        KeyError
            If no subscription with the given name exists.
        """
        if name not in self._subscriptions:
            raise KeyError(f"Subscription '{name}' does not exist.")
        return self._subscriptions[name]

    def list_subscriptions(self, active_only: bool = False) -> List[Subscription]:
        """Return a list of all subscriptions.

        Parameters
        ----------
        active_only: bool, optional
            If True, only return active subscriptions. Defaults to False.

        Returns
        -------
        List[Subscription]
            A list of subscriptions filtered by ``active_only``.
        """
        if active_only:
            return [sub for sub in self._subscriptions.values() if sub.active]
        return list(self._subscriptions.values())

    def total_monthly_cost(self, active_only: bool = True) -> float:
        """Compute the total monthly cost of subscriptions.

        Parameters
        ----------
        active_only: bool, optional
            If True, only include active subscriptions. Defaults to True.

        Returns
        -------
        float
            Sum of the monthly cost of the subscriptions.
        """
        subs = self.list_subscriptions(active_only=active_only)
        return sum(sub.cost for sub in subs)

    def total_savings(self) -> float:
        """Compute the monthly cost saved by cancelled subscriptions.

        Returns
        -------
        float
            Sum of the cost of subscriptions that are not active.
        """
        return sum(sub.cost for sub in self.list_subscriptions() if not sub.active)

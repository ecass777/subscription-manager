"""Top‑level package for the subscription manager.

This package exposes the :class:`Subscription` and :class:`SubscriptionManager`
classes for easy import. It has no side effects when imported.
"""

from .subscription import Subscription, SubscriptionManager  # noqa: F401

__all__ = ["Subscription", "SubscriptionManager"]

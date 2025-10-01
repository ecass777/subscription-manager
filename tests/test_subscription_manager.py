"""Unit tests for the subscription manager package.

These tests verify the core behaviours of the :mod:`subscription_manager`
package: adding, removing and retrieving subscriptions, automatic
cancellation when the renewal date is reached, manual cancellation and
renewal, and summary calculations. Running these tests should give you
confidence that the underlying logic works as expected. They do not test
integration with external systems or user interfaces.
"""

import datetime
import unittest

from subscription_manager import Subscription, SubscriptionManager


class TestSubscription(unittest.TestCase):
    def test_cancel_and_renew(self) -> None:
        today = datetime.date(2025, 1, 1)
        sub = Subscription(name="Netflix", cost=15.0, renewal_date=today)
        self.assertTrue(sub.active)
        sub.cancel()
        self.assertFalse(sub.active)
        # After cancelling we can renew and it should become active again
        sub.renew(today=today)
        self.assertTrue(sub.active)
        # Renewal date should be 30 days ahead of today
        expected_date = today + datetime.timedelta(days=30)
        self.assertEqual(sub.renewal_date, expected_date)


class TestSubscriptionManager(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = SubscriptionManager()
        self.today = datetime.date(2025, 1, 1)

    def test_add_and_get_subscription(self) -> None:
        sub = Subscription(name="Hulu", cost=12.0, renewal_date=self.today)
        self.manager.add_subscription(sub)
        retrieved = self.manager.get_subscription("Hulu")
        self.assertEqual(retrieved.name, "Hulu")
        self.assertEqual(retrieved.cost, 12.0)
        self.assertEqual(retrieved.renewal_date, self.today)

    def test_add_duplicate_raises_value_error(self) -> None:
        sub1 = Subscription(name="Disney", cost=8.0, renewal_date=self.today)
        sub2 = Subscription(name="Disney", cost=9.0, renewal_date=self.today)
        self.manager.add_subscription(sub1)
        with self.assertRaises(ValueError):
            self.manager.add_subscription(sub2)

    def test_remove_subscription(self) -> None:
        sub = Subscription(name="Amazon", cost=10.0, renewal_date=self.today)
        self.manager.add_subscription(sub)
        self.manager.remove_subscription("Amazon")
        # Removing a second time should raise
        with self.assertRaises(KeyError):
            self.manager.remove_subscription("Amazon")

    def test_auto_cancel_subscriptions(self) -> None:
        past_date = self.today - datetime.timedelta(days=1)
        future_date = self.today + datetime.timedelta(days=1)
        sub1 = Subscription(name="PastService", cost=5.0, renewal_date=past_date)
        sub2 = Subscription(name="FutureService", cost=5.0, renewal_date=future_date)
        self.manager.add_subscription(sub1)
        self.manager.add_subscription(sub2)
        # auto cancel should cancel only the past subscription
        self.manager.auto_cancel_subscriptions(today=self.today)
        self.assertFalse(self.manager.get_subscription("PastService").active)
        self.assertTrue(self.manager.get_subscription("FutureService").active)

    def test_renew_subscription(self) -> None:
        past_date = self.today - datetime.timedelta(days=1)
        sub = Subscription(name="OldService", cost=7.0, renewal_date=past_date)
        self.manager.add_subscription(sub)
        # Cancel via auto cancel
        self.manager.auto_cancel_subscriptions(today=self.today)
        self.assertFalse(sub.active)
        # Renew the subscription; should be active again
        self.manager.renew_subscription("OldService", today=self.today)
        self.assertTrue(sub.active)
        expected_date = self.today + datetime.timedelta(days=30)
        self.assertEqual(sub.renewal_date, expected_date)

    def test_total_cost_and_savings(self) -> None:
        past_date = self.today - datetime.timedelta(days=1)
        sub1 = Subscription(name="Cancelled", cost=10.0, renewal_date=past_date)
        sub2 = Subscription(name="Active", cost=20.0, renewal_date=self.today + datetime.timedelta(days=10))
        self.manager.add_subscription(sub1)
        self.manager.add_subscription(sub2)
        # Cancel the first subscription via auto cancel
        self.manager.auto_cancel_subscriptions(today=self.today)
        total_active = self.manager.total_monthly_cost(active_only=True)
        total_all = self.manager.total_monthly_cost(active_only=False)
        savings = self.manager.total_savings()
        self.assertEqual(total_active, 20.0)
        self.assertEqual(total_all, 30.0)
        self.assertEqual(savings, 10.0)


if __name__ == "__main__":
    unittest.main()

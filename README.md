# Subscription Manager

This repository contains a simple subscription management library written in
Python. It models subscriptions with attributes such as name, cost and
renewal date, and provides a `SubscriptionManager` for managing a collection
of subscriptions. The intent is to demonstrate how one might build the core
logic for an app that automatically cancels subscriptions when they reach
their renewal date and allows them to be renewed easily.

## Features

* Add and remove subscriptions by name.
* Automatically cancel subscriptions when their renewal date arrives.
* Manually cancel and renew subscriptions.
* List all subscriptions or only the active ones.
* Compute total monthly cost for active subscriptions and savings from
  cancelled subscriptions.

**Note:** This code does not integrate with external payment APIs or service
providers. It focuses solely on the domain logic; integration would need to be
added separately using appropriate APIs or automation techniques.

## Project Structure

```
.
├── README.md
├── subscription_manager
│    ├── __init__.py
│    ├── cli.py
│    └── subscription.py
└── tests
       └── test_subscription_manager.py
```

* `subscription_manager/subscription.py` contains the `Subscription` and
  `SubscriptionManager` classes.
* `subscription_manager/cli.py` defines a simple command‑line interface
  (CLI) front end. The CLI presents a menu so you can add, remove,
  list, auto‑cancel and renew subscriptions, and view cost summaries without
  writing any Python code yourself.
* `tests/test_subscription_manager.py` holds unit tests that verify the core
  behaviours of the library.

## Running the Tests

This project uses Python’s built‑in `unittest` framework. To run the tests
locally, install a recent version of Python (3.8+ recommended) and then
execute:

```bash
python -m unittest discover -s tests
```

All tests should pass, demonstrating that the subscription manager behaves
correctly for the scenarios covered. You can also run the tests using
`pytest` if you have it installed:

```bash
pytest -q
```

## Running the CLI

This repository includes a simple interactive command‑line interface. To
start the CLI, run the following command from the project root:

```bash
python -m subscription_manager.cli
```

A numbered menu of actions will appear. From this menu you can add new
subscriptions, remove existing ones, list all or only active subscriptions,
automatically cancel any subscriptions whose renewal dates have arrived,
renew a subscription, and show total active cost and savings. Date inputs
should be in ISO format (`YYYY‑MM‑DD`).

## Extending the Prototype

While this library handles the core business logic, a full application would
need to integrate with payment systems or service provider APIs in order to
actually cancel and renew subscriptions in the real world. You might
consider:

* Using a virtual card provider (e.g., Privacy.com, Revolut, or your bank) to
  automatically block recurring charges instead of logging in to each
  streaming service’s website.
* Implementing a user interface (web, mobile or CLI) that calls into the
  `SubscriptionManager` for operations.
* Storing subscription data in a persistent database rather than in memory.

Please note that this repository is intended as an educational example rather
than a production‑ready solution.

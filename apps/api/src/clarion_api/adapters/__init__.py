"""Vendor boundary. Each subpackage defines a Protocol in base.py, an offline
fake in fake.py, real providers in their own module, and a factory in
__init__.py that picks one from settings. Vendor SDK imports stay here."""

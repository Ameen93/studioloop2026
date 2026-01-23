"""Repository layer for data access.

This package provides repository implementations following the Repository Pattern.
Repositories encapsulate database operations and enforce multi-tenancy isolation.

Available base classes:
- BaseRepository: Generic CRUD for platform-scoped models
- GymScopedRepository: Tenant-isolated CRUD for gym-scoped models
"""

from app.repositories.base import BaseRepository, GymScopedRepository

__all__ = [
    "BaseRepository",
    "GymScopedRepository",
]

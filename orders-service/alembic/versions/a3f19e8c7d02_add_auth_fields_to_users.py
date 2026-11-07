"""add auth fields to users (LAB 10 JWT + RBAC)

Revision ID: a3f19e8c7d02
Revises: 291476bcdd84
Create Date: 2026-11-07 13:28:00.000000

Agrega las columnas necesarias para autenticación JWT y control de acceso RBAC
a la tabla 'users':
  - hashed_password: hash bcrypt de la contraseña del usuario
  - role:            nivel de acceso ("user" | "admin" | "superadmin")
  - is_active:       flag para deshabilitar cuentas sin borrarlas
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# ---------------------------------------------------------------------------
# Metadatos de revisión
# ---------------------------------------------------------------------------
revision: str = 'a3f19e8c7d02'
down_revision: Union[str, Sequence[str], None] = '291476bcdd84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica los cambios al esquema (ADD COLUMN idempotente)."""

    # Usamos un bloque de conexión para verificar si las columnas ya existen
    # antes de intentar crearlas (seguridad para re-ejecuciones accidentales)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = {col["name"] for col in inspector.get_columns("users")}

    if "hashed_password" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "hashed_password",
                sa.String(length=255),
                nullable=True,          # nullable para no romper usuarios pre-existentes
                comment="Hash bcrypt de la contraseña del usuario",
            ),
        )

    if "role" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "role",
                sa.String(length=50),
                nullable=False,
                server_default="user",  # valor por defecto a nivel de BD
                comment="Rol RBAC: user | admin | superadmin",
            ),
        )

    if "is_active" not in existing_cols:
        op.add_column(
            "users",
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
                comment="Flag para deshabilitar cuentas sin borrarlas",
            ),
        )


def downgrade() -> None:
    """Revierte los cambios al esquema original."""
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")
    op.drop_column("users", "hashed_password")


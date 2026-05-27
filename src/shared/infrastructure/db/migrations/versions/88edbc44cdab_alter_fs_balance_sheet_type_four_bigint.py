"""alter fs_balance_sheet_type_four bigint columns

Revision ID: 88edbc44cdab
Revises: 377ba4195797
Create Date: 2026-05-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "88edbc44cdab"
down_revision: Union[str, Sequence[str], None] = "377ba4195797"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "fs_balance_sheet_type_four",
        "deposits_from_customers",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        "fs_balance_sheet_type_four",
        "derivatives_and_other_fin_liab",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        "fs_balance_sheet_type_four",
        "entrusted_funds_and_grants",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "fs_balance_sheet_type_four",
        "entrusted_funds_and_grants",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "fs_balance_sheet_type_four",
        "derivatives_and_other_fin_liab",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "fs_balance_sheet_type_four",
        "deposits_from_customers",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )

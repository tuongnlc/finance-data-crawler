from src.shared.domain.base.entity import BaseEntity
import uuid


class CompanyName(BaseEntity):
    stock_id: str
    company_name: str
    business_sector: str
    
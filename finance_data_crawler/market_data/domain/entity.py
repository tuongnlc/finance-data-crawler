from finance_data_crawler.shared.domain.base.entity import BaseEntity
import uuid


class CompanyName(BaseEntity):
    stock_id: str
    company_name: str
    business_sector: str
    
from app.database import SessionLocal
from app.models import Plan

PLANS = [
    {"name": "Free", "price_inr": 0, "monthly_page_limit": 10},
    {"name": "Pro", "price_inr": 499, "monthly_page_limit": 500},
    {"name": "Business", "price_inr": 1499, "monthly_page_limit": 2000},
]

db = SessionLocal()
for p in PLANS:
    if not db.query(Plan).filter_by(name=p["name"]).first():
        db.add(Plan(**p))
db.commit()
db.close()
print("Plans seeded")
import models

from database import SessionLocal
from models.tenant import Tenant


def seed_tenants():
    db = SessionLocal()

    try:
        companies = [
            {"name": "Stackly", "slug": "www.stackly.com",},
            {"name": "Deloitte", "slug": "www.deloitte.com",},
            {"name": "Accenture", "slug": "www.accenture.com",},
        ]

        for company in companies:

            existing_tenant = (
                db.query(Tenant)
                .filter(Tenant.slug == company["slug"])
                .first()
            )

            if existing_tenant:
                print(f"Already exists: {company['name']}")
                continue

            tenant = Tenant(
                name=company["name"],
                slug=company["slug"],
            )

            db.add(tenant)

        db.commit()

        print("\nTenant seeding completed successfully.\n")

        tenants = db.query(Tenant).all()

        for tenant in tenants:
            print(
                f"ID: {tenant.id} | "
                f"Name: {tenant.name} | "
                f"Slug: {tenant.slug}"
            )

    except Exception as exc:
        db.rollback()
        print(f"Error while seeding tenants: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_tenants()
from fastapi import FastAPI
from database import Base, engine

from models import *
from v1.routers import auth, users, tenant, tenant_users, products, product_versions, orders, inventory, inventory_reservations, bookings, sessions, permissions, roles, role_permissions, audit_logs, approvals, webhooks, webhook_retries, idempotency_keys, otp_verifications, scheduled_jobs, external_integrations, job_queue

from v2.routers import auth as v2_auth, users as v2_users, tenants as v2_tenants, products as v2_products, orders as v2_orders, inventory as v2_inventory, audit_logs as v2_audit_logs

app = FastAPI(title="Multi-Tenant API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tenant.router, prefix="/api/v1")
app.include_router(tenant_users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(product_versions.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(inventory_reservations.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(role_permissions.router, prefix="/api/v1")
app.include_router(audit_logs.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(webhook_retries.router, prefix="/api/v1")
app.include_router(idempotency_keys.router, prefix="/api/v1")
app.include_router(otp_verifications.router, prefix="/api/v1")
app.include_router(scheduled_jobs.router, prefix="/api/v1")
app.include_router(external_integrations.router, prefix="/api/v1")
app.include_router(job_queue.router, prefix="/api/v1")

app.include_router(v2_auth.router, prefix="/api/v2")
app.include_router(v2_users.router, prefix="/api/v2")
app.include_router(v2_tenants.router, prefix="/api/v2")
app.include_router(v2_products.router, prefix="/api/v2")
app.include_router(v2_orders.router, prefix="/api/v2")
app.include_router(v2_inventory.router, prefix="/api/v2")
app.include_router(v2_audit_logs.router, prefix="/api/v2")

@app.get("/")
def root():
    return {"message": "Multi-Tenant API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
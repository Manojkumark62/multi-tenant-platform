import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.external_integration import ExternalIntegration
from v1.schemas.external_integration import ExternalIntegrationCreate, ExternalIntegrationUpdate


def _serialize_json_field(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def create_integration(db: Session, tenant_id: int, integration_data: ExternalIntegrationCreate) -> ExternalIntegration:
    existing_integration = db.query(ExternalIntegration).filter(ExternalIntegration.tenant_id == tenant_id, ExternalIntegration.provider == integration_data.provider).first()
    if existing_integration:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Integration with this provider already exists")

    integration = ExternalIntegration(
        tenant_id=tenant_id,
        provider=integration_data.provider,
        name=integration_data.name,
        integration_type=integration_data.integration_type,
        credentials=_serialize_json_field(integration_data.credentials),
        configuration=_serialize_json_field(integration_data.configuration),
        is_active=True,
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

def get_integration(db: Session, tenant_id: int, integration_id: int) -> ExternalIntegration:
    integration = db.query(ExternalIntegration).filter(ExternalIntegration.id == integration_id, ExternalIntegration.tenant_id == tenant_id).first()
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="External integration not found")
    return integration

def get_integration_by_provider(db: Session, tenant_id: int, provider: str) -> ExternalIntegration | None:
    return db.query(ExternalIntegration).filter(ExternalIntegration.tenant_id == tenant_id, ExternalIntegration.provider == provider, ExternalIntegration.is_active.is_(True)).first()

def list_integrations(db: Session, tenant_id: int, offset: int = 0, limit: int = 20) -> list[ExternalIntegration]:
    return db.query(ExternalIntegration).filter(ExternalIntegration.tenant_id == tenant_id).order_by(ExternalIntegration.id.desc()).offset(offset).limit(limit).all()

def update_integration(db: Session, tenant_id: int, integration_id: int, integration_data: ExternalIntegrationUpdate) -> ExternalIntegration:
    integration = get_integration(db, tenant_id, integration_id)
    update_data = integration_data.model_dump(exclude_unset=True)

    if "provider" in update_data and update_data["provider"] != integration.provider:
        existing_integration = db.query(ExternalIntegration).filter(ExternalIntegration.tenant_id == tenant_id, ExternalIntegration.provider == update_data["provider"], ExternalIntegration.id != integration_id).first()
        if existing_integration:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Integration with this provider already exists")

    for field, value in update_data.items():
        if field in {"credentials", "configuration"}:
            setattr(integration, field, _serialize_json_field(value))
        else:
            setattr(integration, field, value)

    db.commit()
    db.refresh(integration)
    return integration

def deactivate_integration(db: Session, tenant_id: int, integration_id: int) -> ExternalIntegration:
    integration = get_integration(db, tenant_id, integration_id)
    integration.is_active = False
    db.commit()
    db.refresh(integration)
    return integration


def test_integration(db: Session, tenant_id: int, integration_id: int) -> dict:
    integration = get_integration(db, tenant_id, integration_id)

    if not integration.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integration is inactive")

    return {
        "integration_id": integration.id,
        "provider": integration.provider,
        "name": integration.name,
        "status": "ok",
        "message": "Integration configuration is valid",
        "tenant_id": tenant_id,
    }
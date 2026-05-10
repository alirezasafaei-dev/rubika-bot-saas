from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import NotFoundError, UnauthorizedError
from app.schemas.webhook import RubikaWebhookPayload, RubikaWebhookResponse
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def get_webhook_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WebhookService:
    return WebhookService(db_session=db)


@router.post(
    "/rubika/{channel_id}",
    response_model=RubikaWebhookResponse,
)
async def rubika_webhook(
    channel_id: int,
    payload: RubikaWebhookPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_webhook_secret: Annotated[str | None, Header(alias="X-Webhook-Secret")] = None,
) -> RubikaWebhookResponse:
    if payload.event_type not in {"message_received", "delivery_result"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported event_type",
        )

    payload_data = payload.model_dump(exclude_none=True)
    try:
        if payload.event_type == "message_received":
            result = await service.process_message_event(
                channel_id=channel_id,
                secret=x_webhook_secret,
                payload=payload_data,
            )
        elif payload.event_type == "delivery_result":
            result = await service.process_delivery_event(
                channel_id=channel_id,
                secret=x_webhook_secret,
                payload=payload_data,
            )
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        ) from exc
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found",
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal processing error",
        ) from exc

    return RubikaWebhookResponse(
        accepted=bool(result["accepted"]),
        reason=result.get("reason") or f"accepted:{payload.event_type}",
    )

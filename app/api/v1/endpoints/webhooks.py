from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import NotFoundError, UnauthorizedError
from app.schemas.webhook import (
    RubikaWebhookAdapterPayload,
    RubikaWebhookResponse,
)
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def get_webhook_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WebhookService:
    return WebhookService(db_session=db)


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _stringified(value: object) -> str | None:
    return str(value) if value is not None else None


def _normalize_rubika_payload(payload: dict[str, object]) -> dict[str, str | None]:
    event_type = payload.get("event_type")
    if event_type in {"message_received", "delivery_result"}:
        return {
            "event_type": str(event_type),
            "message": _optional_str(payload.get("message")),
            "sender_rubika_user_id": _optional_str(
                payload.get("sender_rubika_user_id")
            ),
            "message_id": _stringified(payload.get("message_id")),
            "button_id": _optional_str(payload.get("button_id")),
            "rubika_channel_id": str(
                payload.get("rubika_channel_id")
                or payload.get("chat_id")
                or payload.get("chatId")
            )
            if (
                payload.get("rubika_channel_id") is not None
                or payload.get("chat_id") is not None
                or payload.get("chatId") is not None
            )
            else None,
        }

    update = payload.get("update")
    if isinstance(update, dict):
        raw_event = str(update.get("type", "")).lower()
        if raw_event in {"newmessage", "new_message", "receivemessage", "receivemsg"}:
            new_message = update.get("new_message")
            if not isinstance(new_message, dict):
                new_message = {}
            return {
                "event_type": "message_received",
                "message": _optional_str(new_message.get("text")),
                "sender_rubika_user_id": _optional_str(new_message.get("sender_id")),
                "message_id": _stringified(new_message.get("message_id")),
                "button_id": _optional_str(
                    (
                        new_message.get("aux_data")
                        if isinstance(new_message.get("aux_data"), dict)
                        else {}
                    ).get("button_id")
                ),
                "rubika_channel_id": str(
                    new_message.get("chat_id")
                    or update.get("chat_id")
                    or payload.get("chat_id")
                    or payload.get("chatId")
                )
                if (
                    new_message.get("chat_id") is not None
                    or update.get("chat_id") is not None
                    or payload.get("chat_id") is not None
                    or payload.get("chatId") is not None
                )
                else None,
            }

        if raw_event == "deliveryresult":
            return {
                "event_type": "delivery_result",
                "message": None,
                "sender_rubika_user_id": _optional_str(
                    payload.get("sender_rubika_user_id")
                ),
                "message_id": _stringified(payload.get("message_id")),
                "rubika_channel_id": str(
                    payload.get("chat_id")
                    or payload.get("chatId")
                    or payload.get("rubika_channel_id")
                )
                if (
                    payload.get("chat_id") is not None
                    or payload.get("chatId") is not None
                    or payload.get("rubika_channel_id") is not None
                )
                else None,
            }

    inline_message = payload.get("inline_message")
    if isinstance(inline_message, dict):
        return {
            "event_type": "message_received",
            "message": _optional_str(inline_message.get("text")),
            "sender_rubika_user_id": _optional_str(inline_message.get("sender_id")),
            "message_id": _stringified(inline_message.get("message_id")),
            "button_id": _optional_str(
                (
                    inline_message.get("aux_data")
                    if isinstance(inline_message.get("aux_data"), dict)
                    else {}
                ).get("button_id")
            ),
            "rubika_channel_id": str(
                inline_message.get("chat_id")
                or payload.get("chat_id")
                or payload.get("chatId")
            )
            if (
                inline_message.get("chat_id") is not None
                or payload.get("chat_id") is not None
                or payload.get("chatId") is not None
            )
            else None,
        }

    return {
        "event_type": str(event_type) if event_type else None,
        "message": _optional_str(payload.get("message")),
        "sender_rubika_user_id": _optional_str(payload.get("sender_rubika_user_id")),
        "message_id": _stringified(payload.get("message_id")),
        "button_id": _optional_str(payload.get("button_id")),
        "rubika_channel_id": str(
            payload.get("rubika_channel_id")
            or payload.get("chat_id")
            or payload.get("chatId")
        )
        if (
            payload.get("rubika_channel_id") is not None
            or payload.get("chat_id") is not None
            or payload.get("chatId") is not None
        )
        else None,
    }


def _validate_channel_id(rubika_channel_id: str | None) -> str:
    if not rubika_channel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Rubika channel id",
        )
    return rubika_channel_id


def _validate_event_type(event_type: str | None) -> str:
    if event_type not in {"message_received", "delivery_result"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported event_type",
        )
    return event_type


async def _route_webhook(
    payload: RubikaWebhookAdapterPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_webhook_secret: str | None,
) -> RubikaWebhookResponse:
    normalized = _normalize_rubika_payload(payload.model_dump())
    event_type = _validate_event_type(normalized.get("event_type"))
    rubika_channel_id = _validate_channel_id(normalized.get("rubika_channel_id"))
    payload_data = {
        "event_type": event_type,
        "message": normalized.get("message"),
        "sender_rubika_user_id": normalized.get("sender_rubika_user_id"),
        "message_id": normalized.get("message_id"),
        "button_id": normalized.get("button_id"),
    }

    try:
        if event_type == "message_received":
            result = await service.process_message_event_from_rubika_channel(
                rubika_channel_id=rubika_channel_id,
                secret=x_webhook_secret,
                payload=payload_data,
            )
        else:
            result = await service.process_delivery_event_from_rubika_channel(
                rubika_channel_id=rubika_channel_id,
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
        reason=result.get("reason") or f"accepted:{event_type}",
    )


@router.post("/rubika/{channel_id}", response_model=RubikaWebhookResponse)
async def rubika_webhook_channel(
    channel_id: int,
    payload: RubikaWebhookAdapterPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_webhook_secret: Annotated[str | None, Header(alias="X-Webhook-Secret")] = None,
) -> RubikaWebhookResponse:
    normalized = _normalize_rubika_payload(payload.model_dump())
    event_type = _validate_event_type(normalized.get("event_type"))
    payload_data = {
        "event_type": event_type,
        "message": normalized.get("message"),
        "sender_rubika_user_id": normalized.get("sender_rubika_user_id"),
        "message_id": normalized.get("message_id"),
        "button_id": normalized.get("button_id"),
    }

    try:
        if event_type == "message_received":
            result = await service.process_message_event(
                channel_id=channel_id,
                secret=x_webhook_secret,
                payload=payload_data,
            )
        else:
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
        reason=result.get("reason") or f"accepted:{event_type}",
    )


@router.post("/rubika", response_model=RubikaWebhookResponse)
async def rubika_webhook(
    payload: RubikaWebhookAdapterPayload,
    service: Annotated[WebhookService, Depends(get_webhook_service)],
    x_webhook_secret: Annotated[str | None, Header(alias="X-Webhook-Secret")] = None,
) -> RubikaWebhookResponse:
    return await _route_webhook(
        payload=payload,
        service=service,
        x_webhook_secret=x_webhook_secret,
    )

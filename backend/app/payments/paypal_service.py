from __future__ import annotations

import base64
from typing import Any

import httpx

from app.config import get_settings


class PayPalError(RuntimeError):
    pass


class PayPalService:
    def __init__(self):
        self.settings = get_settings()

    @property
    def live(self) -> bool:
        return (
            not self.settings.demo_mode
            and bool(
                self.settings.paypal_client_id
                and self.settings.paypal_client_secret
            )
        )

    async def get_access_token(self) -> str:
        if not self.live:
            return "DEMO_ACCESS_TOKEN"

        credentials = (
            f"{self.settings.paypal_client_id}:"
            f"{self.settings.paypal_client_secret}"
        )
        encoded_credentials = base64.b64encode(
            credentials.encode()
        ).decode()

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.paypal_base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials"},
            )

        if response.is_error:
            raise PayPalError(
                f"Token request failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json()["access_token"]

    async def create_order(
        self,
        amount: float,
        currency: str = "USD",
    ) -> dict[str, Any]:
        if not self.live:
            return {
                "id": f"DEMO-{int(amount * 100)}",
                "status": "CREATED",
                "intent": "AUTHORIZE",
                "links": [
                    {
                        "rel": "approve",
                        "href": "http://localhost:5173/demo/paypal-approval",
                    }
                ],
            }

        token = await self.get_access_token()

        payload = {
            "intent": "AUTHORIZE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}",
                    },
                    "description": "PayPilot autonomous task",
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "brand_name": "PayPilot",
                        "user_action": "PAY_NOW",
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "shipping_preference": "NO_SHIPPING",
                        "return_url": "http://localhost:5173/paypal/success",
                        "cancel_url": "http://localhost:5173/paypal/cancel",
                    }
                }
            },
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.paypal_base_url}/v2/checkout/orders",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json=payload,
            )

        if response.is_error:
            raise PayPalError(
                f"Create order failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json()

    async def authorize_order(self, order_id: str) -> dict[str, Any]:
        if not self.live:
            return {
                "id": order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "authorizations": [
                                {
                                    "id": f"AUTH-{order_id}",
                                    "status": "CREATED",
                                }
                            ]
                        }
                    }
                ],
            }

        token = await self.get_access_token()

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.paypal_base_url}/v2/checkout/orders/"
                f"{order_id}/authorize",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json={},
            )

        if response.is_error:
            raise PayPalError(
                f"Authorize failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json()

    async def capture_order(self, order_id: str) -> dict[str, Any]:
        if not self.live:
            return {
                "id": order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": f"CAP-{order_id}",
                                    "status": "COMPLETED",
                                }
                            ]
                        }
                    }
                ],
            }

        token = await self.get_access_token()

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.paypal_base_url}/v2/checkout/orders/"
                f"{order_id}/capture",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json={},
            )

        if response.is_error:
            raise PayPalError(
                f"Capture failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json()

    async def verify_webhook(
        self,
        headers: dict[str, str],
        event_body: dict[str, Any],
    ) -> bool:
        if not self.live:
            return True

        token = await self.get_access_token()

        payload = {
            "auth_algo": headers.get("paypal-auth-algo"),
            "cert_url": headers.get("paypal-cert-url"),
            "transmission_id": headers.get("paypal-transmission-id"),
            "transmission_sig": headers.get("paypal-transmission-sig"),
            "transmission_time": headers.get("paypal-transmission-time"),
            "webhook_id": self.settings.paypal_webhook_id,
            "webhook_event": event_body,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.paypal_base_url}/v1/notifications/"
                "verify-webhook-signature",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.is_error:
            raise PayPalError(
                f"Webhook verification failed: "
                f"{response.status_code} {response.text}"
            )

        return response.json().get("verification_status") == "SUCCESS"
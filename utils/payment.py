import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional

# Настройка логирования
payment_logger = logging.getLogger('payment')
payment_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/payments.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
payment_logger.addHandler(file_handler)

class PaymentService:
    def __init__(self):
        self.api_key = os.getenv('WATA_API_KEY')
        self.base_url = 'https://api.wata.pro/api/h2h'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    async def create_payment_link(
        self,
        amount: float,
        currency: str = 'RUB',
        description: str = '',
        order_id: str = '',
        success_url: str = '',
        fail_url: str = '',
        expiration_hours: int = 24
    ) -> Optional[str]:
        try:
            expiration_time = (datetime.utcnow() + timedelta(hours=expiration_hours)).isoformat() + 'Z'
            
            payload = {
                'amount': amount,
                'currency': currency,
                'description': description,
                'orderId': order_id,
                'successRedirectUrl': success_url,
                'failRedirectUrl': fail_url,
                'expirationDateTime': expiration_time
            }

            response = requests.post(
                f'{self.base_url}/links',
                headers=self.headers,
                json=payload
            )

            if response.status_code == 200:
                payment_data = response.json()
                payment_logger.info(f'Created payment link: {json.dumps(payment_data)}')
                return payment_data.get('url')
            else:
                payment_logger.error(f'Failed to create payment link: {response.text}')
                return None

        except Exception as e:
            payment_logger.error(f'Error creating payment link: {str(e)}')
            return None

    async def check_payment_status(self, order_id: str) -> Optional[dict]:
        try:
            response = requests.get(
                f'{self.base_url}/links',
                headers=self.headers,
                params={'orderId': order_id}
            )

            if response.status_code == 200:
                payment_data = response.json()
                payment_logger.info(f'Payment status checked: {json.dumps(payment_data)}')
                items = payment_data.get('items', [])
                if not items:
                    return {'status': 'NOT_FOUND'}
                item = items[0]
                # Если статус не Opened, считаем что оплата прошла
                if item.get('status') != 'Opened':
                    return {'status': 'SUCCESS', 'item': item}
                else:
                    return {'status': 'OPENED', 'item': item}
            else:
                payment_logger.error(f'Failed to check payment status: {response.text}')
                return None

        except Exception as e:
            payment_logger.error(f'Error checking payment status: {str(e)}')
            return None

    async def close_payment_link(self, order_id: str) -> bool:
        try:
            # Получаем id ссылки по orderId
            response = requests.get(
                f'{self.base_url}/links',
                headers=self.headers,
                params={'orderId': order_id}
            )
            if response.status_code == 200:
                items = response.json().get('items', [])
                if not items:
                    return False
                link_id = items[0]['id']
                # Закрываем ссылку
                close_resp = requests.post(
                    f'{self.base_url}/links/{link_id}/close',
                    headers=self.headers
                )
                return close_resp.status_code == 200
            return False
        except Exception as e:
            payment_logger.error(f'Error closing payment link: {str(e)}')
            return False 
from log.schema import BaseJsonLogSchema, ResponseJsonLogSchema, RequestJsonLogSchema, Service
from starlette.middleware.base import RequestResponseEndpoint
from fastapi import Request, Response
from starlette.types import Message
import datetime
import time
import http
import math
import json


class LoggingMiddleware:
    """
    Middleware для обработки запросов и ответов с целью журналирования
    """
    service_id = None
    service_name = None
    service_version = None

    def __init__(self, logger, service_name, service_id, service_version):
        self.logger = logger
        self.service_id = service_id
        self.service_name = service_name
        self.service_version = service_version

    @staticmethod
    async def set_body(request: Request, body: bytes) -> None:
        async def receive() -> Message:
            return {'type': 'http.request', 'body': body}

        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def __call__(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
            *args,
            **kwargs
    ):
        start_time = time.time()
        now = datetime.datetime.fromtimestamp(
            start_time
        ).astimezone().replace(
            microsecond=0
        ).isoformat()
        exception_object = None

        # Request Side
        try:
            if request.headers.get('content-type', None) == 'application/json' \
                    or \
               request.headers.get('accept', None) == 'application/json':
                request_body = await request.body()
            else:
                request_body = 'default content'
        except Exception as e:
            request_body = None
            pass
        request_headers: dict = dict(request.headers.items())

        # Response Side
        try:
            response = await call_next(request)
        except Exception as ex:
            response_body = bytes(
                http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase.encode()
            )
            response_body_log = response_body
            response = Response(
                content=response_body,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR.real,
            )
            exception_object = ex
            response_headers = {}
        else:
            response_headers = dict(response.headers.items())

            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk

            if response.headers.get('content-type', None) == 'application/json':
                response_body_log = response_body
            else:
                response_body_log = b'default content'

            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type
            )

        status_code = response.status_code
        duration: int = math.ceil((time.time() - start_time) * 1000)
        message = f'{"Ошибка" if exception_object else "Ответ"} ' \
                  f'с кодом {status_code} ' \
                  f'на запрос {request.method} \"{str(request.url)}\", ' \
                  f'за {duration} мс'

        request_json_fields = BaseJsonLogSchema(
            service=Service(
                id=self.service_id,
                name=self.service_name,
                version=self.service_version
            ),
            request=RequestJsonLogSchema(
                method=request.method,
                uri=str(request.url),
                path=request.url.path,
                query=str(request.query_params),
                body=request_body,
                size=int(request_headers.get('content-length', 0)),
                headers=json.dumps(request_headers),
                cookie=json.dumps(request.cookies),
                remote_ip=request.client[0],
                remote_port=request.client[1],
            ),
            response=ResponseJsonLogSchema(
                status_code=status_code,
                body=response_body_log.decode(),
                header=json.dumps(response_headers),
                size=int(response_headers.get('content-length', 0))
            ),
            duration=duration,
            timestamp=now
        ).dict(
            exclude_unset=True,
            by_alias=True,
        )

        self.logger.info(
            message,
            extra={
                'request_json_fields': request_json_fields,
                'to_mask': True,
            },
            exc_info=exception_object
        )
        return response

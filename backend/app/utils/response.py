from fastapi.responses import JSONResponse
from typing import Any
from datetime import datetime, date
import json


class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=self._serialize,
        ).encode("utf-8")

    @staticmethod
    def _serialize(obj: Any) -> str:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def success(data: Any = None, msg: str = "success") -> CustomJSONResponse:
    return CustomJSONResponse(content={"code": 200, "msg": msg, "data": data})


def error(msg: str = "error", code: int = 400, data: Any = None) -> CustomJSONResponse:
    return CustomJSONResponse(
        status_code=code if code >= 100 else 400,
        content={"code": code, "msg": msg, "data": data},
    )


def unauthorized(msg: str = "未登录或登录已过期") -> CustomJSONResponse:
    return CustomJSONResponse(
        status_code=401,
        content={"code": 401, "msg": msg, "data": None},
    )


def forbidden(msg: str = "权限不足") -> CustomJSONResponse:
    return CustomJSONResponse(
        status_code=403,
        content={"code": 403, "msg": msg, "data": None},
    )

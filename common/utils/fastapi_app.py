# common/utils/fastapi_app.py
import os
import warnings
from typing import Iterable, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

ALLOWED_ORIGINS_DEFAULT = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api.alluresallol.com",
    "https://alluresallol.com",
    "https://allures-frontend.vercel.app",
]

def use_root_path(service_name: str, env_var: Optional[str] = None) -> bool:
    key = env_var or f"{service_name.upper()}_USE_ROOT_PATH"
    return os.getenv(key, "0") == "1"

# ✅ РЕКОМЕНДОВАНО: использовать это
def create_service_app(service_name: str, title_suffix: str = "Service") -> FastAPI:
    use_root = use_root_path(service_name)
    root = f"/{service_name.lower()}" if use_root else ""
    return FastAPI(
        title=f"{service_name.capitalize()} {title_suffix}",
        root_path=root,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

# ⚠️ УСТАРЕВШЕ: оставить временно для обратной совместимости
def create_app(service_name: str) -> FastAPI:
    warnings.warn(
        "create_app() устарел; используйте create_service_app(). "
        "Функция будет удалена после миграции всех сервисов.",
        DeprecationWarning,
        stacklevel=2,
    )
    return create_service_app(service_name)

def add_cors(
    app: FastAPI,
    *,
    allow_origins: Optional[Iterable[str]] = None,
    allow_origin_regex: Optional[str] = r"https://.*-allures-frontend-.*\.vercel\.app",
    allow_credentials: bool = False,
) -> None:
    origins = list(allow_origins) if allow_origins else ALLOWED_ORIGINS_DEFAULT
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def include_router_with_prefix(
    app: FastAPI,
    router: APIRouter,
    *,
    service_name: str,
    resource_prefix: str,
    tags: Optional[list[str]] = None,
    env_var: Optional[str] = None,
) -> None:
    use_root = use_root_path(service_name, env_var=env_var)
    if use_root:
        app.include_router(router, tags=tags or [])
    else:
        app.include_router(router, prefix=resource_prefix, tags=tags or [])

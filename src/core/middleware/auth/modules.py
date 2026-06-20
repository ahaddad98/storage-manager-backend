from typing import Annotated

from fastapi import Depends, HTTPException, status

from core.middleware.auth.tenant import TenantContext, get_tenant_context


def require_enabled_module(module_key: str):
    async def checker(
        tenant: Annotated[TenantContext, Depends(get_tenant_context)],
    ) -> TenantContext:
        if tenant.has_module(module_key):
            return tenant
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Module '{module_key}' is not enabled for this organization",
        )

    return checker

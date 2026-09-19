from uuid import UUID
from typing import Any

from fastapi import (APIRouter,Depends,status,)

from app.auth.dependencies import (RequireRole,get_current_user,)

from app.auth.enums import Role

from app.shared.schemas import (PaginationParams,PagedResponse,SortParams,)

from app.vendors.dependencies import (get_vendor_service,)

from app.vendors.schemas import (VendorCreateRequest,VendorUpdateRequest,VendorResponse,VendorFilters,ClientCreateRequest,ClientUpdateRequest,ClientResponse,ClientFilters,)

from app.vendors.service import VendorService


router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"],
)

# ==========================================
# Vendor Endpoints
# ==========================================

@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def create_vendor(
    payload: VendorCreateRequest,
    service: VendorService = Depends(
        get_vendor_service
    ),
    current_user: Any = Depends(
        get_current_user
    ),
) -> Any:
    """
    Registers a new Vendor together with any
    initial contact records.
    """

    return await service.create_vendor(
        payload,
        current_user.id,
    )

@router.get(
    "",
    response_model=PagedResponse[VendorResponse],
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def list_vendors(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: VendorFilters = Depends(),
    service: VendorService = Depends(
        get_vendor_service
    ),
) -> Any:
    """
    Returns paginated Vendor records.
    """

    records, metadata = await service.list_vendors(
        pagination,
        sort,
        filters,
    )

    return {
        "data": records,
        "pagination": metadata,
    }

# ==========================================
# Client Endpoints
# ==========================================

@router.post(
    "/clients",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def create_client(
    payload: ClientCreateRequest,
    service: VendorService = Depends(
        get_vendor_service,
    ),
    current_user: Any = Depends(
        get_current_user,
    ),
) -> Any:
    """
    Creates a Client beneath an existing Vendor.
    """

    return await service.create_client(
        payload,
        current_user.id,
    )

@router.get(
    "/clients",
    response_model=PagedResponse[ClientResponse],
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def list_clients(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    filters: ClientFilters = Depends(),
    service: VendorService = Depends(
        get_vendor_service,
    ),
) -> Any:
    """
    Returns paginated Client records.
    """

    records, metadata = await service.list_clients(
        pagination,
        sort,
        filters,
    )

    return {
        "data": records,
        "pagination": metadata,
    }


@router.get(
    "/clients/{public_id}",
    response_model=ClientResponse,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def get_client(
    public_id: UUID,
    service: VendorService = Depends(
        get_vendor_service,
    ),
) -> Any:
    """
    Returns a Client record.
    """

    return await service.get_client(
        public_id,
    )

@router.patch(
    "/clients/{public_id}",
    response_model=ClientResponse,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def update_client(
    public_id: UUID,
    payload: ClientUpdateRequest,
    service: VendorService = Depends(
        get_vendor_service,
    ),
    current_user: Any = Depends(
        get_current_user,
    ),
) -> Any:
    """
    Updates an existing Client.
    """

    return await service.update_client(
        public_id,
        payload,
        current_user.id,
    )


@router.delete(
    "/clients/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                ]
            )
        )
    ],
)
async def archive_client(
    public_id: UUID,
    service: VendorService = Depends(
        get_vendor_service,
    ),
    current_user: Any = Depends(
        get_current_user,
    ),
) -> None:
    """
    Archives a Client.
    """

    await service.archive_client(
        public_id,
        current_user.id,
    )


@router.get(
    "/{public_id}",
    response_model=VendorResponse,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def get_vendor(
    public_id: UUID,
    service: VendorService = Depends(
        get_vendor_service
    ),
) -> Any:
    """
    Returns a Vendor aggregate.
    """

    return await service.get_vendor(
        public_id
    )

@router.patch(
    "/{public_id}",
    response_model=VendorResponse,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                    Role.RECRUITER,
                ]
            )
        )
    ],
)
async def update_vendor(
    public_id: UUID,
    payload: VendorUpdateRequest,
    service: VendorService = Depends(
        get_vendor_service
    ),
    current_user: Any = Depends(
        get_current_user
    ),
) -> Any:
    """
    Updates an existing Vendor.
    """

    return await service.update_vendor(
        public_id,
        payload,
        current_user.id,
    )

@router.delete(
    "/{public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            RequireRole(
                [
                    Role.ADMIN,
                    Role.MANAGER,
                ]
            )
        )
    ],
)
async def archive_vendor(
    public_id: UUID,
    service: VendorService = Depends(
        get_vendor_service
    ),
    current_user = Depends(get_current_user),
) -> None:
    """
    Archives a Vendor.
    """

    await service.archive_vendor(
        public_id=public_id,
        current_user_id=current_user.id,
    )

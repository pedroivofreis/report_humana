from fastapi import APIRouter, Depends

from app.api.dependencies.authentication import get_current_user
from app.api.routers.address import router as address_router
from app.api.routers.addresses import router as addresses_router
from app.api.routers.attachment import router as attachment_router
from app.api.routers.auth import router as auth_router
from app.api.routers.bank_account import router as bank_account_router
from app.api.routers.complementary_data import router as complementary_data_router
from app.api.routers.health_check import router as health_check_router
from app.api.routers.institution_contracts import router as institution_contracts_router
from app.api.routers.institutions import router as institutions_router
from app.api.routers.pix_key import router as pix_key_router
from app.api.routers.profession import router as profession_router
from app.api.routers.professional_crm import router as professional_crm_router
from app.api.routers.role import router as role_router
from app.api.routers.sectors import router as sectors_router
from app.api.routers.shift_types import router as shift_types_router
from app.api.routers.shifts import router as shifts_router
from app.api.routers.specialty import router as specialty_router
from app.api.routers.user import router as user_router
from app.api.routers.user_absence import router as user_absence_router
from app.api.routers.user_shifts import router as user_shifts_router
from app.api.routers.user_specialty import router as user_specialty_router
from app.api.routers.user_timesheets import router as user_timesheets_router
from app.api.routers.user_observation import router as user_observation_router
from app.api.routers.professional_location_binding import router as professional_location_binding_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    institution_contracts_router,
    prefix="/institution-contracts",
    tags=["institution-contracts"],
)

api_router.include_router(
    health_check_router,
    prefix="/health-check",
    tags=["health-check"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    institutions_router,
    prefix="/institutions",
    tags=["institutions"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    addresses_router,
    prefix="/addresses",
    tags=["addresses"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    sectors_router,
    prefix="/sectors",
    tags=["sectors"],
    # dependencies=[Depends(get_current_user)],
)


api_router.include_router(
    user_router,
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    role_router,
    prefix="/roles",
    tags=["roles"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    complementary_data_router,
    prefix="/users/{user_id}/complementary-data",
    tags=["complementary-data"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    address_router,
    prefix="/addresses",
    tags=["addresses"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    attachment_router,
    prefix="/attachments",
    tags=["attachments"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    bank_account_router,
    prefix="/bank-accounts",
    tags=["bank-accounts"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    profession_router,
    prefix="/professions",
    tags=["professions"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    specialty_router,
    prefix="/specialties",
    tags=["specialties"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    user_specialty_router,
    prefix="/user-specialties",
    tags=["user-specialties"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    pix_key_router,
    prefix="/pix-keys",
    tags=["pix-keys"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    shifts_router,
    prefix="/shifts",
    tags=["shifts"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    user_shifts_router,
    prefix="/user-shifts",
    tags=["user-shifts"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    user_timesheets_router,
    prefix="/user-timesheets",
    tags=["user-timesheets"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    shift_types_router,
    prefix="/shift-types",
    tags=["shift-types"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    user_absence_router,
    prefix="/user-absences",
    tags=["user-absences"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    professional_crm_router,
    prefix="/professional-crms",
    tags=["professional-crms"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    user_observation_router,
    prefix="/user-observations",
    tags=["user-observations"],
    # dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    professional_location_binding_router,
    prefix="/professional-location-bindings",
    tags=["professional-location-bindings"],
    # dependencies=[Depends(get_current_user)],
)

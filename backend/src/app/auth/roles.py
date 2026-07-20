from app.auth.enums import Role


ADMIN_ROLES = {
    Role.ADMIN,
}

MANAGEMENT_ROLES = {
    Role.ADMIN,
    Role.MANAGER,
}

RECRUITER_ROLES = {
    Role.ADMIN,
    Role.MANAGER,
    Role.BENCH_SALES_RECRUITER,
}
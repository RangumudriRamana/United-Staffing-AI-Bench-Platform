from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    RECRUITER = "RECRUITER"
    BENCH_SALES_RECRUITER = "BENCH_SALES_RECRUITER"
    USER = "USER"

# Alias Role to UserRole to satisfy dependencies looking for either name
Role = UserRole
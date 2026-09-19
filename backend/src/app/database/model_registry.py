"""
Central model registry.

Import every SQLAlchemy model here so that Base.metadata
contains every table before Alembic autogenerates migrations.
"""

# Existing User model
from app.models.user import User
from app.auth.models import AuthSession

# Feature modules
from app.consultants import models as consultants_models
from app.vendors import models as vendors_models
from app.requirements import models as requirements_models
from app.submissions import models as submissions_models
from app.analytics import models as analytics_models
from app.audit import models as audit_models
from app.automation import models as automation_models
from app.communications import models as communications_models
from app.notifications import models as notifications_models
from app.reporting import models as reporting_models
from app.tasks import models as tasks_models
from app.integrations import models as integrations_models
from app.ai_matching import models as ai_matching_models
from app.marketing import models as marketing_models

__all__ = [
    "User",
    "AuthSession",
]
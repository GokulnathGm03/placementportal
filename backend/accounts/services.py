from students.models import StudentProfile

PLACEMENT_INCHARGE_GROUP_NAME = "Placement Incharge"

ROLE_ANONYMOUS = "ANONYMOUS"
ROLE_PLACEMENT_INCHARGE = "PLACEMENT_INCHARGE"
ROLE_STUDENT = "STUDENT"
ROLE_STAFF = "STAFF"
ROLE_USER = "USER"


def is_placement_incharge(user) -> bool:
    """
    Returns True only for an authenticated superuser or a user belonging
    to the 'Placement Incharge' group.
    is_staff alone does not grant Placement Incharge status.
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    return bool(
        getattr(user, 'is_superuser', False)
        or user.groups.filter(name=PLACEMENT_INCHARGE_GROUP_NAME).exists()
    )


def get_user_role(user) -> str:
    """
    Returns the application-level role for a given user.
    Precedence order:
      1. Anonymous / None / Unauthenticated -> 'ANONYMOUS'
      2. Superuser / Placement Incharge Group -> 'PLACEMENT_INCHARGE'
      3. User with StudentProfile -> 'STUDENT'
      4. Staff user (without Incharge group) -> 'STAFF'
      5. Ordinary authenticated user -> 'USER'
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return ROLE_ANONYMOUS

    if is_placement_incharge(user):
        return ROLE_PLACEMENT_INCHARGE

    if hasattr(user, 'student_profile'):
        try:
            if user.student_profile is not None:
                return ROLE_STUDENT
        except StudentProfile.DoesNotExist:
            pass

    if getattr(user, 'is_staff', False):
        return ROLE_STAFF

    return ROLE_USER

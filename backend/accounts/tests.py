from importlib import import_module
from decimal import Decimal
from django.contrib.auth.models import AnonymousUser, Group, User
from django.db import migrations
from django.test import TestCase
from accounts.services import (
    PLACEMENT_INCHARGE_GROUP_NAME,
    ROLE_ANONYMOUS,
    ROLE_PLACEMENT_INCHARGE,
    ROLE_STAFF,
    ROLE_STUDENT,
    ROLE_USER,
    get_user_role,
    is_placement_incharge,
)
from students.models import StudentProfile


class PlacementInchargeRoleTests(TestCase):
    def setUp(self):
        self.incharge_group = Group.objects.get(name=PLACEMENT_INCHARGE_GROUP_NAME)

    def test_placement_incharge_group_seeded_by_migration(self):
        """Verify the 'Placement Incharge' group was created by the initial migration."""
        self.assertTrue(
            Group.objects.filter(name=PLACEMENT_INCHARGE_GROUP_NAME).exists()
        )

    def test_migration_reverse_operation_is_noop(self):
        """Verify the migration's reverse_code is non-destructive (noop)."""
        migration_module = import_module('accounts.migrations.0001_initial')
        migration = migration_module.Migration('0001_initial', 'accounts')
        self.assertEqual(len(migration.operations), 1)
        operation = migration.operations[0]
        self.assertIsInstance(operation, migrations.RunPython)
        self.assertIs(operation.reverse_code, migrations.RunPython.noop)

    def test_group_member_gets_placement_incharge_role(self):
        """A user in 'Placement Incharge' group has incharge status and role."""
        user = User.objects.create_user(
            username='incharge_user',
            email='incharge@example.com',
            password='password123'
        )
        user.groups.add(self.incharge_group)

        self.assertTrue(is_placement_incharge(user))
        self.assertEqual(get_user_role(user), ROLE_PLACEMENT_INCHARGE)

    def test_superuser_gets_placement_incharge_role(self):
        """A superuser has incharge status and role even without explicit group membership."""
        superuser = User.objects.create_superuser(
            username='admin_user',
            email='admin@example.com',
            password='password123'
        )

        self.assertTrue(is_placement_incharge(superuser))
        self.assertEqual(get_user_role(superuser), ROLE_PLACEMENT_INCHARGE)

    def test_staff_user_without_group_is_not_placement_incharge(self):
        """A staff user without group membership must NOT get PLACEMENT_INCHARGE."""
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )

        self.assertFalse(is_placement_incharge(staff_user))
        self.assertEqual(get_user_role(staff_user), ROLE_STAFF)
        self.assertNotEqual(get_user_role(staff_user), ROLE_PLACEMENT_INCHARGE)

    def test_student_gets_student_role(self):
        """A user with an associated StudentProfile gets STUDENT role."""
        student_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='password123'
        )
        StudentProfile.objects.create(
            user=student_user,
            full_name="Jane Doe",
            registration_number="REG99999",
            college_code="ENG01",
            roll_number="21CS099",
            department="Computer Science",
            batch="2021-2025",
            cgpa=Decimal("8.50"),
            history_of_arrears=0,
            standing_arrears=0,
            verification_status="PENDING"
        )

        self.assertFalse(is_placement_incharge(student_user))
        self.assertEqual(get_user_role(student_user), ROLE_STUDENT)

    def test_ordinary_authenticated_user_gets_user_role(self):
        """An ordinary authenticated user gets USER role."""
        user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='password123'
        )

        self.assertFalse(is_placement_incharge(user))
        self.assertEqual(get_user_role(user), ROLE_USER)

    def test_anonymous_user_returns_anonymous_role(self):
        """AnonymousUser instance returns False for incharge and ANONYMOUS role."""
        anon = AnonymousUser()

        self.assertFalse(is_placement_incharge(anon))
        self.assertEqual(get_user_role(anon), ROLE_ANONYMOUS)

    def test_none_user_returns_anonymous_role(self):
        """Passing None safely returns False for incharge and ANONYMOUS role."""
        self.assertFalse(is_placement_incharge(None))
        self.assertEqual(get_user_role(None), ROLE_ANONYMOUS)

    def test_role_precedence_incharge_over_student(self):
        """Incharge role takes precedence over student profile if user has both."""
        dual_user = User.objects.create_user(
            username='dual_user',
            email='dual@example.com',
            password='password123'
        )
        dual_user.groups.add(self.incharge_group)
        StudentProfile.objects.create(
            user=dual_user,
            full_name="Dual User",
            registration_number="REG88888",
            college_code="ENG01",
            roll_number="21CS088",
            department="Computer Science",
            batch="2021-2025",
            verification_status="PENDING"
        )

        self.assertTrue(is_placement_incharge(dual_user))
        self.assertEqual(get_user_role(dual_user), ROLE_PLACEMENT_INCHARGE)

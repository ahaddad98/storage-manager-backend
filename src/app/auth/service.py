import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schema import (
    AcceptInvitationRequest,
    AuthMeResponse,
    InviteStaffRequest,
    LoginRequest,
    MembershipInfo,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.clinics.model import Clinic
from app.organizations.model import Organization
from app.staff.model import ClinicAssignment, Membership
from app.users.model import User
from core.business_modules import normalize_business_type, resolve_enabled_modules
from core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from core.middleware.auth.exceptions import create_access_token, hash_password, verify_password
from core.middleware.auth.permission_list import Role
from core.middleware.auth.role_list import ROLE_PERMISSIONS


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing = await self.session.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ConflictException("Email already registered")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
        )
        self.session.add(user)
        await self.session.flush()

        org = Organization(name=data.organization_name)
        self.session.add(org)
        await self.session.flush()

        membership = Membership(
            user_id=user.id,
            organization_id=org.id,
            role="owner",
            status="active",
            joined_at=datetime.now(timezone.utc),
        )
        self.session.add(membership)
        await self.session.flush()

        clinic = Clinic(
            organization_id=org.id,
            name=f"{data.organization_name} - Main",
            status="active",
        )
        self.session.add(clinic)
        await self.session.flush()

        assignment = ClinicAssignment(
            membership_id=membership.id,
            organization_id=org.id,
            clinic_id=clinic.id,
        )
        self.session.add(assignment)
        await self.session.flush()

        token = create_access_token(
            user.id,
            role="owner",
            extra={"organization_id": str(org.id)},
        )
        return TokenResponse(access_token=token)

    async def login(self, data: LoginRequest) -> TokenResponse:
        result = await self.session.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        membership_result = await self.session.execute(
            select(Membership)
            .where(Membership.user_id == user.id, Membership.status == "active")
            .limit(1)
        )
        membership = membership_result.scalar_one_or_none()
        if not membership:
            raise UnauthorizedException("No active organization membership")

        user.last_active = datetime.now(timezone.utc)
        await self.session.flush()

        token = create_access_token(
            user.id,
            role=membership.role,
            extra={"organization_id": str(membership.organization_id)},
        )
        return TokenResponse(access_token=token)

    async def get_me(self, user_id: UUID, organization_id: UUID) -> AuthMeResponse:
        user_result = await self.session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")

        membership_result = await self.session.execute(
            select(Membership, Organization)
            .join(Organization, Membership.organization_id == Organization.id)
            .where(
                Membership.user_id == user_id,
                Membership.organization_id == organization_id,
            )
        )
        row = membership_result.first()
        if not row:
            raise NotFoundException("Membership not found")
        membership, org = row

        if membership.role in {Role.OWNER, Role.ADMIN}:
            assignments_result = await self.session.execute(
                select(Clinic.id).where(
                    Clinic.organization_id == org.id,
                    Clinic.deleted_on.is_(None),
                )
            )
        else:
            assignments_result = await self.session.execute(
                select(ClinicAssignment.clinic_id)
                .join(Clinic, ClinicAssignment.clinic_id == Clinic.id)
                .where(
                    ClinicAssignment.membership_id == membership.id,
                    ClinicAssignment.organization_id == org.id,
                    Clinic.organization_id == org.id,
                    Clinic.deleted_on.is_(None),
                )
            )
        clinic_ids = [row[0] for row in assignments_result.all()]
        business_type = normalize_business_type(org.business_type)
        enabled_modules = resolve_enabled_modules(business_type, org.enabled_modules)
        permissions = sorted(ROLE_PERMISSIONS.get(membership.role, set()))

        return AuthMeResponse(
            user=UserResponse.model_validate(user),
            membership=MembershipInfo(
                organization_id=org.id,
                organization_name=org.name,
                role=membership.role,
                status=membership.status,
                business_type=business_type,
                enabled_modules=enabled_modules,
                permissions=permissions,
            ),
            clinic_ids=clinic_ids,
        )

    async def invite_staff(self, data: InviteStaffRequest, organization_id: UUID) -> UserResponse:
        existing = await self.session.execute(select(User).where(User.email == data.email))
        user = existing.scalar_one_or_none()
        if not user:
            user = User(
                email=data.email,
                password_hash=hash_password(secrets.token_urlsafe(32)),
                full_name=data.full_name,
                is_active=False,
            )
            self.session.add(user)
            await self.session.flush()

        token = secrets.token_urlsafe(32)
        membership = Membership(
            user_id=user.id,
            organization_id=organization_id,
            role=data.role,
            status="invited",
            invited_at=datetime.now(timezone.utc),
            invitation_token=token,
        )
        self.session.add(membership)
        await self.session.flush()

        for clinic_id in data.clinic_ids:
            clinic_result = await self.session.execute(
                select(Clinic.id).where(
                    Clinic.id == clinic_id,
                    Clinic.organization_id == organization_id,
                    Clinic.deleted_on.is_(None),
                )
            )
            if clinic_result.scalar_one_or_none() is None:
                raise NotFoundException(f"Clinic {clinic_id} not found")
            assignment = ClinicAssignment(
                membership_id=membership.id,
                organization_id=organization_id,
                clinic_id=clinic_id,
            )
            self.session.add(assignment)
        await self.session.flush()

        return UserResponse.model_validate(user)

    async def accept_invitation(self, data: AcceptInvitationRequest) -> TokenResponse:
        result = await self.session.execute(
            select(Membership, User)
            .join(User, Membership.user_id == User.id)
            .where(Membership.invitation_token == data.token, Membership.status == "invited")
        )
        row = result.first()
        if not row:
            raise NotFoundException("Invalid invitation token")
        membership, user = row

        user.password_hash = hash_password(data.password)
        user.is_active = True
        membership.status = "active"
        membership.joined_at = datetime.now(timezone.utc)
        membership.invitation_token = None
        await self.session.flush()

        token = create_access_token(
            user.id,
            role=membership.role,
            extra={"organization_id": str(membership.organization_id)},
        )
        return TokenResponse(access_token=token)

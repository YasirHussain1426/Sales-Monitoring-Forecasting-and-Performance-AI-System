from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCompanyAdmin(BasePermission):
    message = "Only company admins can perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        profile = getattr(user, "profile", None)

        return bool(
            profile
            and profile.role == "company_admin"
        )


class IsAuthenticatedReadOnlyOrCompanyAdmin(BasePermission):
    message = "Only company admins can modify this resource."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        profile = getattr(user, "profile", None)

        return bool(
            profile
            and profile.role == "company_admin"
        )


class IsCompanyAdminOrManager(BasePermission):
    message = "Only company admins or sales managers can perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        profile = getattr(user, "profile", None)

        return bool(
            profile
            and profile.role in {
                "company_admin",
                "sales_manager",
            }
        )


class SalesTransactionPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        profile = getattr(user, "profile", None)

        if not profile:
            return False

        role = profile.role

        if role == "company_admin":
            return True

        if role == "sales_manager":
            return True

        if role == "salesperson":
            return request.method in SAFE_METHODS or request.method == "POST"

        if role == "analyst":
            return request.method in SAFE_METHODS

        return False
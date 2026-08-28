from .models import SalesTransaction


def get_authorized_sales_queryset(user):
    """
    Return the sales transactions the authenticated user is
    allowed to access based on application role.
    """

    queryset = SalesTransaction.objects.select_related(
        "customer",
        "product",
        "salesperson",
        "salesperson__region",
    )

    profile = getattr(user, "profile", None)

    if not user or not user.is_authenticated or not profile:
        return queryset.none()

    if profile.role in {
        "company_admin",
        "analyst",
    }:
        return queryset

    if profile.role == "sales_manager":
        sales_profile = getattr(user, "sales_profile", None)

        if not sales_profile:
            return queryset.none()

        return queryset.filter(
            salesperson__region_id=sales_profile.region_id
        )

    if profile.role == "salesperson":
        sales_profile = getattr(user, "sales_profile", None)

        if not sales_profile:
            return queryset.none()

        return queryset.filter(
            salesperson__user_id=user.id
        )

    return queryset.none()
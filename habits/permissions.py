from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Разрешение, позволяющее работать с объектом
    только его владельцу (поле user).
    """

    def has_object_permission(self, request, view, obj):
        user = getattr(obj, "user", None)
        return user == request.user

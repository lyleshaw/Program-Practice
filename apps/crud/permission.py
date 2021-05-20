from sqlalchemy.orm import Session

from apps.model.permission import PermissionDB
from apps.serializer.permission import PermissionSerializer


def add_permission(session: Session, permission_serializer: PermissionSerializer) -> PermissionDB:
    permission = PermissionDB(name=permission_serializer.name)
    session.add(permission)
    return permission


def get_permission_by_id(session: Session, permission_id: int) -> PermissionDB:
    permission = session.query(PermissionDB).filter(PermissionDB.id == permission_id).first()
    return permission


def update_permission_by_id(session: Session, permission_id: int, permission_serializer: PermissionSerializer) -> PermissionDB:
    permission = session.query(PermissionDB).filter(PermissionDB.id == permission_id).first()
    if permission is None:
        return None
    permission.name = permission_serializer.name
    session.add(permission)
    return permission

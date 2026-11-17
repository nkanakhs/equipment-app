from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    REAL,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AppSettings(Base):
    __tablename__ = "app_settings"

    application_name: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    library_name: Mapped[Optional[str]] = mapped_column(Text)
    organization_name: Mapped[Optional[str]] = mapped_column(Text)
    default_unit: Mapped[Optional[str]] = mapped_column(Text)
    headquarters_name: Mapped[Optional[str]] = mapped_column(Text)
    headquarters_address: Mapped[Optional[str]] = mapped_column(Text)
    headquarters_latitude: Mapped[Optional[float]] = mapped_column(REAL)
    headquarters_longitude: Mapped[Optional[float]] = mapped_column(REAL)


class Equipment(Base):
    __tablename__ = "equipment"

    code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("'Διαθέσιμο'"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    category: Mapped[Optional[str]] = mapped_column(Text)
    manufacturer: Mapped[Optional[str]] = mapped_column(Text)
    model: Mapped[Optional[str]] = mapped_column(Text)
    serial_number: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    equipment_photo: Mapped[Optional[str]] = mapped_column(Text)
    location_photo: Mapped[Optional[str]] = mapped_column(Text)
    dei_registry_number: Mapped[Optional[str]] = mapped_column(Text)
    tem_internal_code: Mapped[Optional[str]] = mapped_column(Text)
    dexion: Mapped[Optional[str]] = mapped_column(String(255))
    shelf: Mapped[Optional[str]] = mapped_column(String(255))
    storage_column: Mapped[Optional[str]] = mapped_column(String(255))

    equipment_alternatives_alternative_equipment: Mapped[list["EquipmentAlternatives"]] = (
        relationship(
            "EquipmentAlternatives",
            foreign_keys="[EquipmentAlternatives.alternative_equipment_id]",
            back_populates="alternative_equipment",
        )
    )
    equipment_alternatives_equipment: Mapped[list["EquipmentAlternatives"]] = relationship(
        "EquipmentAlternatives",
        foreign_keys="[EquipmentAlternatives.equipment_id]",
        back_populates="equipment",
    )
    equipment_documents: Mapped[list["EquipmentDocuments"]] = relationship(
        "EquipmentDocuments", back_populates="equipment"
    )
    field_mission_items: Mapped[list["FieldMissionItems"]] = relationship(
        "FieldMissionItems", back_populates="equipment"
    )
    loans: Mapped[list["Loans"]] = relationship("Loans", back_populates="equipment")
    picking_list_items: Mapped[list["PickingListItems"]] = relationship(
        "PickingListItems", back_populates="equipment"
    )


class EquipmentCategories(Base):
    __tablename__ = "equipment_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class FieldMissions(Base):
    __tablename__ = "field_missions"

    destination: Mapped[str] = mapped_column(Text, nullable=False)
    team_name: Mapped[str] = mapped_column(Text, nullable=False)
    departure_date: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("'Προετοιμασία'"))
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    mission_code: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    expected_return_date: Mapped[Optional[str]] = mapped_column(Text)
    vehicle: Mapped[Optional[str]] = mapped_column(Text)
    license_plate: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[str]] = mapped_column(Text)

    field_mission_items: Mapped[list["FieldMissionItems"]] = relationship(
        "FieldMissionItems", back_populates="mission"
    )


class MeasurementTeams(Base):
    __tablename__ = "measurement_teams"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class MissionDestinations(Base):
    __tablename__ = "mission_destinations"
    __table_args__ = (
        Index("idx_mission_destinations_station_code",
              text("(NULLIF(TRIM(station_code), ''))"), unique=True),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    is_location_verified: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    show_on_map: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    address: Mapped[Optional[str]] = mapped_column(Text)
    latitude: Mapped[Optional[float]] = mapped_column(REAL)
    longitude: Mapped[Optional[float]] = mapped_column(REAL)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    station_code: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[Optional[str]] = mapped_column(Text)
    energy_source: Mapped[Optional[str]] = mapped_column(Text)
    area_system: Mapped[Optional[str]] = mapped_column(Text)
    coordinate_accuracy: Mapped[Optional[str]] = mapped_column(Text)
    operational_status: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)


class MissionVehicles(Base):
    __tablename__ = "mission_vehicles"

    model: Mapped[str] = mapped_column(Text, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)


class PickingLists(Base):
    __tablename__ = "picking_lists"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("'Draft'"))
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    list_code: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    destination: Mapped[Optional[str]] = mapped_column(Text)
    travel_date: Mapped[Optional[str]] = mapped_column(Text)
    team_name: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    picking_list_items: Mapped[list["PickingListItems"]] = relationship(
        "PickingListItems", back_populates="picking_list"
    )


class StorageLocations(Base):
    __tablename__ = "storage_locations"
    __table_args__ = (UniqueConstraint("dexion", "shelf", "storage_column"),)

    dexion: Mapped[str] = mapped_column(String(255), nullable=False)
    shelf: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_column: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(Text)


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('ADMIN','USER')"),
    )

    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    last_login: Mapped[Optional[str]] = mapped_column(Text)

    audit_log: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")
    user_sessions: Mapped[list["UserSessions"]] = relationship(
        "UserSessions", back_populates="user"
    )


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("idx_audit_created_at", "created_at"),)

    action: Mapped[str] = mapped_column(Text, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    username: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(Text)
    role: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[Optional["Users"]] = relationship("Users", back_populates="audit_log")


class EquipmentAlternatives(Base):
    __tablename__ = "equipment_alternatives"
    __table_args__ = (UniqueConstraint("equipment_id", "alternative_equipment_id"),)

    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    alternative_equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id"), nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)

    alternative_equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        foreign_keys=[alternative_equipment_id],
        back_populates="equipment_alternatives_alternative_equipment",
    )
    equipment: Mapped["Equipment"] = relationship(
        "Equipment", foreign_keys=[equipment_id], back_populates="equipment_alternatives_equipment"
    )


class EquipmentDocuments(Base):
    __tablename__ = "equipment_documents"

    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    original_name: Mapped[str] = mapped_column(Text, nullable=False)
    stored_name: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="equipment_documents")


class FieldMissionItems(Base):
    __tablename__ = "field_mission_items"
    __table_args__ = (UniqueConstraint("mission_id", "equipment_id"),)

    mission_id: Mapped[int] = mapped_column(ForeignKey("field_missions.id"), nullable=False)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("'Προετοιμασία'"))
    added_at: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    returned_at: Mapped[Optional[str]] = mapped_column(Text)
    return_notes: Mapped[Optional[str]] = mapped_column(Text)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="field_mission_items")
    mission: Mapped["FieldMissions"] = relationship(
        "FieldMissions", back_populates="field_mission_items"
    )


class Loans(Base):
    __tablename__ = "loans"

    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    borrower_name: Mapped[str] = mapped_column(Text, nullable=False)
    checkout_date: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    borrower_unit: Mapped[Optional[str]] = mapped_column(Text)
    expected_return_date: Mapped[Optional[str]] = mapped_column(Text)
    return_date: Mapped[Optional[str]] = mapped_column(Text)
    checkout_notes: Mapped[Optional[str]] = mapped_column(Text)
    return_notes: Mapped[Optional[str]] = mapped_column(Text)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="loans")


class PickingListItems(Base):
    __tablename__ = "picking_list_items"
    __table_args__ = (UniqueConstraint("picking_list_id", "equipment_id"),)

    picking_list_id: Mapped[int] = mapped_column(ForeignKey("picking_lists.id"), nullable=False)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="picking_list_items")
    picking_list: Mapped["PickingLists"] = relationship(
        "PickingLists", back_populates="picking_list_items"
    )


class UserSessions(Base):
    __tablename__ = "user_sessions"
    __table_args__ = (Index("idx_user_sessions_token", "token_hash"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)

    user: Mapped["Users"] = relationship("Users", back_populates="user_sessions")

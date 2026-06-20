"""Seed comprehensive demo data for Cabinet Dentaire Atlas."""

import asyncio
import logging
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.model import Appointment
from app.billing.model import Invoice, InvoiceItem, Payment
from app.clinics.model import Clinic, ClinicRoom
from app.dental_chart.model import DentalChart, ToothRecord
from app.documents.model import ActivityLog, Document, Notification
from app.inventory.model import InventoryItem, StockMovement, Supplier
from app.organizations.model import Organization
from app.patients.model import MedicalHistory, Patient
from app.staff.model import ClinicAssignment, Membership
from app.treatment_plans.model import TreatmentItem, TreatmentPlan
from app.users.model import User
from core.database.session import async_session_factory
from core.logging import setup_logging
from core.middleware.auth.exceptions import hash_password
from core.middleware.auth.permission_list import Role

logger = logging.getLogger(__name__)

ORG_NAME = "Cabinet Dentaire Atlas"
OWNER_EMAIL = "owner@atlas-dental.ma"
DEFAULT_PASSWORD = "password123"

CLINICS = [
    {
        "name": "Casablanca Centre",
        "address": "45 Boulevard Mohammed V",
        "city": "Casablanca",
        "country": "Maroc",
        "phone": "+212 522 123 456",
        "email": "casablanca@atlas-dental.ma",
        "timezone": "Africa/Casablanca",
    },
    {
        "name": "Rabat Agdal",
        "address": "12 Avenue Annakhil",
        "city": "Rabat",
        "country": "Maroc",
        "phone": "+212 537 234 567",
        "email": "rabat@atlas-dental.ma",
        "timezone": "Africa/Casablanca",
    },
    {
        "name": "Marrakech Gueliz",
        "address": "8 Rue de la Liberté",
        "city": "Marrakech",
        "country": "Maroc",
        "phone": "+212 524 345 678",
        "email": "marrakech@atlas-dental.ma",
        "timezone": "Africa/Casablanca",
    },
]

STAFF = [
    ("owner", "Dr. Karim Alaoui", OWNER_EMAIL, "+212 661 000 001"),
    ("admin", "Sanae Benjelloun", "admin1@atlas-dental.ma", "+212 661 000 002"),
    ("admin", "Mehdi Tazi", "admin2@atlas-dental.ma", "+212 661 000 003"),
    ("dentist", "Dr. Leila Chraibi", "dentist1@atlas-dental.ma", "+212 661 000 004"),
    ("dentist", "Dr. Youssef Idrissi", "dentist2@atlas-dental.ma", "+212 661 000 005"),
    ("dentist", "Dr. Amal Fassi", "dentist3@atlas-dental.ma", "+212 661 000 006"),
    ("assistant", "Nadia El Amrani", "assistant1@atlas-dental.ma", "+212 661 000 007"),
    ("assistant", "Hassan Berrada", "assistant2@atlas-dental.ma", "+212 661 000 008"),
    ("receptionist", "Sara Mouline", "reception1@atlas-dental.ma", "+212 661 000 009"),
    ("receptionist", "Omar Benali", "reception2@atlas-dental.ma", "+212 661 000 010"),
]

FIRST_NAMES = [
    "Youssef",
    "Fatima",
    "Amina",
    "Karim",
    "Nadia",
    "Hassan",
    "Leila",
    "Omar",
    "Sara",
    "Mohammed",
    "Khadija",
    "Rachid",
    "Imane",
    "Adil",
    "Salma",
    "Hamza",
    "Zineb",
    "Mehdi",
    "Loubna",
    "Reda",
    "Pierre",
    "Marie",
    "Sophie",
    "Jean",
    "Claire",
    "Thomas",
    "Isabelle",
    "Nicolas",
    "Camille",
    "Julien",
    "Aïcha",
    "Bilal",
    "Houda",
    "Tarik",
    "Samira",
    "Khalid",
    "Nour",
    "Yasmine",
    "Anas",
    "Latifa",
]

LAST_NAMES = [
    "Alaoui",
    "Benali",
    "Chraibi",
    "El Amrani",
    "Fassi",
    "Idrissi",
    "Berrada",
    "Mouline",
    "Tazi",
    "Benjelloun",
    "Lahlou",
    "Ouazzani",
    "Bennani",
    "Ziani",
    "Kettani",
    "Sefrioui",
    "Bensaid",
    "Dupont",
    "Martin",
    "Bernard",
    "Moreau",
    "Lefebvre",
    "Garcia",
    "Roux",
    "Fontaine",
    "Mercier",
    "Hajji",
    "Amrani",
    "Cherkaoui",
    "Filali",
    "Sqalli",
    "Bouazza",
    "Naciri",
    "Tahiri",
    "Rami",
]

ALLERGIES = [
    None,
    "Pénicilline",
    "Latex",
    "Aspirine",
    "Iode",
    "Anesthésiques locaux",
    "Pénicilline, Latex",
]

CHRONIC_DISEASES = [
    None,
    "Diabète type 2",
    "Hypertension",
    "Asthme",
    "Hypothyroïdie",
]

MEDICATIONS = [
    None,
    "Metformine 500mg",
    "Amlodipine 5mg",
    "Ventoline au besoin",
    "Levothyrox 50mcg",
]

TREATMENT_TYPES = [
    "Consultation",
    "Détartrage",
    "Extraction",
    "Plombage composite",
    "Couronne céramique",
    "Blanchiment",
    "Traitement de canal",
    "Pose d'implant",
    "Prothèse amovible",
    "Orthodontie - contrôle",
]

APPOINTMENT_STATUSES = ["scheduled", "confirmed", "completed", "cancelled", "no_show"]

TOOTH_STATUSES = ["healthy", "caries", "filled", "crown", "missing", "root_canal", "implant"]

TREATMENT_NAMES = [
    ("Plombage composite", 450),
    ("Couronne céramique", 3500),
    ("Extraction simple", 600),
    ("Traitement de canal", 1800),
    ("Détartrage", 350),
    ("Blanchiment", 2500),
    ("Pose d'implant", 8500),
    ("Prothèse amovible", 4200),
    ("Consultation", 200),
    ("Radiographie panoramique", 300),
]

INVENTORY_CATALOG = [
    ("Gants nitrile (boîte)", "CONS-001", "Consommables", 150, "boîte", 30, 85),
    ("Masques chirurgicaux (boîte)", "CONS-002", "Consommables", 80, "boîte", 20, 45),
    ("Composite A2", "MAT-001", "Matériaux", 25, "seringue", 10, 320),
    ("Ciment verre ionomère", "MAT-002", "Matériaux", 15, "unité", 5, 280),
    ("Anesthésique locale (carpules)", "PHAR-001", "Pharmacie", 200, "carpule", 50, 12),
    ("Fil de suture résorbable", "SUT-001", "Chirurgie", 40, "unité", 10, 95),
    ("Buses à ultrasons", "EQUIP-001", "Équipement", 60, "unité", 15, 25),
    ("Gel fluoré", "PREV-001", "Prévention", 30, "flacon", 8, 180),
]

SUPPLIERS_DATA = [
    ("Dental Pro Maroc", "Rachid Sqalli", "+212 522 900 100", "contact@dentalpro.ma"),
    ("MediDent Casablanca", "Fatima Naciri", "+212 522 800 200", "ventes@medident.ma"),
    ("OrthoSupply Rabat", "Jean Dupont", "+212 537 700 300", "info@orthosupply.ma"),
]

FDI_TEETH = list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))

PAYMENT_METHODS = ["cash", "card", "transfer", "check"]

DOCUMENT_TYPES = ["radiograph", "consent_form", "prescription", "report", "invoice_pdf", "other"]

NOTIFICATION_TEMPLATES = [
    ("appointment_reminder", "Rappel de rendez-vous", "Vous avez un rendez-vous demain à {time}."),
    ("appointment_confirmed", "Rendez-vous confirmé", "Le rendez-vous du {date} a été confirmé."),
    ("invoice_due", "Facture en attente", "La facture {number} est en attente de paiement."),
    ("low_stock", "Stock bas", "L'article {item} est en dessous du seuil minimum."),
    (
        "treatment_approved",
        "Plan de traitement approuvé",
        "Le plan de traitement pour {patient} a été approuvé.",
    ),
]

ACTIVITY_EVENTS = [
    ("patient.created", "Nouveau patient enregistré"),
    ("appointment.scheduled", "Rendez-vous planifié"),
    ("appointment.completed", "Rendez-vous terminé"),
    ("invoice.created", "Facture créée"),
    ("payment.received", "Paiement reçu"),
    ("treatment.started", "Traitement démarré"),
    ("inventory.updated", "Stock mis à jour"),
]


def _rand_phone() -> str:
    return f"+212 6{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)}"


def _rand_email(first: str, last: str, idx: int) -> str:
    slug = f"{first.lower()}.{last.lower().replace(' ', '')}{idx}"
    return f"{slug}@email.ma"


def _opening_hours() -> dict:
    return {
        "monday": {"open": "09:00", "close": "18:00"},
        "tuesday": {"open": "09:00", "close": "18:00"},
        "wednesday": {"open": "09:00", "close": "18:00"},
        "thursday": {"open": "09:00", "close": "18:00"},
        "friday": {"open": "09:00", "close": "13:00"},
        "saturday": {"open": "09:00", "close": "14:00"},
        "sunday": None,
    }


async def org_exists(session: AsyncSession) -> bool:
    result = await session.execute(select(Organization).where(Organization.name == ORG_NAME))
    return result.scalar_one_or_none() is not None


async def seed_demo_data(session: AsyncSession) -> None:
    random.seed(42)
    now = datetime.now(timezone.utc)
    password_hash = hash_password(DEFAULT_PASSWORD)

    org = Organization(
        name=ORG_NAME,
        billing_info="ICE: 001234567000012 | RC: 123456 | IF: 45678910",
    )
    session.add(org)
    await session.flush()

    clinics: list[Clinic] = []
    for data in CLINICS:
        clinic = Clinic(
            organization_id=org.id,
            opening_hours=_opening_hours(),
            status="active",
            **data,
        )
        session.add(clinic)
        clinics.append(clinic)
    await session.flush()

    rooms_by_clinic: dict[uuid.UUID, list[ClinicRoom]] = {}
    for clinic in clinics:
        rooms: list[ClinicRoom] = []
        for chair in range(1, 4):
            room = ClinicRoom(
                organization_id=org.id,
                clinic_id=clinic.id,
                name=f"Salle {chair}",
                chair_number=chair,
                status="available" if chair < 3 else random.choice(["available", "occupied"]),
            )
            session.add(room)
            rooms.append(room)
        rooms_by_clinic[clinic.id] = rooms
    await session.flush()

    users: list[User] = []
    memberships: list[Membership] = []
    dentists: list[User] = []
    for role, full_name, email, phone in STAFF:
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone,
            is_active=True,
            last_active=now - timedelta(days=random.randint(0, 7)),
        )
        session.add(user)
        users.append(user)
        if role == Role.DENTIST:
            dentists.append(user)
    await session.flush()

    for i, (role, _, _, _) in enumerate(STAFF):
        membership = Membership(
            organization_id=org.id,
            user_id=users[i].id,
            role=role,
            status="active",
            joined_at=now - timedelta(days=random.randint(30, 365)),
        )
        session.add(membership)
        memberships.append(membership)
    await session.flush()

    for i, membership in enumerate(memberships):
        assigned_clinics = (
            clinics if STAFF[i][0] in (Role.OWNER, Role.ADMIN) else [clinics[i % len(clinics)]]
        )
        for clinic in assigned_clinics:
            session.add(
                ClinicAssignment(
                    organization_id=org.id,
                    membership_id=membership.id,
                    clinic_id=clinic.id,
                )
            )
    await session.flush()

    owner = users[0]
    receptionists = [u for u, (r, _, _, _) in zip(users, STAFF) if r == Role.RECEPTIONIST]

    patients: list[Patient] = []
    for i in range(100):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        clinic = clinics[i % len(clinics)]
        gender = random.choice(["male", "female"])
        birth_year = random.randint(1960, 2005)
        patient = Patient(
            organization_id=org.id,
            clinic_id=clinic.id,
            created_by=random.choice(receptionists).id,
            full_name=f"{first} {last}",
            birth_date=date(birth_year, random.randint(1, 12), random.randint(1, 28)),
            gender=gender,
            phone=_rand_phone(),
            email=_rand_email(first, last, i),
            address=f"{random.randint(1, 200)} Rue {random.choice(['Hassan II', 'Mohammed V', 'de France', 'Atlas', 'Zerktouni'])}, {clinic.city}",
            emergency_contact=f"{random.choice(FIRST_NAMES)} {last} - {_rand_phone()}",
            occupation=random.choice(
                [
                    "Enseignant",
                    "Ingénieur",
                    "Commerçant",
                    "Étudiant",
                    "Fonctionnaire",
                    "Médecin",
                    None,
                ]
            ),
            status="active",
            notes=random.choice(
                [
                    None,
                    "Patient anxieux",
                    "Préfère les RDV matinaux",
                    "Allergie signalée au dossier",
                ]
            ),
        )
        session.add(patient)
        patients.append(patient)
    await session.flush()

    for patient in patients:
        session.add(
            MedicalHistory(
                organization_id=org.id,
                patient_id=patient.id,
                allergies=random.choice(ALLERGIES),
                chronic_diseases=random.choice(CHRONIC_DISEASES),
                current_medications=random.choice(MEDICATIONS),
                pregnancy_status=(
                    random.choice([None, "non_applicable", "non", "oui"])
                    if patient.gender == "female"
                    else None
                ),
                smoking_status=random.choice(["non", "occasionnel", "régulier", "ancien_fumeur"]),
                previous_surgeries=random.choice(
                    [None, "Appendicectomie", "Césarienne", "Extraction dent de sagesse"]
                ),
                medical_alerts=random.choice(
                    [None, "Diabète - surveillance glycémie", "Anticoagulants"]
                ),
                blood_pressure_notes=random.choice(
                    [None, "120/80", "135/85 - légère hypertension"]
                ),
                doctor_notes=random.choice(
                    [None, "Bonne hygiène bucco-dentaire", "Suivi orthodontique recommandé"]
                ),
            )
        )
    await session.flush()

    appointments: list[Appointment] = []
    start_range = now - timedelta(days=90)
    end_range = now + timedelta(days=30)
    total_days = (end_range - start_range).days

    for _ in range(200):
        patient = random.choice(patients)
        clinic = next(c for c in clinics if c.id == patient.clinic_id)
        room = random.choice(rooms_by_clinic[clinic.id])
        day_offset = random.randint(0, total_days)
        appt_date = (start_range + timedelta(days=day_offset)).replace(
            hour=random.choice([9, 10, 11, 14, 15, 16, 17]),
            minute=random.choice([0, 15, 30, 45]),
            second=0,
            microsecond=0,
        )
        duration = random.choice([30, 45, 60, 90])
        is_past = appt_date < now
        if is_past:
            status = random.choices(
                ["completed", "cancelled", "no_show", "confirmed"],
                weights=[70, 10, 5, 15],
            )[0]
        else:
            status = random.choice(["scheduled", "confirmed"])

        appointment = Appointment(
            organization_id=org.id,
            clinic_id=clinic.id,
            created_by=random.choice(receptionists).id,
            patient_id=patient.id,
            dentist_id=random.choice(dentists).id,
            room_id=room.id,
            start_time=appt_date,
            end_time=appt_date + timedelta(minutes=duration),
            treatment_type=random.choice(TREATMENT_TYPES),
            notes=random.choice(
                [None, "Première visite", "Contrôle post-traitement", "Urgence dentaire"]
            ),
            status=status,
            reminder_status=(
                random.choice(["pending", "sent", "not_needed"]) if not is_past else "sent"
            ),
        )
        session.add(appointment)
        appointments.append(appointment)
    await session.flush()

    charts: list[DentalChart] = []
    for patient in patients:
        chart = DentalChart(
            organization_id=org.id,
            clinic_id=patient.clinic_id,
            patient_id=patient.id,
            status="active",
            notes=random.choice([None, "Charte initiale complétée", "Suivi semestriel"]),
        )
        session.add(chart)
        charts.append(chart)
    await session.flush()

    for chart in charts:
        affected_teeth = random.sample(FDI_TEETH, k=random.randint(3, 8))
        for tooth_num in affected_teeth:
            status = random.choice(TOOTH_STATUSES)
            session.add(
                ToothRecord(
                    organization_id=org.id,
                    chart_id=chart.id,
                    tooth_number=tooth_num,
                    status=status,
                    diagnosis=random.choice(
                        [None, "Caries profonde", "Fracture coronaire", "Pulpite", "Abcès"]
                    ),
                    notes=random.choice([None, "Surveillance requise", "Traitement urgent"]),
                    planned_treatments=random.choice(
                        [None, "Couronne", "Extraction", "Traitement de canal"]
                    ),
                    completed_treatments=(
                        random.choice([None, "Plombage", "Détartrage localisé"])
                        if status == "filled"
                        else None
                    ),
                )
            )
    await session.flush()

    treatment_plans: list[TreatmentPlan] = []
    plan_patients = random.sample(patients, k=50)
    for patient in plan_patients:
        items_data = random.sample(TREATMENT_NAMES, k=random.randint(2, 5))
        estimated_total = Decimal(sum(cost for _, cost in items_data))
        plan = TreatmentPlan(
            organization_id=org.id,
            clinic_id=patient.clinic_id,
            created_by=random.choice(dentists).id,
            patient_id=patient.id,
            dentist_id=random.choice(dentists).id,
            title=random.choice(
                [
                    "Plan de restauration",
                    "Traitement orthodontique",
                    "Réhabilitation complète",
                    "Soins préventifs",
                ]
            ),
            description=random.choice(
                [None, "Plan établi après consultation initiale", "Traitement en plusieurs séances"]
            ),
            status=random.choice(["draft", "active", "completed", "cancelled"]),
            estimated_total=estimated_total,
            notes=random.choice([None, "Devis présenté au patient", "En attente d'approbation"]),
        )
        session.add(plan)
        treatment_plans.append(plan)
        await session.flush()

        for name, cost in items_data:
            session.add(
                TreatmentItem(
                    organization_id=org.id,
                    plan_id=plan.id,
                    tooth_number=random.choice(FDI_TEETH) if random.random() > 0.3 else None,
                    name=name,
                    description=f"{name} - séance prévue",
                    estimated_cost=Decimal(cost),
                    status=random.choice(["planned", "in_progress", "completed", "cancelled"]),
                    priority=random.choice(["low", "normal", "high", "urgent"]),
                )
            )
    await session.flush()

    invoices: list[Invoice] = []
    invoice_patients = random.sample(patients, k=60)
    for idx, patient in enumerate(invoice_patients, start=1):
        items_data = random.sample(TREATMENT_NAMES, k=random.randint(1, 4))
        subtotal = Decimal(sum(cost for _, cost in items_data))
        discount = Decimal(random.choice([0, 0, 0, 50, 100, 200]))
        total = subtotal - discount
        amount_paid = Decimal(0)
        inv_status = "unpaid"
        if random.random() > 0.4:
            amount_paid = total
            inv_status = "paid"
        elif random.random() > 0.5:
            amount_paid = Decimal(int(total * Decimal("0.5")))
            inv_status = "partial"

        inv_date = date.today() - timedelta(days=random.randint(1, 120))
        invoice = Invoice(
            organization_id=org.id,
            clinic_id=patient.clinic_id,
            created_by=random.choice(receptionists).id,
            patient_id=patient.id,
            invoice_number=f"INV-2026-{idx:04d}",
            invoice_date=inv_date,
            due_date=inv_date + timedelta(days=30),
            subtotal=subtotal,
            discount=discount,
            total_amount=total,
            amount_paid=amount_paid,
            status=inv_status,
            notes=random.choice([None, "Paiement en plusieurs fois accepté"]),
        )
        session.add(invoice)
        invoices.append(invoice)
        await session.flush()

        for name, cost in items_data:
            session.add(
                InvoiceItem(
                    organization_id=org.id,
                    invoice_id=invoice.id,
                    description=name,
                    treatment_ref=random.choice([None, f"TRT-{random.randint(1000, 9999)}"]),
                    quantity=1,
                    unit_price=Decimal(cost),
                    total=Decimal(cost),
                )
            )

        if amount_paid > 0:
            session.add(
                Payment(
                    organization_id=org.id,
                    clinic_id=patient.clinic_id,
                    patient_id=patient.id,
                    invoice_id=invoice.id,
                    amount=amount_paid,
                    payment_date=inv_date + timedelta(days=random.randint(0, 15)),
                    method=random.choice(PAYMENT_METHODS),
                    reference=f"PAY-{uuid.uuid4().hex[:8].upper()}",
                    received_by=random.choice(receptionists).id,
                )
            )
    await session.flush()

    suppliers: list[Supplier] = []
    for name, contact, phone, email in SUPPLIERS_DATA:
        supplier = Supplier(
            organization_id=org.id,
            name=name,
            contact_person=contact,
            phone=phone,
            email=email,
            address=random.choice(["Casablanca", "Rabat", "Marrakech"]),
        )
        session.add(supplier)
        suppliers.append(supplier)
    await session.flush()

    inventory_items: list[InventoryItem] = []
    for clinic in clinics:
        for item_name, sku, category, qty, unit, min_level, cost in INVENTORY_CATALOG:
            item = InventoryItem(
                organization_id=org.id,
                clinic_id=clinic.id,
                name=item_name,
                sku=f"{sku}-{clinic.city[:3].upper()}",
                category=category,
                quantity=qty + random.randint(-5, 20),
                unit=unit,
                min_stock_level=min_level,
                cost_per_unit=Decimal(cost),
                supplier_id=random.choice(suppliers).id,
                expiry_date=(
                    date.today() + timedelta(days=random.randint(90, 730))
                    if category == "Pharmacie"
                    else None
                ),
            )
            session.add(item)
            inventory_items.append(item)
    await session.flush()

    for item in random.sample(inventory_items, k=min(15, len(inventory_items))):
        movement_type = random.choice(["in", "out", "adjustment"])
        qty = random.randint(1, 10)
        session.add(
            StockMovement(
                organization_id=org.id,
                clinic_id=item.clinic_id,
                created_by=random.choice(users).id,
                item_id=item.id,
                movement_type=movement_type,
                quantity=qty,
                reason=random.choice(
                    ["Réapprovisionnement", "Utilisation clinique", "Inventaire", "Péremption"]
                ),
            )
        )
    await session.flush()

    for patient in random.sample(patients, k=20):
        plan = random.choice(treatment_plans) if treatment_plans else None
        session.add(
            Document(
                organization_id=org.id,
                clinic_id=patient.clinic_id,
                created_by=random.choice(dentists).id,
                patient_id=patient.id,
                treatment_id=plan.id if plan and plan.patient_id == patient.id else None,
                file_name=f"doc_{patient.full_name.replace(' ', '_').lower()}_{random.randint(1, 99)}.pdf",
                file_type="application/pdf",
                document_type=random.choice(DOCUMENT_TYPES),
                file_url=f"/storage/documents/{uuid.uuid4()}.pdf",
                notes=random.choice([None, "Document scanné", "Consentement signé"]),
            )
        )
    await session.flush()

    for user in users:
        for _ in range(random.randint(2, 5)):
            template = random.choice(NOTIFICATION_TEMPLATES)
            session.add(
                Notification(
                    organization_id=org.id,
                    user_id=user.id,
                    notification_type=template[0],
                    title=template[1],
                    message=template[2].format(
                        time="10:30",
                        date=date.today().strftime("%d/%m/%Y"),
                        number=f"INV-2026-{random.randint(1, 60):04d}",
                        item=random.choice(INVENTORY_CATALOG)[0],
                        patient=random.choice(patients).full_name,
                    ),
                    is_read=random.choice([True, False, False]),
                    related_entity_type=random.choice([None, "appointment", "invoice", "patient"]),
                    related_entity_id=uuid.uuid4() if random.random() > 0.5 else None,
                )
            )
    await session.flush()

    for _ in range(80):
        patient = random.choice(patients)
        event_type, description = random.choice(ACTIVITY_EVENTS)
        session.add(
            ActivityLog(
                organization_id=org.id,
                clinic_id=patient.clinic_id,
                patient_id=patient.id,
                user_id=random.choice(users).id,
                event_type=event_type,
                description=f"{description}: {patient.full_name}",
                entity_type=random.choice([None, "patient", "appointment", "invoice"]),
                entity_id=uuid.uuid4() if random.random() > 0.3 else None,
            )
        )

    await session.commit()
    logger.info(
        "Seeded %s: %d clinics, %d staff, %d patients, %d appointments, "
        "%d charts, %d treatment plans, %d invoices, %d inventory items",
        ORG_NAME,
        len(clinics),
        len(users),
        len(patients),
        len(appointments),
        len(charts),
        len(treatment_plans),
        len(invoices),
        len(inventory_items),
    )


async def run_seed() -> None:
    setup_logging(debug=True)
    async with async_session_factory() as session:
        if await org_exists(session):
            logger.info("Organization '%s' already exists — skipping seed", ORG_NAME)
            return
        await seed_demo_data(session)


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()

import logging
import os
import sys
import uuid
from datetime import datetime

import pandas as pd
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, create_engine, text, update
from sqlalchemy.orm import declarative_base, sessionmaker

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import uuid

# Monkeypatch uuid7 to return standard uuid.UUID to please sqlalchemy/psycopg2
import uuid_utils

original_uuid7 = uuid_utils.uuid7


def standard_uuid7() -> uuid.UUID:
    val = original_uuid7()
    # Check if it's already a standard UUID or needs conversion
    if type(val) is uuid.UUID:
        return val
    return uuid.UUID(str(val))


uuid_utils.uuid7 = standard_uuid7


import secrets
import string

from sqlalchemy.sql import func

from app.api.models.address import Address

# Import other models to ensure they are registered in SQLAlchemy
from app.api.models.attachment import Attachment
from app.api.models.bank_account import BankAccount
from app.api.models.complementary_data import ComplementaryData
from app.api.models.institution_contract import InstitutionContract
from app.api.models.institution_contract_sector_value import InstitutionContractSectorValue
from app.api.models.institutions import Institution
from app.api.models.pix_key import PixKey
from app.api.models.profession import Profession
from app.api.models.professional_crm import ProfessionalCrm
from app.api.models.role import Role
from app.api.models.sectors import Sector
from app.api.models.specialty import Specialty
from app.api.models.user import User as LocalUser
from app.api.models.user_absence import UserAbsence
from app.api.models.user_role import UserRole
from app.api.models.user_specialty import UserSpecialty  # noqa: F401
from app.api.schemas.complementary_data import GenderEnum, MaritalStatusEnum

# NOTE: DocumentSourceEnum was removed after refactoring documents to attachments
# This import script needs to be updated to work with the new attachment structure
# from app.api.schemas.document import DocumentSourceEnum
from app.core.config import settings
from app.core.security import get_password_hash


def generate_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


local_engine = create_engine(settings.get_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=local_engine)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Monolith DB Connection
MONO_SERVER = settings.POSTGRES_MONO_SERVER
MONO_USER = settings.POSTGRES_MONO_USER
MONO_PASSWORD = settings.POSTGRES_MONO_PASSWORD
MONO_DB = settings.POSTGRES_MONO_DB
MONO_PORT = settings.POSTGRES_MONO_PORT

# Excel File Path
EXCEL_FILE = "Cadastro.xlsx"

if not MONO_SERVER:
    logger.error("Environment variable POSTGRES_MONO_SERVER is not set.")
    logger.warning(
        "Continuing without Monolith connection (will fail if Monolith query is needed)."
    )

# MONO_DATABASE_URL = f"postgresql://user:password@0.0.0.0:5432/oncall_pay_db"
# MONO_DATABASE_URL = (
#     f"postgresql://{MONO_USER}:{MONO_PASSWORD}@{MONO_SERVER}:{MONO_PORT}/{MONO_DB}"
# )

MONO_DATABASE_URL = (
    "postgresql://postgres:eiHtiIWnAkSTGNeSYJJbkJUwCTPHTtRB@maglev.proxy.rlwy.net:37717/railway"
)

# Monolith Model Definition
from typing import Any

BaseMono: Any = declarative_base()


class MonolithUser(BaseMono):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, nullable=False, default=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    password = Column(String(72))
    f_document_cpf = Column(String(11), nullable=True, unique=True)
    date_created = Column(DateTime)


def clean_cpf(value: Any) -> str | None:
    if pd.isna(value):
        return None
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    s = s.replace(".", "").replace("-", "").replace("/", "")

    if len(s) == 10:
        s = "0" + s

    if len(s) > 11:
        return s[:11]  # Truncate to first 11 chars
    return s.zfill(11) if s else None


def clean_alphanumeric(value: Any, max_len: int | None = None) -> str | None:
    if pd.isna(value):
        return None
    s = str(value).strip()
    if max_len and len(s) > max_len:
        return s[:max_len]
    return s


def map_marital_status(val: Any) -> MaritalStatusEnum | None:
    if pd.isna(val):
        return None
    s = str(val).upper().strip()
    if "SOLTEIRO" in s:
        return MaritalStatusEnum.SINGLE
    if "CASADO" in s:
        return MaritalStatusEnum.MARRIED
    if "DIVORCIADO" in s:
        return MaritalStatusEnum.DIVORCED
    if "VIUV" in s:
        return MaritalStatusEnum.WIDOWED
    if "UNIAO" in s or "UNIÃO" in s:
        return MaritalStatusEnum.DOMESTIC_PARTNERSHIP
    return None


def map_gender(val: Any) -> GenderEnum | None:
    if pd.isna(val):
        return None
    s = str(val).upper().strip()
    if "MASCULINO" in s or s == "M":
        return GenderEnum.MALE
    if "FEMININO" in s or s == "F":
        return GenderEnum.FEMALE
    return None


def migrate_users() -> None:
    logger.info("Starting user migration from Excel & Monolith...")

    # 1. Read Excel
    if not os.path.exists(EXCEL_FILE):
        logger.error(f"Excel file not found: {EXCEL_FILE}")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
        logger.info(f"Loaded Excel with {len(df)} rows.")
        logger.info(f"Columns: {list(df.columns)}")
        # Debug: show first non-null date value and its type
        date_col = next((c for c in df.columns if "NASC" in c.upper()), None)
        if date_col:
            sample = df[date_col].dropna().iloc[0] if not df[date_col].dropna().empty else None
            logger.info(
                f"Date column found: '{date_col}' | sample value: {sample!r} (type: {type(sample).__name__})"
            )
    except Exception as e:
        logger.error(f"Failed to read Excel: {e}")
        return

    # Pre-process Excel Data
    excel_users = []

    seen_cpfs = set()

    for _, row in df.iterrows():
        cpf = clean_cpf(row.get("CPF"))
        if not cpf:
            continue  # Skip invalid rows

        if cpf in seen_cpfs:
            logger.warning(f"Ignorando usuário repetido no Excel com CPF: {cpf}")
            continue
        seen_cpfs.add(cpf)

        name = str(row.get("NOME COMPLETO", "")).strip().title()
        parts = name.split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        email_val = str(row.get("E-MAIL", "")).strip()
        email: str | None = None if not email_val or email_val.lower() == "nan" else email_val

        # New fields
        phone = clean_alphanumeric(row.get("TELEFONE"), 20)

        # Date of birth
        dob = row.get("DATA DE NASCIMENTO")
        date_of_birth = None
        if dob is not None and not (isinstance(dob, float) and pd.isna(dob)):
            try:
                if hasattr(dob, "date"):
                    # Pandas already parsed it as Timestamp from Excel date column
                    date_of_birth = dob.date()
                else:
                    # String like "25/01/1989" — parse explicitly as DD/MM/YYYY
                    from datetime import datetime as _dt

                    date_of_birth = _dt.strptime(str(dob).strip(), "%d/%m/%Y").date()
            except Exception as e:
                logger.warning(f"Could not parse date of birth '{dob}': {e}")
        excel_users.append(
            {
                "cpf": cpf,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "date_of_birth": date_of_birth,
                "row_data": row,
                # New logic for pendency
                "is_pending": str(row.get("TERMO", "")).strip().upper() != "CONCLUÍDO",
            }
        )

    logger.info(f"Processed {len(excel_users)} valid entries from Excel.")

    excel_cpfs = [u["cpf"] for u in excel_users]

    # 2. Connect to Databases
    local_session = SessionLocal()

    mono_session = None
    try:
        if MONO_SERVER:
            mono_engine = create_engine(MONO_DATABASE_URL)
            MonoSession = sessionmaker(bind=mono_engine)
            mono_session = MonoSession()
            logger.info("Connected to Monolith database.")
    except Exception as e:
        logger.error(f"Failed to connect to Monolith: {e}")
        return

    try:
        # 3. Query Monolith for matching CPFs
        mono_matches = {}
        if mono_session and excel_cpfs:
            try:
                chunk_size = 1000
                for i in range(0, len(excel_cpfs), chunk_size):
                    chunk = excel_cpfs[i : i + chunk_size]
                    results = (
                        mono_session.query(MonolithUser)
                        .filter(MonolithUser.f_document_cpf.in_(chunk))
                        .all()
                    )
                    for m in results:
                        cleaned_mono_cpf = clean_cpf(m.f_document_cpf)
                        if cleaned_mono_cpf:
                            mono_matches[cleaned_mono_cpf] = m

                logger.info(f"Found {len(mono_matches)} matches in Monolith.")
            except Exception as e:
                logger.error(f"Failed to query Monolith: {e}. Continuing with Excel data only.")
                mono_matches = {}

        # Ensure 'professional' role exists
        pro_role = local_session.query(Role).filter(Role.name == "professional").first()
        if not pro_role:
            pro_role = Role(name="professional")
            local_session.add(pro_role)
            local_session.commit()
            local_session.refresh(pro_role)

        # Ensure 'Médico' profession exists (for specialties)
        med_profession = local_session.query(Profession).filter(Profession.name == "Médico").first()
        if not med_profession:
            med_profession = Profession(name="Médico", description="Profissional da medicina")
            local_session.add(med_profession)
            local_session.commit()
            local_session.refresh(med_profession)

        # 4. Sync Logic
        created_count = 0
        updated_count = 0

        for user_data in excel_users:
            try:
                cpf = user_data["cpf"]
                email = user_data["email"]
                row = user_data["row_data"]

                mono_user: MonolithUser | None = mono_matches.get(cpf) if cpf else None
                try:
                    local_user = local_session.query(LocalUser).filter(LocalUser.cpf == cpf).first()
                except Exception:
                    logger.warning(f"Skipping user {cpf} due to invalid CPF format/digits.")
                    continue

                if not local_user and email:
                    local_user = (
                        local_session.query(LocalUser).filter(LocalUser.email == email).first()
                    )

                if mono_user:

                    if local_user:
                        # removed ID sync logic and deletions

                        local_user.is_active = mono_user.active

                        # Generate new random password for everyone as requested
                        random_password = generate_random_password()
                        local_user.password = get_password_hash(random_password)

                        local_user.first_name = mono_user.first_name or user_data["first_name"]
                        local_user.last_name = mono_user.last_name or user_data["last_name"]
                        if mono_user.email:
                            local_user.email = mono_user.email
                        elif not local_user.email and email:
                            local_user.email = email

                        # Excel Overwrites - Source of Truth for these fields
                        if email:
                            local_user.email = email  # Force Excel email if present

                        local_user.phone = user_data["phone"]
                        local_user.date_of_birth = user_data["date_of_birth"]
                        local_user.pendency = user_data["is_pending"]
                        local_user.profession_id = med_profession.id

                        local_user.cpf = cpf  # type: ignore[assignment]

                        updated_count += 1
                    else:
                        random_password = generate_random_password()
                        new_user = LocalUser(
                            first_name=mono_user.first_name or user_data["first_name"],
                            last_name=mono_user.last_name or user_data["last_name"],
                            email=mono_user.email or email or f"noemail_{cpf}@placeholder.com",
                            cpf=cpf,
                            password=get_password_hash(random_password),
                            is_active=mono_user.active,
                            phone=user_data["phone"],
                            date_of_birth=user_data["date_of_birth"],
                            pendency=user_data["is_pending"],
                            profession_id=med_profession.id,
                        )
                        local_session.add(new_user)
                        created_count += 1
                else:
                    if local_user:
                        local_user.first_name = user_data["first_name"]
                        local_user.last_name = user_data["last_name"]
                        if email:
                            local_user.email = email
                        local_user.cpf = cpf  # type: ignore[assignment]
                        local_user.phone = user_data["phone"]
                        local_user.date_of_birth = user_data["date_of_birth"]
                        local_user.pendency = user_data["is_pending"]
                        local_user.profession_id = med_profession.id

                        random_password = generate_random_password()
                        local_user.password = get_password_hash(random_password)

                        updated_count += 1
                    else:
                        random_password = generate_random_password()
                        new_user = LocalUser(
                            first_name=user_data["first_name"],
                            last_name=user_data["last_name"],
                            email=email or f"noemail_{cpf}@placeholder.com",
                            cpf=cpf,
                            password=get_password_hash(random_password),
                            is_active=True,
                            phone=user_data["phone"],
                            date_of_birth=user_data["date_of_birth"],
                            pendency=user_data["is_pending"],
                            profession_id=med_profession.id,
                        )
                        local_session.add(new_user)
                        created_count += 1

                if not local_user:
                    local_session.flush()
                    local_user = new_user

                # --- SYNC RELATED DATA ---

                # 1. Attachments (RG)
                # rg_code = clean_alphanumeric(row.get("RG"), 50)
                # if rg_code:
                #     existing_rg = (
                #         local_session.query(Attachment)
                #         .filter_by(user_id=local_user.id, title=f"RG - {rg_code}")
                #         .first()
                #     )
                #     if not existing_rg:
                #         local_session.add(
                #             Attachment(user_id=local_user.id, title=f"RG - {rg_code}")
                #         )

                # 2. Address
                street_raw = clean_alphanumeric(row.get("ENDEREÇO"), 500)
                if street_raw:
                    addr = local_session.query(Address).filter_by(user_id=local_user.id).first()
                    if not addr:
                        addr = Address(user_id=local_user.id)
                        local_session.add(addr)

                    # Split "Rua X, 123 APTO 74" → street="Rua X", number="123", complement="APTO 74"
                    addr_parts = [p.strip() for p in street_raw.split(",", 1)]
                    addr.street = addr_parts[0][:255]
                    if len(addr_parts) > 1:
                        after_comma = addr_parts[1].split(None, 1)  # split on first whitespace
                        addr.number = after_comma[0][:25] if after_comma else "S/N"
                        addr.complement = after_comma[1][:255] if len(after_comma) > 1 else None
                    else:
                        addr.number = "S/N"
                        addr.complement = None

                    addr.neighborhood = clean_alphanumeric(row.get("BAIRRO"), 255) or "Unknown"

                    # Cidade/UF split
                    city_uf = row.get("CIDADE/UF")
                    if city_uf and isinstance(city_uf, str) and "/" in city_uf:
                        parts = city_uf.split("/")
                        addr.city = parts[0].strip()
                        addr.uf = parts[1].strip()[:2]
                    else:
                        addr.city = str(city_uf) if city_uf else "Unknown"
                        addr.uf = "XX"

                    addr.zip_code = clean_alphanumeric(row.get("CEP"), 8) or "00000000"

                # 3. Bank Account
                bank_name = clean_alphanumeric(row.get("BANCO"), 255)
                if bank_name:
                    # Look for existing bank account with same attributes or just any main one?
                    # The user might have multiple. We'll check by bank name for now as per old logic.
                    bank = (
                        local_session.query(BankAccount)
                        .filter_by(user_id=local_user.id, bank_name=bank_name)
                        .first()
                    )
                    if not bank:
                        bank = BankAccount(user_id=local_user.id, bank_name=bank_name)
                        local_session.add(bank)

                    bank.bank_code = clean_alphanumeric(row.get("Nº BANCO"), 10) or "000"
                    bank.agency = clean_alphanumeric(row.get("AGÊNCIA"), 10) or "0000"

                    raw_conta = str(row.get("CONTA", "")).strip()
                    if "-" in raw_conta:
                        c_parts = raw_conta.split("-")
                        bank.account_number = c_parts[0][:20]
                        bank.account_digit = c_parts[1][:2]
                    else:
                        bank.account_number = raw_conta[:20]
                        bank.account_digit = "0"

                    bank.account_type = clean_alphanumeric(row.get("TIPO CONTA"), 20) or "Corrente"
                    bank.is_main = True

                # 4. Pix Key
                pix_code = clean_alphanumeric(row.get("PIX"), 255)
                if pix_code:
                    existing_pix = (
                        local_session.query(PixKey)
                        .filter_by(user_id=local_user.id, code=pix_code)
                        .first()
                    )
                    if not existing_pix:
                        p_type = "random"
                        if "@" in pix_code:
                            p_type = "email"
                        elif len("".join(filter(str.isdigit, pix_code))) == 11:
                            p_type = "cpf"
                        elif pix_code.startswith("+"):
                            p_type = "phone"

                        local_session.add(
                            PixKey(user_id=local_user.id, code=pix_code, type=p_type, is_main=True)
                        )

                # 5. Roles
                existing_role = (
                    local_session.query(UserRole)
                    .filter_by(user_id=local_user.id, role_id=pro_role.id)
                    .first()
                )
                if not existing_role:
                    local_session.add(UserRole(user_id=local_user.id, role_id=pro_role.id))

                # 6. Complementary Data
                comp_data = (
                    local_session.query(ComplementaryData).filter_by(user_id=local_user.id).first()
                )
                if not comp_data:
                    comp_data = ComplementaryData(user_id=local_user.id)
                    local_session.add(comp_data)

                comp_data.mother_name = clean_alphanumeric(row.get("NOME DA MÃE"), 255)
                comp_data.father_name = clean_alphanumeric(row.get("NOME DO PAI"), 255)
                comp_data.nationality = clean_alphanumeric(row.get("NACIONALIDADE"), 255)
                comp_data.place_of_birth = clean_alphanumeric(
                    row.get("MUNICÍPIO DE NASCIMENTO"), 255
                )
                comp_data.marital_status = map_marital_status(row.get("ESTADO CIVIL"))
                # comp_data.gender = map_gender(row.get('Gênero')) # Not in file

                # 7. CRM (Professional CRM)
                crm_code = clean_alphanumeric(row.get("CRM"), 50)
                crm_state = clean_alphanumeric(row.get("UF/CRM"), 2)
                if crm_code and crm_state:
                    existing_crm = (
                        local_session.query(ProfessionalCrm)
                        .filter_by(user_id=local_user.id, code=crm_code, state=crm_state)
                        .first()
                    )
                    if not existing_crm:
                        local_session.add(
                            ProfessionalCrm(
                                user_id=local_user.id,
                                code=crm_code,
                                state=crm_state,
                            )
                        )

                local_session.commit()

            except Exception as e:
                local_session.rollback()
                logger.error(f"Error processing row {user_data.get('cpf')}: {e}")
                import traceback

                traceback.print_exc()

        logger.info(f"Migration finished. Created: {created_count}, Updated: {updated_count}")

    except Exception as e:
        logger.error(f"Global Error during processing: {e}")
        local_session.rollback()
        import traceback

        traceback.print_exc()
    finally:
        local_session.close()
        if mono_session:
            mono_session.close()


if __name__ == "__main__":
    migrate_users()

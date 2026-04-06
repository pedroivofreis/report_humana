#!/usr/bin/env python3
"""Seed database with test data.

Creates:
- roles
- professions + specialties
- users + address + complementary_data
- user_roles + user_professions_specialties

Usage:
  python scripts/seed_database.py --users 50 --seed 123
  python scripts/seed_database.py --users 200 --truncate --seed 1
"""

import argparse
import asyncio
import hashlib
import random
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import BigInteger, String, cast, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to path (same pattern as other scripts)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid  # noqa: E402

import uuid_utils  # noqa: E402

# Monkeypatch uuid7 to return standard UUID to satisfy SQLAlchemy's strict typing checks
# during bulk inserts (sentinel matching).
_original_uuid7 = uuid_utils.uuid7


def _compatible_uuid7() -> uuid.UUID:
    return uuid.UUID(int=_original_uuid7().int)


uuid_utils.uuid7 = _compatible_uuid7

from app.api.models.address import Address  # noqa: E402
from app.api.models.attachment import Attachment  # noqa: F401, E402
from app.api.models.bank_account import BankAccount  # noqa: F401, E402
from app.api.models.complementary_data import ComplementaryData  # noqa: E402
from app.api.models.institutions import Institution  # noqa: F401, E402
from app.api.models.pix_key import PixKey  # noqa: F401, E402
from app.api.models.profession import Profession  # noqa: E402
from app.api.models.role import Role  # noqa: E402
from app.api.models.sectors import Sector  # noqa: F401, E402
from app.api.models.specialty import Specialty  # noqa: E402
from app.api.models.user import User  # noqa: E402
from app.api.models.user_absence import UserAbsence  # noqa: F401, E402
from app.api.models.user_profession_specialty import UserProfessionSpecialty  # noqa: E402
from app.api.models.user_role import UserRole  # noqa: E402
from app.api.schemas.complementary_data import GenderEnum, MaritalStatusEnum, RaceEnum  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402

ROLE_SEED = [
    ("admin", "Administrador do sistema"),
    ("manager", "Gestor"),
    ("professional", "Profissional"),
]

PROFESSIONS_AND_SPECIALTIES: dict[str, list[str]] = {
    "Medicina": [
        "Acupuntura",
        "Alergia e Imunologia",
        "Anestesiologia",
        "Angiologia",
        "Cardiologia",
        "Cirurgia Cardiovascular",
        "Cirurgia da Mão",
        "Cirurgia de Cabeça e Pescoço",
        "Cirurgia do Aparelho Digestivo",
        "Cirurgia Geral",
        "Cirurgia Oncológica",
        "Cirurgia Pediátrica",
        "Cirurgia Plástica",
        "Cirurgia Torácica",
        "Cirurgia Vascular",
        "Clínica Médica",
        "Coloproctologia",
        "Dermatologia",
        "Endocrinologia e Metabologia",
        "Endoscopia",
        "Gastroenterologia",
        "Genética Médica",
        "Geriatria",
        "Ginecologia e Obstetrícia",
        "Hematologia e Hemoterapia",
        "Homeopatia",
        "Infectologia",
        "Mastologia",
        "Medicina de Emergência",
        "Medicina de Família e Comunidade",
        "Medicina do Trabalho",
        "Medicina do Tráfego",
        "Medicina Esportiva",
        "Medicina Física e Reabilitação",
        "Medicina Intensiva",
        "Medicina Legal e Perícia Médica",
        "Medicina Nuclear",
        "Medicina Preventiva e Social",
        "Nefrologia",
        "Neurocirurgia",
        "Neurologia",
        "Nutrologia",
        "Oftalmologia",
        "Oncologia Clínica",
        "Ortopedia e Traumatologia",
        "Otorrinolaringologia",
        "Patologia",
        "Patologia Clínica/Medicina Laboratorial",
        "Pediatria",
        "Pneumologia",
        "Psiquiatria",
        "Radiologia e Diagnóstico por Imagem",
        "Radioterapia",
        "Reumatologia",
        "Urologia",
    ],
    "Enfermagem": [
        "Enfermagem Aeroespacial",
        "Enfermagem em Cardiologia",
        "Enfermagem em Central de Material e Esterilização",
        "Enfermagem em Centro Cirúrgico",
        "Enfermagem em Cuidados Paliativos",
        "Enfermagem em Dermatologia",
        "Enfermagem em Diagnóstico por Imagem",
        "Enfermagem em Doenças Infecciosas",
        "Enfermagem em Endocrinologia",
        "Enfermagem em Estética",
        "Enfermagem em Estomaterapia",
        "Enfermagem em Gerontologia",
        "Enfermagem em Hematologia",
        "Enfermagem em Hemoterapia",
        "Enfermagem em Infecção Hospitalar",
        "Enfermagem em Nefrologia",
        "Enfermagem em Neurologia",
        "Enfermagem em Nutrição Parenteral",
        "Enfermagem em Obstetrícia",
        "Enfermagem em Oftalmologia",
        "Enfermagem em Oncologia",
        "Enfermagem em Otorrinolaringologia",
        "Enfermagem em Pediatria",
        "Enfermagem em Perícia Forense",
        "Enfermagem em Práticas Integrativas",
        "Enfermagem em Saúde Coletiva",
        "Enfermagem em Saúde da Criança e Adolescente",
        "Enfermagem em Saúde da Família",
        "Enfermagem em Saúde da Mulher",
        "Enfermagem em Saúde do Adulto",
        "Enfermagem em Saúde do Homem",
        "Enfermagem em Saúde do Idoso",
        "Enfermagem em Saúde Mental",
        "Enfermagem em Saúde Ocupacional",
        "Enfermagem em Terapia Holística",
        "Enfermagem em Terapia Intensiva",
        "Enfermagem em Traumato-ortopedia",
        "Enfermagem em Urgência e Emergência",
        "Enfermagem em Urologia",
    ],
    "Odontologia": [
        "Cirurgia e Traumatologia Buco-Maxilo-Facial",
        "Dentística",
        "Disfunção Temporomandibular e Dor Orofacial",
        "Endodontia",
        "Estomatologia",
        "Harmonização Orofacial",
        "Homeopatia",
        "Implantodontia",
        "Odontogeriatria",
        "Odontologia do Esporte",
        "Odontologia do Trabalho",
        "Odontologia Legal",
        "Odontologia para Pacientes com Necessidades Especiais",
        "Odontopediatria",
        "Ortodontia",
        "Ortopedia Funcional dos Maxilares",
        "Patologia Oral e Maxilo Facial",
        "Periodontia",
        "Prótese Buco-Maxilo-Facial",
        "Prótese Dentária",
        "Radiologia Odontológica e Imaginologia",
        "Saúde Coletiva",
    ],
    "Fisioterapia": [
        "Fisioterapia em Acupuntura",
        "Fisioterapia Aquática",
        "Fisioterapia Cardiovascular",
        "Fisioterapia Dermatofuncional",
        "Fisioterapia do Trabalho",
        "Fisioterapia Esportiva",
        "Fisioterapia em Gerontologia",
        "Fisioterapia Neurofuncional",
        "Fisioterapia em Oncologia",
        "Fisioterapia Respiratória",
        "Fisioterapia Traumato-Ortopédica",
        "Fisioterapia em Saúde da Mulher",
        "Fisioterapia em Terapia Intensiva",
        "Osteopatia",
        "Quiropraxia",
    ],
    "Psicologia": [
        "Neuropsicologia",
        "Psicologia Clínica",
        "Psicologia do Esporte",
        "Psicologia do Trânsito",
        "Psicologia Escolar e Educacional",
        "Psicologia Hospitalar",
        "Psicologia Jurídica",
        "Psicologia Organizacional e do Trabalho",
        "Psicologia Social",
        "Psicomotricidade",
        "Psicopedagogia",
    ],
    "Nutrição": [
        "Nutrição Clínica",
        "Nutrição Esportiva",
        "Nutrição em Saúde Coletiva",
        "Nutrição em Alimentação Coletiva",
        "Nutrição Materno-Infantil",
        "Fitoterapia",
    ],
    "Biomedicina": [
        "Acupuntura",
        "Análises Clínicas",
        "Análises Ambientais",
        "Biologia Molecular",
        "Biomedicina Estética",
        "Citopatologia",
        "Diagnóstico por Imagem",
        "Genética",
        "Hematologia",
        "Imunologia",
        "Microbiologia",
        "Parasitologia",
        "Toxicologia",
    ],
    "Farmácia": [
        "Análises Clínicas",
        "Farmácia Clínica",
        "Farmácia de Manipulação",
        "Farmácia Dermatológica",
        "Farmácia Hospitalar",
        "Farmácia Industrial",
        "Farmácia Oncológica",
        "Farmácia Veterinária",
        "Fitoterapia",
        "Radiofarmácia",
        "Toxicologia",
    ],
    "Fonoaudiologia": [
        "Audiologia",
        "Disfagia",
        "Fonoaudiologia Educacional",
        "Fonoaudiologia do Trabalho",
        "Fonoaudiologia Neurofuncional",
        "Gerontologia",
        "Linguagem",
        "Motricidade Orofacial",
        "Saúde Coletiva",
        "Voz",
    ],
    "Terapia Ocupacional": [
        "Terapia Ocupacional em Acupuntura",
        "Terapia Ocupacional em Contextos Hospitalares",
        "Terapia Ocupacional em Contextos Sociais",
        "Terapia Ocupacional em Gerontologia",
        "Terapia Ocupacional em Saúde da Família",
        "Terapia Ocupacional em Saúde Mental",
        "Terapia Ocupacional em Saúde do Trabalhador",
    ],
    "Educação Física": [
        "Personal Trainer",
        "Fisiologia do Exercício",
        "Ginástica Laboral",
        "Grupos Especiais",
        "Recreação e Lazer",
    ],
    "Veterinária": [
        "Anestesiologia Veterinária",
        "Cardiologia Veterinária",
        "Cirurgia de Pequenos Animais",
        "Clínica Cirúrgica de Grandes Animais",
        "Clínica Médica de Pequenos Animais",
        "Dermatologia Veterinária",
        "Diagnóstico por Imagem",
        "Oftalmologia Veterinária",
        "Oncologia Veterinária",
        "Patologia Veterinária",
        "Saúde Pública Veterinária",
    ],
}

FIRST_NAMES = [
    "Ana",
    "Bruno",
    "Carla",
    "Daniel",
    "Eduarda",
    "Felipe",
    "Gabriela",
    "Henrique",
    "Isabela",
    "João",
    "Larissa",
    "Marcos",
    "Natália",
    "Otávio",
    "Patrícia",
    "Rafael",
    "Sofia",
    "Thiago",
    "Vanessa",
    "Yasmin",
]

LAST_NAMES = [
    "Silva",
    "Souza",
    "Oliveira",
    "Santos",
    "Lima",
    "Pereira",
    "Ferreira",
    "Rodrigues",
    "Almeida",
    "Costa",
    "Gomes",
    "Ribeiro",
    "Carvalho",
    "Araujo",
    "Melo",
]

UF = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "PE", "CE", "GO"]
CITIES = [
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Porto Alegre",
    "Florianópolis",
]
NEIGHBORHOODS = ["Centro", "Jardins", "Copacabana", "Savassi", "Batel", "Trindade"]
STREETS = ["Rua das Flores", "Av. Brasil", "Rua A", "Rua B", "Av. Principal", "Rua do Comércio"]


def _sha256(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _digits(n: int, rng: random.Random) -> str:
    return "".join(str(rng.randint(0, 9)) for _ in range(n))


def _make_unique_email(first: str, last: str, i: int) -> str:
    return f"{first.lower()}.{last.lower()}.{i}@example.test"


def _generate_valid_cpf(seq: int) -> str:
    """Generate a valid CPF from a sequence number."""
    base = f"{seq:09d}"

    sum1 = sum(int(base[i]) * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 == 10:
        digit1 = 0

    base_with_digit1 = base + str(digit1)
    sum2 = sum(int(base_with_digit1[i]) * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 == 10:
        digit2 = 0

    return base + str(digit1) + str(digit2)


async def _truncate_tables(session: AsyncSession) -> None:
    # This is destructive. Only run when explicitly requested.
    await session.execute(
        text(
            """
            TRUNCATE TABLE
              users_roles,
              user_professions_specialties,
              complementary_data,
              addresses,
              pix_keys,
              bank_accounts,
              attachments,
              users,
              specialties,
              professions,
              roles
            CASCADE;
            """
        )
    )


async def _ensure_roles(session: AsyncSession) -> list[Role]:
    names = [name for name, _ in ROLE_SEED]
    existing = (await session.execute(select(Role).where(Role.name.in_(names)))).scalars().all()
    by_name = {r.name: r for r in existing}

    created: list[Role] = []
    for name, desc in ROLE_SEED:
        if name in by_name:
            continue
        r = Role(name=name, description=desc, is_active=True)
        session.add(r)
        created.append(r)

    if created:
        await session.flush()
        existing = (await session.execute(select(Role).where(Role.name.in_(names)))).scalars().all()

    return list(existing)


async def _ensure_professions_and_specialties(
    session: AsyncSession,
) -> tuple[list[Profession], list[Specialty]]:
    profession_names = list(PROFESSIONS_AND_SPECIALTIES.keys())
    professions = (
        (await session.execute(select(Profession).where(Profession.name.in_(profession_names))))
        .scalars()
        .all()
    )
    prof_by_name = {p.name: p for p in professions}

    for name in profession_names:
        if name in prof_by_name:
            continue
        p = Profession(name=name, description=f"Seed: {name}", is_active=True)
        session.add(p)
        prof_by_name[name] = p

    await session.flush()

    # Ensure specialties (unique per profession_id + name)
    all_specialties: list[Specialty] = []
    for prof_name, specialty_names in PROFESSIONS_AND_SPECIALTIES.items():
        prof = prof_by_name[prof_name]
        existing_specs = (
            (await session.execute(select(Specialty).where(Specialty.profession_id == prof.id)))
            .scalars()
            .all()
        )
        spec_name_set = {s.name for s in existing_specs}
        for spec_name in specialty_names:
            if spec_name in spec_name_set:
                continue
            session.add(
                Specialty(
                    profession_id=prof.id,
                    name=spec_name,
                    description=f"Seed: {spec_name}",
                    is_active=True,
                )
            )

    await session.flush()

    professions = list(
        (await session.execute(select(Profession).where(Profession.name.in_(profession_names))))
        .scalars()
        .all()
    )
    all_specialties = list((await session.execute(select(Specialty))).scalars().all())
    return professions, all_specialties


async def seed(users: int, seed: int | None, truncate: bool) -> None:
    rng = random.Random(seed)

    async with AsyncSessionLocal() as session:
        if truncate:
            await _truncate_tables(session)

        roles = await _ensure_roles(session)
        professions, specialties = await _ensure_professions_and_specialties(session)

        # If running seed multiple times without --truncate, keep unique fields collision-free
        # by continuing from the highest numeric CPF already present.
        max_cpf_num = (
            await session.execute(
                select(func.max(cast(User.cpf, BigInteger))).where(
                    cast(User.cpf, String).op("~")("^[0-9]{11}$")
                )
            )
        ).scalar_one()
        start_idx = int(max_cpf_num or 0) + 1

        specialties_by_profession: dict[Any, list[Specialty]] = {}
        for s in specialties:
            specialties_by_profession.setdefault(s.profession_id, []).append(s)

        # Create users + related entities
        created_users: list[User] = []
        for i in range(users):
            seq = start_idx + i
            first = rng.choice(FIRST_NAMES)
            last = rng.choice(LAST_NAMES)

            # Keep unique fields deterministic to avoid collisions.
            cpf = _generate_valid_cpf(seq)
            # Generate 11 digit phone: 11 (DDD) + 9 digits
            phone_digits = f"11{(900000000 + seq):09d}"  # 11 digits total

            user = User(
                first_name=first,
                last_name=last,
                is_active=(rng.random() > 0.05),
                cpf=cpf,
                email=_make_unique_email(first, last, seq),
                phone=phone_digits,  # Just the 11 digits, no country code
                profile_picture=None,
                date_of_birth=None,
                password=_sha256("Password123!"),
            )
            session.add(user)
            created_users.append(user)

        await session.flush()  # ensure user.id is available

        # Link roles, address, complementary_data, profession/specialty
        for idx, user in enumerate(created_users, start=1):
            # roles (1-2 distinct)
            role_count = 1 if rng.random() < 0.8 else 2
            picked_roles = rng.sample(roles, k=min(role_count, len(roles)))
            for r in picked_roles:
                session.add(UserRole(user_id=user.id, role_id=r.id))

            # address
            session.add(
                Address(
                    user_id=user.id,
                    zip_code=_digits(8, rng),
                    street=rng.choice(STREETS),
                    number=str(rng.randint(1, 9999)),
                    complement=None if rng.random() < 0.7 else f"Apto {rng.randint(1, 200)}",
                    neighborhood=rng.choice(NEIGHBORHOODS),
                    city=rng.choice(CITIES),
                    uf=rng.choice(UF),
                )
            )

            # complementary data
            has_disability = rng.random() < 0.05
            session.add(
                ComplementaryData(
                    user_id=user.id,
                    marital_status=rng.choice(list(MaritalStatusEnum)),
                    place_of_birth=rng.choice(CITIES),
                    nationality="BR",
                    mother_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                    father_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                    has_disability=has_disability,
                    disability="Seed: deficiência motora" if has_disability else None,
                    gender=rng.choice(list(GenderEnum)),
                    race=rng.choice(list(RaceEnum)),
                )
            )

            # profession + specialty (1 entry, primary)
            prof = rng.choice(professions)
            specs = specialties_by_profession.get(prof.id, [])
            spec = rng.choice(specs) if specs and rng.random() < 0.9 else None
            session.add(
                UserProfessionSpecialty(
                    user_id=user.id,
                    profession_id=prof.id,
                    specialty_id=spec.id if spec else None,
                    is_primary=True,
                )
            )

            # optionally add a second non-primary entry
            if rng.random() < 0.25 and len(professions) > 1:
                prof2 = rng.choice([p for p in professions if p.id != prof.id])
                specs2 = specialties_by_profession.get(prof2.id, [])
                spec2 = rng.choice(specs2) if specs2 and rng.random() < 0.9 else None
                session.add(
                    UserProfessionSpecialty(
                        user_id=user.id,
                        profession_id=prof2.id,
                        specialty_id=spec2.id if spec2 else None,
                        is_primary=False,
                    )
                )

            if idx % 200 == 0:
                # periodic flush to keep memory/locks under control for large seeds
                await session.flush()

        await session.commit()

    print(f"✅ Seed concluído: {users} usuários.")
    print("   Senha padrão (sha256): Password123!")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed database with test data.")
    p.add_argument(
        "--users", type=int, default=50, help="Quantidade de usuários a criar (default: 50)"
    )
    p.add_argument("--seed", type=int, default=None, help="Seed do RNG (reprodutibilidade)")
    p.add_argument(
        "--truncate",
        action="store_true",
        help="TRUNCATE nas tabelas (DESTRUTIVO). Use em ambiente local.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    asyncio.run(seed(users=args.users, seed=args.seed, truncate=args.truncate))


if __name__ == "__main__":
    main()

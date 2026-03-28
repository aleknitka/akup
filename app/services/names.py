from __future__ import annotations

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

ADJECTIVES = [
    "Brave", "Bright", "Calm", "Clever", "Cool", "Daring", "Eager", "Fair",
    "Fast", "Fierce", "Gentle", "Grand", "Happy", "Keen", "Kind", "Lively",
    "Lucky", "Merry", "Mighty", "Noble", "Proud", "Quick", "Quiet", "Sharp",
    "Silent", "Smooth", "Steady", "Bold", "Swift", "Tall", "True", "Vivid",
    "Warm", "Wise", "Witty", "Agile", "Alert", "Crisp", "Deft", "Fresh",
    "Glad", "Light", "Neat", "Plain", "Prime", "Rare", "Safe", "Stout",
    "Tidy", "Vast",
]

ANIMALS = [
    "Falcon", "Otter", "Panda", "Raven", "Tiger", "Eagle", "Whale", "Heron",
    "Badger", "Crane", "Gecko", "Hound", "Koala", "Lemur", "Lynx", "Moose",
    "Newt", "Owl", "Quail", "Robin", "Shark", "Stoat", "Viper", "Wolf",
    "Bison", "Coral", "Drake", "Finch", "Goose", "Hawk", "Ibis", "Jay",
    "Kite", "Lark", "Mole", "Osprey", "Pike", "Seal", "Tern", "Wren",
    "Bear", "Colt", "Dove", "Fox", "Gull", "Hare", "Mink", "Swan",
    "Toad", "Yak",
]


async def generate_display_name(db: AsyncSession, org_id: object) -> str:
    result = await db.execute(
        select(User.display_name).where(User.organization_id == org_id)
    )
    existing = set(result.scalars().all())

    candidates = [f"{adj} {animal}" for adj in ADJECTIVES for animal in ANIMALS]
    random.shuffle(candidates)

    for name in candidates:
        if name not in existing:
            return name

    # Fallback: add numeric suffix
    for i in range(1, 10000):
        adj = random.choice(ADJECTIVES)
        animal = random.choice(ANIMALS)
        name = f"{adj} {animal} {i}"
        if name not in existing:
            return name

    return f"User {random.randint(10000, 99999)}"

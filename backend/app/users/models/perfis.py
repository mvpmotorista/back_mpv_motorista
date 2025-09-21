import decimal
import uuid
from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.core.models.core import Log



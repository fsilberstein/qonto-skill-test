from typing import Literal, Optional, Dict

from pydantic import BaseModel, Field, ConfigDict


class EntityChange(BaseModel):
    """Model that describes an entity change"""

    from_value: Optional[str] = Field(None, description="Value before the change", alias="from")
    to: Optional[str] = Field(None, description="Value after the change")


class CompanyEvent(BaseModel):
    """Model that describes a company event from Kafka"""

    model_config = ConfigDict(populate_by_name=True)

    idempotency_key: str = Field(..., description="", examples=["xxxxxxxx-updated-xxxxx"])
    event: Literal["created", "updated"] = Field(..., description="Event type", examples=["created"])

    id: str = Field(
        ..., description="Id of the company represented by a uuid.", examples=["e2b1350a-c4b5-490d-bf29-47ffc6698a18"]
    )
    organization_id: str = Field(
        ...,
        description="Organization id the company belongs to. Represented by a uuid",
        examples=["9a9fce27-1234-490c-90b8-edd229327879"],
    )
    name: str = Field(None, description="name of the company")
    created_at: int = Field(
        None,
        description="Timestamp of the creation of the company in seconds",
        examples=[1606900567],
    )
    updated_at: int = Field(
        None,
        description="Timestamp of the last update of the company in seconds",
        examples=[1606900567],
    )
    changes: Dict[str, EntityChange] = Field(..., description="Changes in the event")

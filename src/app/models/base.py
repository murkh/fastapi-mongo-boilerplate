from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel as PydanticBaseModel, Field, field_validator, ConfigDict


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return handler(ObjectId)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseModel(PydanticBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Optional[object]) -> PyObjectId | object | None:
        if isinstance(v, str):
            return PyObjectId(v)
        return v

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from ..core.database import get_database
from ..models.base import BaseModel as BaseModelWithId

ModelType = TypeVar("ModelType", bound=BaseModelWithId)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations and aggregation support."""

    def __init__(self, model: Type[ModelType], collection_name: str):
        self.model = model
        self.collection_name = collection_name
        self.collection: AsyncIOMotorCollection = get_database()[collection_name]

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new document."""
        obj_data = obj_in.model_dump()
        result = await self.collection.insert_one(obj_data)
        obj_data["_id"] = result.inserted_id
        return self.model(**obj_data)

    async def get(self, id: str) -> Optional[ModelType]:
        """Get a document by ID."""
        if not ObjectId.is_valid(id):
            return None
        obj_data = await self.collection.find_one({"_id": ObjectId(id)})
        if obj_data:
            return self.model(**obj_data)
        return None

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple documents with pagination."""
        cursor = self.collection.find().skip(skip).limit(limit)
        documents: List[Dict[str, Any]] = await cursor.to_list(length=limit)
        return [self.model(**doc) for doc in documents]

    async def update(self, *, id: str, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update a document."""
        if not ObjectId.is_valid(id):
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = update_data.get("updated_at")
            result = await self.collection.update_one(
                {"_id": ObjectId(id)}, {"$set": update_data}
            )
            if result.modified_count:
                return await self.get(id)
        return None

    async def delete(self, *, id: str) -> bool:
        """Delete a document."""
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return bool(result.deleted_count)

    async def count(self) -> int:
        """Count total documents in collection."""
        count: int = await self.collection.count_documents({})
        return count

    async def exists(self, id: str) -> bool:
        """Check if document exists."""
        if not ObjectId.is_valid(id):
            return False
        result: int = await self.collection.count_documents({"_id": ObjectId(id)})
        return result > 0

    # Aggregation Pipeline Methods
    async def aggregate(
        self, pipeline: List[Dict[str, Any]], allow_disk_use: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute an aggregation pipeline.

        Args:
            pipeline: List of aggregation stages
            allow_disk_use: Whether to allow disk use for large operations

        Returns:
            List of aggregation results
        """
        try:
            cursor = self.collection.aggregate(pipeline, allowDiskUse=allow_disk_use)
            results: List[Dict[str, Any]] = await cursor.to_list(length=None)
            return results
        except Exception as e:
            # Log the error in production
            print(f"Aggregation error: {e}")
            return []

    async def aggregate_with_model(
        self,
        pipeline: List[Dict[str, Any]],
        model_class: Optional[Type[ModelType]] = None,
        allow_disk_use: bool = False,
    ) -> List[ModelType]:
        """
        Execute an aggregation pipeline and return results as model instances.

        Args:
            pipeline: List of aggregation stages
            model_class: Model class to instantiate results (defaults to self.model)
            allow_disk_use: Whether to allow disk use for large operations

        Returns:
            List of model instances
        """
        model = model_class or self.model
        results = await self.aggregate(pipeline, allow_disk_use)
        return [model(**doc) for doc in results]

    async def aggregate_single(
        self, pipeline: List[Dict[str, Any]], allow_disk_use: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Execute an aggregation pipeline and return the first result.

        Args:
            pipeline: List of aggregation stages
            allow_disk_use: Whether to allow disk use for large operations

        Returns:
            First aggregation result or None
        """
        results = await self.aggregate(pipeline, allow_disk_use)
        return results[0] if results else None

    async def aggregate_count(
        self, pipeline: List[Dict[str, Any]], allow_disk_use: bool = False
    ) -> int:
        """
        Execute an aggregation pipeline and return the count.

        Args:
            pipeline: List of aggregation stages
            allow_disk_use: Whether to allow disk use for large operations

        Returns:
            Count from aggregation result
        """
        # Add $count stage to the end of the pipeline
        count_pipeline = pipeline + [{"$count": "total"}]
        result = await self.aggregate_single(count_pipeline, allow_disk_use)
        return int(result.get("total", 0) if result else 0)

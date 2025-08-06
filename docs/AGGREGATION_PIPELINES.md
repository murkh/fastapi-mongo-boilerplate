# Aggregation Pipelines in FastAPI MongoDB Boilerplate

This document explains how to use MongoDB aggregation pipelines in the FastAPI MongoDB boilerplate, following best practices and the repository pattern.

## Overview

Aggregation pipelines are powerful MongoDB features that allow you to process documents and return computed results. Our boilerplate provides a clean, type-safe way to use aggregation pipelines through the repository pattern.

## Architecture

```
API Layer (FastAPI) → Service Layer → Repository Layer → MongoDB Aggregation Pipeline
```

## Base Repository Aggregation Methods

The `BaseRepository` class provides several methods for executing aggregation pipelines:

### 1. `aggregate(pipeline, allow_disk_use=False)`
Execute a raw aggregation pipeline and return results as dictionaries.

```python
pipeline = [
    {"$match": {"is_active": True}},
    {"$group": {"_id": "$department", "count": {"$sum": 1}}}
]
results = await repository.aggregate(pipeline)
```

### 2. `aggregate_with_model(pipeline, model_class=None, allow_disk_use=False)`
Execute an aggregation pipeline and return results as model instances.

```python
pipeline = [{"$match": {"is_active": True}}]
users = await repository.aggregate_with_model(pipeline, User)
```

### 3. `aggregate_single(pipeline, allow_disk_use=False)`
Execute an aggregation pipeline and return the first result.

```python
pipeline = [{"$count": "total"}]
result = await repository.aggregate_single(pipeline)
total = result.get("total", 0) if result else 0
```

### 4. `aggregate_count(pipeline, allow_disk_use=False)`
Execute an aggregation pipeline and return the count.

```python
pipeline = [{"$match": {"is_active": True}}]
count = await repository.aggregate_count(pipeline)
```

## User Repository Aggregation Examples

### 1. User Statistics (`get_user_statistics`)

**Purpose**: Get comprehensive user statistics using `$facet` to run multiple aggregations in parallel.

**Pipeline**:
```javascript
[
  {
    "$facet": {
      "total_users": [{"$count": "count"}],
      "active_users": [
        {"$match": {"is_active": true}},
        {"$count": "count"}
      ],
      "superusers": [
        {"$match": {"is_superuser": true}},
        {"$count": "count"}
      ],
      "users_by_month": [
        {
          "$group": {
            "_id": {
              "year": {"$year": "$created_at"},
              "month": {"$month": "$created_at"}
            },
            "count": {"$sum": 1}
          }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
      ],
      "average_username_length": [
        {
          "$group": {
            "_id": null,
            "avg_length": {"$avg": {"$strLenCP": "$username"}}
          }
        }
      ]
    }
  }
]
```

**Usage**:
```python
stats = await user_service.get_user_statistics()
print(f"Total users: {stats['total_users']}")
print(f"Active users: {stats['active_users']}")
```

### 2. Users by Activity Status (`get_users_by_activity_status`)

**Purpose**: Group users by activity status with sample users from each group.

**Pipeline**:
```javascript
[
  {
    "$group": {
      "_id": "$is_active",
      "users": {
        "$push": {
          "id": "$_id",
          "username": "$username",
          "email": "$email",
          "full_name": "$full_name",
          "created_at": "$created_at"
        }
      },
      "count": {"$sum": 1}
    }
  },
  {
    "$project": {
      "status": {
        "$cond": {
          "if": "$_id",
          "then": "active",
          "else": "inactive"
        }
      },
      "count": 1,
      "users": {"$slice": ["$users", limit]}
    }
  },
  {"$sort": {"count": -1}}
]
```

**Usage**:
```python
activity_groups = await user_service.get_users_by_activity_status(limit=5)
for group in activity_groups:
    print(f"{group['status']}: {group['count']} users")
```

### 3. Recent Users with Details (`get_recent_users_with_details`)

**Purpose**: Get recent users with computed fields like days since creation and email domain.

**Pipeline**:
```javascript
[
  {
    "$match": {
      "created_at": {"$gte": cutoff_date}
    }
  },
  {
    "$addFields": {
      "days_since_created": {
        "$floor": {
          "$divide": [
            {"$subtract": [new Date(), "$created_at"]},
            1000 * 60 * 60 * 24
          ]
        }
      },
      "has_full_name": {"$ne": ["$full_name", null]},
      "email_domain": {
        "$substr": ["$email", {"$indexOfBytes": ["$email", "@"]}, -1]
      }
    }
  },
  {
    "$project": {
      "_id": 1,
      "username": 1,
      "email": 1,
      "full_name": 1,
      "is_active": 1,
      "is_superuser": 1,
      "created_at": 1,
      "days_since_created": 1,
      "has_full_name": 1,
      "email_domain": 1
    }
  },
  {"$sort": {"created_at": -1}}
]
```

**Usage**:
```python
recent_users = await user_service.get_recent_users_with_details(days=30)
for user in recent_users:
    print(f"{user['username']} created {user['days_since_created']} days ago")
```

### 4. User Growth Trend (`get_user_growth_trend`)

**Purpose**: Analyze user growth over time with monthly breakdowns.

**Pipeline**:
```javascript
[
  {
    "$match": {
      "created_at": {"$gte": start_date, "$lte": end_date}
    }
  },
  {
    "$group": {
      "_id": {
        "year": {"$year": "$created_at"},
        "month": {"$month": "$created_at"}
      },
      "new_users": {"$sum": 1},
      "active_users": {
        "$sum": {"$cond": ["$is_active", 1, 0]}
      },
      "superusers": {
        "$sum": {"$cond": ["$is_superuser", 1, 0]}
      }
    }
  },
  {
    "$project": {
      "_id": 0,
      "year": "$_id.year",
      "month": "$_id.month",
      "new_users": 1,
      "active_users": 1,
      "superusers": 1,
      "month_name": {
        "$switch": {
          "branches": [
            {"case": {"$eq": ["$_id.month", 1]}, "then": "January"},
            // ... other months
          ],
          "default": "Unknown"
        }
      }
    }
  },
  {"$sort": {"year": 1, "month": 1}}
]
```

**Usage**:
```python
growth_trend = await user_service.get_user_growth_trend(months=12)
for month in growth_trend:
    print(f"{month['month_name']} {month['year']}: {month['new_users']} new users")
```

### 5. Advanced Search (`search_users_advanced`)

**Purpose**: Advanced search with pagination, filtering, and faceting.

**Pipeline**:
```javascript
[
  {
    "$match": {
      "$or": [
        {"username": {"$regex": search_term, "$options": "i"}},
        {"email": {"$regex": search_term, "$options": "i"}},
        {"full_name": {"$regex": search_term, "$options": "i"}}
      ],
      // Additional filters
    }
  },
  {
    "$facet": {
      "data": [
        {"$sort": {sort_by: sort_order}},
        {"$skip": skip},
        {"$limit": limit},
        {
          "$project": {
            "_id": 1,
            "username": 1,
            "email": 1,
            "full_name": 1,
            "is_active": 1,
            "is_superuser": 1,
            "created_at": 1,
            "updated_at": 1
          }
        }
      ],
      "total": [{"$count": "count"}],
      "facets": [
        {
          "$group": {
            "_id": "$is_active",
            "count": {"$sum": 1}
          }
        }
      ]
    }
  }
]
```

**Usage**:
```python
search_results = await user_service.search_users_advanced(
    search_term="john",
    filters={"is_active": True},
    limit=20,
    skip=0
)
print(f"Found {search_results['total']} users")
```

## API Endpoints

The boilerplate provides REST API endpoints for aggregation pipelines:

### Analytics Endpoints

- `GET /api/v1/users/analytics/statistics` - User statistics
- `GET /api/v1/users/analytics/activity-status` - Users by activity status
- `GET /api/v1/users/analytics/recent-users` - Recent users with details
- `GET /api/v1/users/analytics/growth-trend` - User growth trend
- `GET /api/v1/users/search/advanced` - Advanced search

### Example API Usage

```bash
# Get user statistics
curl "http://localhost:8000/api/v1/users/analytics/statistics"

# Get recent users
curl "http://localhost:8000/api/v1/users/analytics/recent-users?days=30"

# Advanced search
curl "http://localhost:8000/api/v1/users/search/advanced?search_term=john&is_active=true&limit=10"
```

## Best Practices

### 1. Performance Optimization

- **Use indexes**: Ensure proper indexes for fields used in `$match` stages
- **Limit results**: Use `$limit` to prevent large result sets
- **Allow disk use**: For large datasets, set `allow_disk_use=True`
- **Pipeline optimization**: Place `$match` stages early to reduce documents processed

### 2. Error Handling

```python
try:
    results = await repository.aggregate(pipeline)
except Exception as e:
    logger.error(f"Aggregation failed: {e}")
    return []
```

### 3. Type Safety

```python
from typing import List, Dict, Any

async def get_user_stats() -> Dict[str, Any]:
    pipeline = [...]
    return await repository.aggregate_single(pipeline)
```

### 4. Testing

```python
@pytest.mark.asyncio
async def test_aggregation():
    with patch.object(repository, 'aggregate', return_value=mock_result):
        result = await repository.get_user_statistics()
        assert result["total_users"] == 100
```

## Common Aggregation Patterns

### 1. Counting Documents
```python
pipeline = [{"$count": "total"}]
result = await repository.aggregate_single(pipeline)
count = result.get("total", 0) if result else 0
```

### 2. Grouping and Counting
```python
pipeline = [
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
```

### 3. Computing Averages
```python
pipeline = [
    {"$group": {"_id": None, "avg_value": {"$avg": "$field"}}}
]
```

### 4. Date-based Aggregations
```python
pipeline = [
    {
        "$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"}
            },
            "count": {"$sum": 1}
        }
    }
]
```

### 5. Text Search with Faceting
```python
pipeline = [
    {
        "$match": {
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        }
    },
    {
        "$facet": {
            "data": [{"$limit": 10}],
            "total": [{"$count": "count"}],
            "categories": [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ]
        }
    }
]
```

## Performance Monitoring

Monitor aggregation performance using MongoDB's built-in tools:

```python
# Enable query logging
pipeline = [{"$explain": True}] + your_pipeline
explanation = await repository.aggregate(pipeline)
```

## Conclusion

The aggregation pipeline support in this boilerplate provides:

- **Type safety** with proper typing
- **Error handling** with graceful fallbacks
- **Performance optimization** with configurable options
- **Clean architecture** following repository pattern
- **Comprehensive testing** with mocked results
- **REST API endpoints** for easy consumption

This approach makes MongoDB aggregation pipelines accessible, maintainable, and performant in FastAPI applications. 
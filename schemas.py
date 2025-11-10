"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (you can keep these examples for reference)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Movie app schema used by the application
class Movie(BaseModel):
    """
    Movies collection schema
    Collection name: "movie"
    """
    title: str = Field(..., min_length=1, max_length=200, description="Movie title")
    description: Optional[str] = Field("", max_length=2000, description="Movie description")
    rating: float = Field(..., ge=0, le=10, description="Rating from 0 to 10")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    genres: Optional[List[str]] = Field(default=None, description="List of genres")

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app import db

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    category: Mapped[Optional[str]] = mapped_column(Enum("news", "publication", "tech", "other"))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    author: Mapped[Optional[str]] = mapped_column(String(20), default="Anonymous")

    def __repr__(self):
        return f"<Post(title={self.title})>"
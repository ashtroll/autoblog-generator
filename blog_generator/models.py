from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class Topic(BaseModel):
    title: str
    description: str = ""
    source_urls: List[str] = Field(default_factory=list)
    score: float = 0.0


class QualityReport(BaseModel):
    quality_score: int
    seo_score: int
    pass_: bool = Field(alias="pass")
    meta_description: str
    tags: List[str] = Field(default_factory=list)
    slug: str
    estimated_read_time: str
    issues: List[str] = Field(default_factory=list)
    rewrite_instructions: Optional[str] = None

    model_config = {"populate_by_name": True}


class BlogPost(BaseModel):
    topic: Topic
    title: str
    content_md: str
    content_html: str = ""
    meta: QualityReport
    needs_review: bool = False

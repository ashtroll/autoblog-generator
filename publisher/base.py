from abc import ABC, abstractmethod
from blog_generator.models import BlogPost


class BasePublisher(ABC):
    @abstractmethod
    def publish(self, blog: BlogPost) -> dict:
        """Publish a blog post and return platform response data."""

    @classmethod
    @abstractmethod
    def from_config(cls) -> "BasePublisher":
        """Construct publisher from environment variables."""

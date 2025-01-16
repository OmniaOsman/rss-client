from django.db import models
from accounts.models import User
import re
from pgvector.django import VectorField,HnswIndex
from sources.models import Source


# def arabic_slugify(str):
#     """
#     Custom slugify function that handles Arabic text by transliterating Arabic characters
#     to their closest English representation.
#     """
#     arabic_map = {
#         'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
#         'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's',
#         'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
#         'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y',
#         'ة': 'h', 'ى': 'a', 'ء': 'a', 'ؤ': 'o', 'ئ': 'e', 'إ': 'e', 'أ': 'a',
#         'آ': 'a', 'ض': 'd', 'ص': 's', 'ث': 'th', 'ق': 'q', 'ف': 'f', 'غ': 'gh',
#         'ع': 'a', 'ه': 'h', 'خ': 'kh', 'ح': 'h', 'ج': 'j', 'ش': 'sh', 'س': 's',
#         'ي': 'y', 'ب': 'b', 'ل': 'l', 'ا': 'a', 'ت': 't', 'ن': 'n', 'م': 'm',
#         'ك': 'k', 'ط': 't', 'ذ': 'th', 'ء': 'a', 'ؤ': 'o', 'ر': 'r', 'ى': 'a',
#         'ة': 'h', 'و': 'w', 'ز': 'z', 'ظ': 'z',
#     }

# # Convert Arabic characters to English representations
# str = ''.join(arabic_map.get(char, char) for char in str)

# # Remove non-word characters and convert spaces to hyphens
# str = re.sub(r'[^\w\s-]', '', str).strip().lower()
# str = re.sub(r'[-\s]+', '-', str)

# return str or 'untitled'


class TagCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="tag category name")
    # slug = models.SlugField(max_length=100, unique=True, help_text='tag category slug')
    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = arabic_slugify(self.name)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, help_text="tag name")
    # slug = models.SlugField(max_length=100, unique=True, help_text='tag slug')
    category = models.ForeignKey(
        TagCategory,
        on_delete=models.SET_NULL,
        related_name="tags",
        null=True,
        help_text="tag category",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = arabic_slugify(self.name)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["name", "category"]


class Feed(models.Model):
    title = models.CharField(max_length=500, help_text="feed title")
    url = models.URLField(max_length=5000, help_text="rss url")
    description = models.TextField(null=True, help_text="feed description")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="feeds",
        null=True,
        help_text="user associated with the feed",
    )
    tags = models.ManyToManyField(
        Tag, related_name="feeds", help_text="tags associated with the feed"
    )
    active = models.BooleanField(default=True, help_text="feed is still active or not")
    external_id = models.CharField(
        max_length=5000, help_text="ID from the original news source"
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        related_name="feeds",
        null=True,
        help_text="source associated with the feed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    #feed embedding
    embedding = VectorField(dimensions=1536)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ("user", "url", "external_id")
        indexes = [
            models.Index(fields=["user", "url"], name="user_url_index"),
            HnswIndex(
                    name="embedding_vectors_index",
                    fields=["embedding"],
                    m=16,
                    ef_construction=64,
                    opclasses=["vector_cosine_ops"],
                ),
        ]


class ProcessedFeed(models.Model):
    title = models.CharField(max_length=500, help_text="processed feed title")
    summary = models.TextField(help_text="processed feed summary")
    references = models.JSONField(help_text="processed feed references")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="processed_feeds",
        null=True,
        help_text="user associated with the processed feed",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




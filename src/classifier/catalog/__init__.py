"""Mục lục thư mục chuẩn — dựng TRƯỚC mọi bước phân loại."""
from classifier.catalog.schema import Catalog, Section, Slot
from classifier.catalog.loader import build_catalog, load_profile

__all__ = ["Catalog", "Section", "Slot", "build_catalog", "load_profile"]

"""Đầu vào — chuẩn hoá mọi kiểu nguồn về ``list[Photo]`` + file đi kèm."""
from classifier.intake.photo import Batch, Photo
from classifier.intake.sources import read_source

__all__ = ["Batch", "Photo", "read_source"]

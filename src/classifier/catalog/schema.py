"""Kiểu dữ liệu của mục lục. Thuần — không I/O."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Slot:
    """1 thư mục con của mục lục: ``hm/template``; template có thể còn 1 biến (``{mong}``…)
    mà giá trị phải lấy từ bằng chứng (ảnh / tên file), không đoán."""
    hm: str                                       # thư mục hạng mục, vd "3.Công tác kiểm tra …"
    template: str                                 # tên thư mục con (có thể chứa "{var}")
    var: str | None = None
    values: list[str] = field(default_factory=list)
    hint: str = ""                                # ảnh trông thế nào ([vision.hints])
    is_khac: bool = False

    @property
    def option(self) -> str:
        """Khoá lựa chọn (mẫu chưa điền biến)."""
        return f"{self.hm}/{self.template}"

    def fill(self, value: str | None) -> str | None:
        """Thư mục cụ thể; biến không có giá trị hợp lệ → ``None``."""
        if self.var is None:
            return self.option
        if value is None:
            return None
        v = str(value).strip().casefold()
        hit = next((x for x in self.values if x.casefold() == v), None)
        return f"{self.hm}/{self.template.replace('{' + self.var + '}', hit)}" if hit else None

    def leaves(self) -> list[str]:
        return [self.option] if self.var is None else [self.fill(v) for v in self.values]


@dataclass
class Section:
    no: int
    folder: str                                   # "n.Tên hạng mục"
    slots: list[Slot] = field(default_factory=list)

    @property
    def khac(self) -> Slot:
        return next(s for s in self.slots if s.is_khac)


@dataclass
class Catalog:
    sections: list[Section]
    root_khac: str                                # "Hình ảnh khác" ở gốc trạm

    @property
    def slots(self) -> list[Slot]:
        return [s for sec in self.sections for s in sec.slots]

    def by_option(self) -> dict[str, Slot]:
        return {s.option: s for s in self.slots}

    def section_of(self, folder: str) -> Section | None:
        hm = folder.split("/", 1)[0]
        return next((s for s in self.sections if s.folder == hm), None)

    def leaves(self) -> list[str]:
        out = dict.fromkeys(leaf for s in self.slots for leaf in s.leaves())
        out.setdefault(self.root_khac, None)
        return list(out)

    def fingerprint(self) -> str:
        import hashlib
        text = "\n".join(f"{s.option}|{s.values}|{s.hint}" for s in self.slots)
        return hashlib.sha1(text.encode()).hexdigest()[:10]

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegionRecord:
    region_id: str
    status: str = "established"


class RegionRegistry:
    def __init__(self, records: list[RegionRecord] | None = None) -> None:
        self._records = {record.region_id: record for record in (records or [])}

    @classmethod
    def seed(cls) -> "RegionRegistry":
        return cls([
            RegionRecord("human-auditory"),
            RegionRecord("atmospheric-acoustic"),
            RegionRecord("underwater-acoustic"),
            RegionRecord("solid-earth-vibration"),
            RegionRecord("structural-vibration"),
            RegionRecord("ultrasonic"),
            RegionRecord("infrasonic"),
            RegionRecord("rendered-sonified"),
            RegionRecord("unknown-mechanical", status="provisional"),
        ])

    def ids(self) -> set[str]:
        return set(self._records)

    def get(self, region_id: str) -> RegionRecord:
        return self._records[region_id]


@dataclass(frozen=True, slots=True)
class MethodRecord:
    method_id: str
    evidence_level: str = "L1"


class MethodRegistry:
    def __init__(self, records: list[MethodRecord] | None = None) -> None:
        self._records = {record.method_id: record for record in (records or [])}

    @classmethod
    def seed(cls) -> "MethodRegistry":
        return cls([
            MethodRecord("periodicity-estimator"),
            MethodRecord("farhp", evidence_level="L2"),
            MethodRecord("noise-estimator"),
            MethodRecord("transient-detector"),
            MethodRecord("residual-structure-analyzer"),
        ])

    def ids(self) -> set[str]:
        return set(self._records)

    def get(self, method_id: str) -> MethodRecord:
        return self._records[method_id]

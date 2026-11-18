"""Validasi granularitas periode sebelum data masuk ke Silver."""

from __future__ import annotations

import re
from collections.abc import Iterable


class PeriodeTidakTahunan(ValueError):
    """Periode mentah bukan tahunan sehingga tidak boleh diubah menjadi tahunan."""


def _nilai_berbeda(nilai: Iterable[object]) -> list[str]:
    return sorted({str(item).strip() for item in nilai})


def _nilai_tidak_sesuai(nilai: Iterable[object], predikat) -> list[str]:
    return [
        item
        for item in _nilai_berbeda(nilai)
        if not predikat(item)
    ]


def validasi_periode_bps(periode: Iterable[object], seri: str) -> None:
    """Pastikan seluruh nilai kolom Periode BPS adalah Tahun."""
    salah = _nilai_tidak_sesuai(periode, lambda item: item.casefold() == "tahun")
    if salah:
        raise PeriodeTidakTahunan(
            f"{seri}: periode BPS non-tahunan ditemukan: {', '.join(salah)}"
        )


def validasi_periode_wdi(tanggal: Iterable[object], seri: str) -> None:
    """Pastikan seluruh tanggal WDI berupa tahun empat digit."""
    salah = _nilai_tidak_sesuai(
        tanggal,
        lambda item: re.fullmatch(r"\d{4}", item) is not None,
    )
    if salah:
        raise PeriodeTidakTahunan(
            f"{seri}: periode WDI non-tahunan ditemukan: {', '.join(salah)}"
        )


def validasi_periode_who(time_type: Iterable[object], seri: str) -> None:
    """Pastikan seluruh DIM_TIME_TYPE WHO GHO adalah YEAR."""
    salah = _nilai_tidak_sesuai(time_type, lambda item: item.upper() == "YEAR")
    if salah:
        raise PeriodeTidakTahunan(
            f"{seri}: periode WHO non-tahunan ditemukan: {', '.join(salah)}"
        )

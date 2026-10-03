"""
year_dossier.py — deep year-wise analysis generator.

Generates an analytical yearly dossier from PRODUCTION data only. Every
astronomical value is read from kundali_data.json / risk_timeline.json or
recomputed with the same engine; nothing is invented.

LANGUAGE RULES (enforced):
  * No death prediction, no disease diagnosis, no guaranteed financial outcome.
  * "may correspond with", "traditional interpretation suggests", "attention is
    warranted around" - never "this WILL happen".
  * Confidence labels describe calculation/interpretation STABILITY, never the
    probability of an event.
  * D9 and D7 conclusions are labelled TIME-SENSITIVE because both lagnas move
    inside a +/-15 minute birth-time window.
  * Numerology is NOT counted as independent astronomical evidence.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import swisseph as swe                                   # noqa: E402
import kundali_core as K                                  # noqa: E402

OUT = os.path.join(HERE, "out")

HOUSE_THEMES = {
    1: "self, body, identity, vitality",
    2: "money, speech, family of origin, savings",
    3: "skill, communication, courage, effort, siblings",
    4: "home, property, mother, comfort, inner peace",
    5: "learning, children, creativity, speculation",
    6: "work, service, debt, conflict, daily routine, health",
    7: "marriage, partnership, contracts, the other",
    8: "transformation, shared resources, obligations of others",
    9: "luck, dharma, teachers, long journeys, belief",
    10: "career, status, public standing, authority",
    11: "gains, network, income, fulfilment of ambition",
    12: "expense, foreign, retreat, loss, letting go",
}

SIGNS = K.SIGNS


class Chart:
    """Production natal chart, loaded once."""

    def __init__(self):
        with open(os.path.join(OUT, "kundali_data.json"), encoding="utf-8") as fh:
            self.ds = json.load(fh)
        self.P = {p["body"]: p for p in self.ds["planets"]}
        a = self.ds["ascendant"]
        self.asc_lon = a["longitude_sidereal"]
        self.asc_sign = K.sign_of(self.asc_lon)
        self.asc_deg = a["degree_in_sign"]
        self.asc_nak = a.get("nakshatra") or K.nakshatra_of(self.asc_lon)[1]
        self.asc_pada = a.get("nakshatra_pada") or K.nakshatra_of(self.asc_lon)[3]
        self.lords = {h: K.SIGN_LORDS[(self.asc_sign + h - 1) % 12]
                      for h in range(1, 13)}
        self.lord_sign = {n: K.sign_of(self.P[n]["longitude_sidereal"])
                          for n in self.P if n != "Ascendant"}
        self.moon_sign = K.sign_of(self.P["Moon"]["longitude_sidereal"])
        self.moon_deg = self.P["Moon"]["degree_in_sign"]

    def house(self, body):
        return self.P[body]["house_whole_sign"]

    def nak(self, body):
        p = self.P[body]
        return p.get("nakshatra"), p.get("nakshatra_pada")

    def lord_house(self, h):
        return self.house(self.lords[h]) if self.lords[h] in self.P else None


def transit_sign_on(pid, y, m, d):
    tot = d - 5.5 * 3600
    sh, rem = int(tot // 86400), tot % 86400
    base = datetime.date(y, m, 1) + datetime.timedelta(days=sh)
    jd = swe.julday(base.year, base.month, base.day, rem / 3600.0)
    ay = swe.get_ayanamsa_ut(jd)
    return K.sign_of((swe.calc_ut(jd, pid, FL)[0][0] - ay) % 360)


def crossing_date(pid, y0, m0, d0, y1, m1, d1):
    def jd_of(y, m, d):
        tot = d - 5.5 * 3600
        sh, rem = int(tot // 86400), tot % 86400
        b = datetime.date(y, m, 1) + datetime.timedelta(days=sh)
        return swe.julday(b.year, b.month, b.day, rem / 3600.0)

    def sidx(j):
        return transit_sign_on(pid, *_swe_rev(j))

    a, b = jd_of(y0, m0, d0), jd_of(y1, m1, d1)
    sa = sidx(a)
    if sidx(b) == sa:
        return None
    for _ in range(50):
        mid = (a + b) / 2
        if sidx(mid) == sa:
            a = mid
        else:
            b = mid
        if abs(b - a) < 1e-8:
            break
    r = swe.revjul((a + b) / 2, swe.GREG_CAL)
    frac = ((a + b) / 2) % 1
    return (datetime.date(int(r[0]), int(r[1]), int(r[2])),
            int(frac * 24), int((frac * 24 % 1) * 60))


def _swe_rev(j):
    r = swe.revjul(j, swe.GREG_CAL)
    return int(r[0]), int(r[1]), int(r[2])


FL = swe.FLG_SWIEPH | swe.FLG_SPEED
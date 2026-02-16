# Prana Guru - Vedic Astrology Calculations
# In-house calculations for Kundali, Numerology, and Compatibility

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Constants
AYANAMSA_2000 = 23.856  # Lahiri Ayanamsa at J2000.0
AYANAMSA_RATE = 50.29 / 3600  # degrees per year

RASHIS = [
    {"name": "Mesha", "english": "Aries", "lord": "Mars", "element": "Fire"},
    {"name": "Vrishabha", "english": "Taurus", "lord": "Venus", "element": "Earth"},
    {"name": "Mithuna", "english": "Gemini", "lord": "Mercury", "element": "Air"},
    {"name": "Karka", "english": "Cancer", "lord": "Moon", "element": "Water"},
    {"name": "Simha", "english": "Leo", "lord": "Sun", "element": "Fire"},
    {"name": "Kanya", "english": "Virgo", "lord": "Mercury", "element": "Earth"},
    {"name": "Tula", "english": "Libra", "lord": "Venus", "element": "Air"},
    {"name": "Vrishchika", "english": "Scorpio", "lord": "Mars", "element": "Water"},
    {"name": "Dhanu", "english": "Sagittarius", "lord": "Jupiter", "element": "Fire"},
    {"name": "Makara", "english": "Capricorn", "lord": "Saturn", "element": "Earth"},
    {"name": "Kumbha", "english": "Aquarius", "lord": "Saturn", "element": "Air"},
    {"name": "Meena", "english": "Pisces", "lord": "Jupiter", "element": "Water"},
]

NAKSHATRAS = [
    {"name": "Ashwini", "lord": "Ketu", "deity": "Ashwini Kumaras"},
    {"name": "Bharani", "lord": "Venus", "deity": "Yama"},
    {"name": "Krittika", "lord": "Sun", "deity": "Agni"},
    {"name": "Rohini", "lord": "Moon", "deity": "Brahma"},
    {"name": "Mrigashira", "lord": "Mars", "deity": "Soma"},
    {"name": "Ardra", "lord": "Rahu", "deity": "Rudra"},
    {"name": "Punarvasu", "lord": "Jupiter", "deity": "Aditi"},
    {"name": "Pushya", "lord": "Saturn", "deity": "Brihaspati"},
    {"name": "Ashlesha", "lord": "Mercury", "deity": "Nagas"},
    {"name": "Magha", "lord": "Ketu", "deity": "Pitris"},
    {"name": "Purva Phalguni", "lord": "Venus", "deity": "Bhaga"},
    {"name": "Uttara Phalguni", "lord": "Sun", "deity": "Aryaman"},
    {"name": "Hasta", "lord": "Moon", "deity": "Savitar"},
    {"name": "Chitra", "lord": "Mars", "deity": "Vishwakarma"},
    {"name": "Swati", "lord": "Rahu", "deity": "Vayu"},
    {"name": "Vishakha", "lord": "Jupiter", "deity": "Indra-Agni"},
    {"name": "Anuradha", "lord": "Saturn", "deity": "Mitra"},
    {"name": "Jyeshtha", "lord": "Mercury", "deity": "Indra"},
    {"name": "Mula", "lord": "Ketu", "deity": "Nirriti"},
    {"name": "Purva Ashadha", "lord": "Venus", "deity": "Apas"},
    {"name": "Uttara Ashadha", "lord": "Sun", "deity": "Vishvedevas"},
    {"name": "Shravana", "lord": "Moon", "deity": "Vishnu"},
    {"name": "Dhanishta", "lord": "Mars", "deity": "Vasus"},
    {"name": "Shatabhisha", "lord": "Rahu", "deity": "Varuna"},
    {"name": "Purva Bhadrapada", "lord": "Jupiter", "deity": "Aja Ekapada"},
    {"name": "Uttara Bhadrapada", "lord": "Saturn", "deity": "Ahir Budhnya"},
    {"name": "Revati", "lord": "Mercury", "deity": "Pushan"},
]

# Vimshottari Dasha periods in years
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


def julian_day(year: int, month: int, day: int, hour: float = 0) -> float:
    """Calculate Julian Day Number"""
    if month <= 2:
        year -= 1
        month += 12
    
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    
    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour/24 + B - 1524.5
    return JD


def get_ayanamsa(jd: float) -> float:
    """Calculate Lahiri Ayanamsa for given Julian Day"""
    # J2000.0 = JD 2451545.0
    years_from_2000 = (jd - 2451545.0) / 365.25
    return AYANAMSA_2000 + (AYANAMSA_RATE * years_from_2000)


def calculate_lagna(jd: float, lat: float, lon: float) -> float:
    """
    Calculate Lagna (Ascendant) - simplified calculation
    Returns sidereal longitude in degrees
    """
    # Calculate Local Sidereal Time
    T = (jd - 2451545.0) / 36525  # Julian centuries from J2000.0
    
    # Greenwich Mean Sidereal Time in degrees
    GMST = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T**2
    GMST = GMST % 360
    
    # Local Sidereal Time
    LST = GMST + lon
    LST = LST % 360
    
    # Obliquity of ecliptic
    epsilon = 23.439291 - 0.0130042 * T
    
    # Convert to radians
    LST_rad = math.radians(LST)
    lat_rad = math.radians(lat)
    eps_rad = math.radians(epsilon)
    
    # Calculate Ascendant (tropical)
    y = math.sin(LST_rad)
    x = math.cos(LST_rad) * math.cos(eps_rad) - math.tan(lat_rad) * math.sin(eps_rad)
    
    asc_tropical = math.degrees(math.atan2(y, x))
    if asc_tropical < 0:
        asc_tropical += 360
    
    # Convert to sidereal
    ayanamsa = get_ayanamsa(jd)
    asc_sidereal = (asc_tropical - ayanamsa) % 360
    
    return asc_sidereal


def calculate_sun_position(jd: float) -> float:
    """Calculate Sun's sidereal longitude (simplified)"""
    # Days from J2000.0
    n = jd - 2451545.0
    
    # Mean longitude
    L = (280.460 + 0.9856474 * n) % 360
    
    # Mean anomaly
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    
    # Ecliptic longitude (tropical)
    lambda_sun = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
    
    # Convert to sidereal
    ayanamsa = get_ayanamsa(jd)
    return (lambda_sun - ayanamsa) % 360


def calculate_moon_position(jd: float) -> float:
    """Calculate Moon's sidereal longitude (simplified)"""
    # Days from J2000.0
    n = jd - 2451545.0
    
    # Moon's mean longitude
    L = (218.316 + 13.176396 * n) % 360
    
    # Moon's mean anomaly
    M = math.radians((134.963 + 13.064993 * n) % 360)
    
    # Moon's mean elongation
    D = math.radians((297.850 + 12.190749 * n) % 360)
    
    # Ecliptic longitude (tropical) - simplified
    lambda_moon = L + 6.289 * math.sin(M)
    
    # Convert to sidereal
    ayanamsa = get_ayanamsa(jd)
    return (lambda_moon - ayanamsa) % 360


def get_rashi(longitude: float) -> Dict:
    """Get Rashi details from longitude"""
    rashi_index = int(longitude / 30) % 12
    degree_in_rashi = longitude % 30
    return {
        "index": rashi_index,
        **RASHIS[rashi_index],
        "degree": round(degree_in_rashi, 2)
    }


def get_nakshatra(moon_longitude: float) -> Dict:
    """Get Nakshatra details from Moon's longitude"""
    nakshatra_span = 360 / 27  # 13.333... degrees each
    nakshatra_index = int(moon_longitude / nakshatra_span) % 27
    pada = int((moon_longitude % nakshatra_span) / (nakshatra_span / 4)) + 1
    
    return {
        "index": nakshatra_index,
        **NAKSHATRAS[nakshatra_index],
        "pada": pada
    }


def calculate_kundali(
    birth_date: datetime,
    lat: float,
    lon: float,
    timezone_offset: float = 5.5  # IST default
) -> Dict:
    """
    Calculate complete Kundali (Birth Chart)
    
    Args:
        birth_date: Birth datetime (local time)
        lat: Latitude of birth place
        lon: Longitude of birth place
        timezone_offset: Hours offset from UTC
    
    Returns:
        Dictionary with chart details
    """
    # Convert to UTC
    utc_hours = birth_date.hour + birth_date.minute/60 + birth_date.second/3600 - timezone_offset
    
    jd = julian_day(
        birth_date.year,
        birth_date.month,
        birth_date.day,
        utc_hours
    )
    
    # Calculate key positions
    lagna_deg = calculate_lagna(jd, lat, lon)
    sun_deg = calculate_sun_position(jd)
    moon_deg = calculate_moon_position(jd)
    
    lagna_rashi = get_rashi(lagna_deg)
    sun_rashi = get_rashi(sun_deg)
    moon_rashi = get_rashi(moon_deg)
    nakshatra = get_nakshatra(moon_deg)
    
    # Create house positions (Equal house system from Lagna)
    houses = []
    for i in range(12):
        house_start = (lagna_deg + i * 30) % 360
        houses.append({
            "house": i + 1,
            "sign": RASHIS[int(house_start / 30) % 12],
            "degree": round(house_start % 30, 2)
        })
    
    return {
        "birth_details": {
            "date": birth_date.strftime("%Y-%m-%d"),
            "time": birth_date.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "timezone": f"UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset}"
        },
        "lagna": {
            "degree": round(lagna_deg, 2),
            "rashi": lagna_rashi
        },
        "sun": {
            "degree": round(sun_deg, 2),
            "rashi": sun_rashi
        },
        "moon": {
            "degree": round(moon_deg, 2),
            "rashi": moon_rashi,
            "nakshatra": nakshatra
        },
        "houses": houses,
        "ayanamsa": round(get_ayanamsa(jd), 4)
    }


# ============== NUMEROLOGY ==============

def calculate_psychic_number(day: int) -> int:
    """Calculate Psychic Number (Moolank) from birth day"""
    while day > 9:
        day = sum(int(d) for d in str(day))
    return day


def calculate_destiny_number(birth_date: datetime) -> int:
    """Calculate Destiny Number (Bhagyank) from full birth date"""
    total = birth_date.day + birth_date.month + birth_date.year
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total


def calculate_name_number(name: str) -> int:
    """Calculate Name Number using Chaldean system"""
    chaldean = {
        'a': 1, 'i': 1, 'j': 1, 'q': 1, 'y': 1,
        'b': 2, 'k': 2, 'r': 2,
        'c': 3, 'g': 3, 'l': 3, 's': 3,
        'd': 4, 'm': 4, 't': 4,
        'e': 5, 'h': 5, 'n': 5, 'x': 5,
        'u': 6, 'v': 6, 'w': 6,
        'o': 7, 'z': 7,
        'f': 8, 'p': 8
    }
    
    total = sum(chaldean.get(c.lower(), 0) for c in name if c.isalpha())
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total


NUMEROLOGY_MEANINGS = {
    1: {"planet": "Sun", "traits": "Leadership, independence, ambition", "lucky_day": "Sunday"},
    2: {"planet": "Moon", "traits": "Intuitive, diplomatic, sensitive", "lucky_day": "Monday"},
    3: {"planet": "Jupiter", "traits": "Creative, optimistic, expressive", "lucky_day": "Thursday"},
    4: {"planet": "Rahu", "traits": "Practical, disciplined, hardworking", "lucky_day": "Sunday"},
    5: {"planet": "Mercury", "traits": "Versatile, adventurous, freedom-loving", "lucky_day": "Wednesday"},
    6: {"planet": "Venus", "traits": "Loving, nurturing, artistic", "lucky_day": "Friday"},
    7: {"planet": "Ketu", "traits": "Spiritual, analytical, introspective", "lucky_day": "Monday"},
    8: {"planet": "Saturn", "traits": "Ambitious, authoritative, material success", "lucky_day": "Saturday"},
    9: {"planet": "Mars", "traits": "Courageous, energetic, humanitarian", "lucky_day": "Tuesday"}
}


def get_numerology(birth_date: datetime, name: str = "") -> Dict:
    """Get complete numerology analysis"""
    psychic = calculate_psychic_number(birth_date.day)
    destiny = calculate_destiny_number(birth_date)
    name_num = calculate_name_number(name) if name else None
    
    result = {
        "psychic_number": {
            "number": psychic,
            **NUMEROLOGY_MEANINGS[psychic],
            "description": "Reveals your inner self and how you see yourself"
        },
        "destiny_number": {
            "number": destiny,
            **NUMEROLOGY_MEANINGS[destiny],
            "description": "Reveals your life path and what you're destined to achieve"
        }
    }
    
    if name_num:
        result["name_number"] = {
            "number": name_num,
            **NUMEROLOGY_MEANINGS[name_num],
            "description": "Reveals how others perceive you"
        }
    
    return result


# ============== COMPATIBILITY (KOOTA MATCHING) ==============

KOOTA_POINTS = {
    "varna": 1,      # Spiritual compatibility
    "vashya": 2,     # Dominance/control
    "tara": 3,       # Destiny compatibility
    "yoni": 4,       # Sexual/physical compatibility
    "graha_maitri": 5,  # Mental compatibility
    "gana": 6,       # Temperament
    "bhakoot": 7,    # Love and family
    "nadi": 8        # Health and genes
}

VARNA_SCORES = {
    # Higher varna groom with lower/equal bride = 1, else 0
    "Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1
}

NAKSHATRA_VARNA = {
    0: "Brahmin", 3: "Brahmin", 6: "Brahmin",  # Ashwini, Rohini, Punarvasu
    1: "Kshatriya", 4: "Kshatriya", 7: "Kshatriya",  # Bharani, Mrigashira, Pushya
    2: "Vaishya", 5: "Vaishya", 8: "Vaishya",  # Krittika, Ardra, Ashlesha
}

GANA_MAP = {
    "Deva": [0, 4, 6, 10, 12, 15, 19, 21, 26],  # Divine
    "Manushya": [1, 3, 7, 9, 13, 16, 20, 24],   # Human
    "Rakshasa": [2, 5, 8, 11, 14, 17, 18, 22, 23, 25]  # Demon
}


def get_gana(nakshatra_index: int) -> str:
    """Get Gana from Nakshatra"""
    for gana, nakshatras in GANA_MAP.items():
        if nakshatra_index in nakshatras:
            return gana
    return "Manushya"


def calculate_compatibility(
    person1_moon: float,
    person2_moon: float
) -> Dict:
    """
    Calculate 8-point Koota matching (Ashtakoota)
    
    Args:
        person1_moon: Moon longitude of person 1 (groom)
        person2_moon: Moon longitude of person 2 (bride)
    
    Returns:
        Compatibility score and breakdown
    """
    nak1 = get_nakshatra(person1_moon)
    nak2 = get_nakshatra(person2_moon)
    
    rashi1 = get_rashi(person1_moon)
    rashi2 = get_rashi(person2_moon)
    
    scores = {}
    
    # 1. Varna (1 point) - simplified
    scores["varna"] = {
        "score": 1 if nak1["index"] % 3 >= nak2["index"] % 3 else 0,
        "max": 1,
        "description": "Spiritual/work compatibility"
    }
    
    # 2. Vashya (2 points) - simplified based on rashi elements
    same_element = rashi1["element"] == rashi2["element"]
    scores["vashya"] = {
        "score": 2 if same_element else 1,
        "max": 2,
        "description": "Mutual attraction and influence"
    }
    
    # 3. Tara (3 points) - based on nakshatra count
    tara_count = (nak2["index"] - nak1["index"]) % 27
    tara_group = (tara_count % 9) + 1
    favorable_taras = [1, 2, 4, 6, 8, 9]
    scores["tara"] = {
        "score": 3 if tara_group in favorable_taras else 0,
        "max": 3,
        "description": "Destiny and health compatibility"
    }
    
    # 4. Yoni (4 points) - simplified
    yoni_diff = abs(nak1["index"] - nak2["index"]) % 14
    scores["yoni"] = {
        "score": 4 if yoni_diff <= 2 else (2 if yoni_diff <= 5 else 0),
        "max": 4,
        "description": "Physical and intimate compatibility"
    }
    
    # 5. Graha Maitri (5 points) - based on rashi lords
    lords_match = rashi1["lord"] == rashi2["lord"]
    scores["graha_maitri"] = {
        "score": 5 if lords_match else 3,
        "max": 5,
        "description": "Mental and intellectual compatibility"
    }
    
    # 6. Gana (6 points)
    gana1 = get_gana(nak1["index"])
    gana2 = get_gana(nak2["index"])
    if gana1 == gana2:
        gana_score = 6
    elif (gana1 == "Deva" and gana2 == "Manushya") or (gana1 == "Manushya" and gana2 == "Deva"):
        gana_score = 5
    elif (gana1 == "Manushya" and gana2 == "Rakshasa") or (gana1 == "Rakshasa" and gana2 == "Manushya"):
        gana_score = 1
    else:
        gana_score = 0
    scores["gana"] = {
        "score": gana_score,
        "max": 6,
        "description": "Temperament compatibility",
        "person1_gana": gana1,
        "person2_gana": gana2
    }
    
    # 7. Bhakoot (7 points) - based on rashi positions
    rashi_diff = abs(rashi1["index"] - rashi2["index"])
    unfavorable = [2, 5, 6, 8, 9, 12]  # 2/12, 5/9, 6/8
    scores["bhakoot"] = {
        "score": 0 if rashi_diff in unfavorable else 7,
        "max": 7,
        "description": "Love, family prosperity, and financial compatibility"
    }
    
    # 8. Nadi (8 points) - based on nakshatra thirds
    nadi1 = nak1["index"] % 3
    nadi2 = nak2["index"] % 3
    nadi_names = ["Aadi", "Madhya", "Antya"]
    scores["nadi"] = {
        "score": 0 if nadi1 == nadi2 else 8,
        "max": 8,
        "description": "Health and genetic compatibility",
        "person1_nadi": nadi_names[nadi1],
        "person2_nadi": nadi_names[nadi2]
    }
    
    # Calculate totals
    total_score = sum(s["score"] for s in scores.values())
    max_score = 36
    percentage = round((total_score / max_score) * 100, 1)
    
    # Compatibility verdict
    if percentage >= 75:
        verdict = "Excellent match - Highly recommended"
    elif percentage >= 60:
        verdict = "Good match - Recommended with minor considerations"
    elif percentage >= 50:
        verdict = "Average match - Proceed with caution and remedies"
    else:
        verdict = "Below average - Consult a qualified astrologer for remedies"
    
    return {
        "person1": {
            "nakshatra": nak1,
            "rashi": rashi1
        },
        "person2": {
            "nakshatra": nak2,
            "rashi": rashi2
        },
        "scores": scores,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "verdict": verdict
    }


# ============== DAILY HOROSCOPE ==============

RASHI_DAILY_THEMES = {
    0: ["New beginnings", "Take initiative", "Leadership opportunities"],
    1: ["Financial matters", "Stability focus", "Sensory pleasures"],
    2: ["Communication", "Short travels", "Learning"],
    3: ["Home and family", "Emotional matters", "Property"],
    4: ["Creative expression", "Romance", "Children matters"],
    5: ["Health focus", "Service to others", "Daily routines"],
    6: ["Partnerships", "Legal matters", "Public dealings"],
    7: ["Transformation", "Shared resources", "Deep insights"],
    8: ["Higher learning", "Long journeys", "Spiritual growth"],
    9: ["Career matters", "Public image", "Authority"],
    10: ["Friendships", "Social activities", "Future planning"],
    11: ["Solitude beneficial", "Spiritual practices", "Hidden matters"]
}


def get_daily_horoscope(moon_rashi_index: int, date: datetime = None) -> Dict:
    """Generate daily horoscope based on Moon sign"""
    if date is None:
        date = datetime.now(timezone.utc)
    
    # Use day of year for variety
    day_seed = date.timetuple().tm_yday
    
    # Rotate themes based on day
    theme_index = (moon_rashi_index + day_seed) % 12
    themes = RASHI_DAILY_THEMES[theme_index]
    
    # Lucky elements based on rashi
    rashi = RASHIS[moon_rashi_index]
    
    lucky_numbers = [(moon_rashi_index + day_seed + i) % 9 + 1 for i in range(3)]
    lucky_colors = {
        "Fire": ["Red", "Orange", "Gold"],
        "Earth": ["Green", "Brown", "Yellow"],
        "Air": ["White", "Light Blue", "Grey"],
        "Water": ["Blue", "Silver", "Purple"]
    }
    
    return {
        "rashi": rashi,
        "date": date.strftime("%Y-%m-%d"),
        "themes": themes,
        "lucky_numbers": lucky_numbers,
        "lucky_colors": lucky_colors.get(rashi["element"], ["White"]),
        "favorable_time": "Morning" if day_seed % 2 == 0 else "Evening",
        "caution_time": "Afternoon" if day_seed % 3 == 0 else "Late night"
    }

"""
MEVA — Motorcycle Expert Virtual Assistant
Capstone Edition v6.2 · Bike List + Service Map
"""

import streamlit as st
import requests
import os
import re
import json
import datetime
import threading
import markdown as md_lib
from dotenv import load_dotenv
# ── Translations (inlined — no external meva_translations.py needed) ─────────
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
}

T = {
    "sec_bike_profile": {
        "en": "Bike Profile",
        "hi": "बाइक प्रोफ़ाइल",
        "ta": "பைக் சுயவிவரம்",
        "te": "బైక్ ప్రొఫైల్",
        "kn": "ಬೈಕ್ ಪ್ರೊಫೈಲ್",
        "ml": "ബൈക്ക് പ്രൊഫൈൽ",
    },
    "sec_response_mode": {
        "en": "Response Mode",
        "hi": "प्रतिक्रिया मोड",
        "ta": "பதில் பயன்முறை",
        "te": "స్పందన మోడ్",
        "kn": "ಪ್ರತಿಕ್ರಿಯೆ ಮೋಡ್",
        "ml": "പ്രതികരണ മോഡ്",
    },
    "sec_language": {
        "en": "Language",
        "hi": "भाषा",
        "ta": "மொழி",
        "te": "భాష",
        "kn": "ಭಾಷೆ",
        "ml": "ഭാഷ",
    },
    "sec_checklist": {
        "en": "Service Checklist",
        "hi": "सर्विस चेकलिस्ट",
        "ta": "சேவை சரிபார்ப்பு பட்டியல்",
        "te": "సర్వీస్ చెక్‌లిస్ట్",
        "kn": "ಸರ್ವೀಸ್ ಪರಿಶೀಲನಾ ಪಟ್ಟಿ",
        "ml": "സർവീസ് ചെക്ക്‌ലിസ്റ്റ്",
    },
    "bike_model_label": {
        "en": "Bike Model",
        "hi": "बाइक मॉडल",
        "ta": "பைக் மாடல்",
        "te": "బైక్ మోడల్",
        "kn": "ಬೈಕ್ ಮಾದರಿ",
        "ml": "ബൈക്ക് മോഡൽ",
    },
    "bike_type_label": {
        "en": "Bike Type",
        "hi": "बाइक प्रकार",
        "ta": "பைக் வகை",
        "te": "బైక్ రకం",
        "kn": "ಬೈಕ್ ವಿಧ",
        "ml": "ബൈക്ക് തരം",
    },
    "custom_model_label": {
        "en": "Enter Custom Model",
        "hi": "कस्टम मॉडल दर्ज करें",
        "ta": "தனிப்பயன் மாடலை உள்ளிடுக",
        "te": "కస్టమ్ మోడల్ నమోదు చేయండి",
        "kn": "ಕಸ್ಟಮ್ ಮಾದರಿ ನಮೂದಿಸಿ",
        "ml": "കസ്റ്റം മോഡൽ നൽകുക",
    },
    "year_label": {
        "en": "Year",
        "hi": "वर्ष",
        "ta": "ஆண்டு",
        "te": "సంవత్సరం",
        "kn": "ವರ್ಷ",
        "ml": "വർഷം",
    },
    "odometer_label": {
        "en": "Odometer",
        "hi": "ओडोमीटर",
        "ta": "ஓடோமீட்டர்",
        "te": "ఒడోమీటర్",
        "kn": "ಓಡೋಮೀಟರ್",
        "ml": "ഓഡോമീറ്റർ",
    },
    "notes_label": {
        "en": "Notes",
        "hi": "नोट्स",
        "ta": "குறிப்புகள்",
        "te": "గమనికలు",
        "kn": "ಟಿಪ್ಪಣಿಗಳು",
        "ml": "കുറിപ്പുകൾ",
    },
    "type_ice": {
        "en": "Petrol / ICE",
        "hi": "पेट्रोल / ICE",
        "ta": "பெட்ரோல் / ICE",
        "te": "పెట్రోల్ / ICE",
        "kn": "ಪೆಟ್ರೋಲ್ / ICE",
        "ml": "പെട്രോൾ / ICE",
    },
    "type_ev": {
        "en": "Electric / EV",
        "hi": "इलेक्ट्रिक / EV",
        "ta": "மின்சார / EV",
        "te": "ఎలక్ట్రిక్ / EV",
        "kn": "ವಿದ್ಯುತ್ / EV",
        "ml": "ഇലക്ട്രിക് / EV",
    },
    "mode_desc_detailed": {
        "en": "Detailed",
        "hi": "विस्तृत",
        "ta": "விரிவான",
        "te": "వివరంగా",
        "kn": "ವಿವರವಾದ",
        "ml": "വിശദമായ",
    },
    "mode_detailed": {
        "en": "Detailed",
        "hi": "विस्तृत",
        "ta": "விரிவான",
        "te": "వివరంగా",
        "kn": "ವಿವರವಾದ",
        "ml": "വിശദമായ",
    },
    "mode_concise": {
        "en": "Concise",
        "hi": "संक्षिप्त",
        "ta": "சுருக்கமான",
        "te": "సంక్షిప్తంగా",
        "kn": "ಸಂಕ್ಷಿಪ್ತ",
        "ml": "സംക്ഷിപ്തം",
    },
    "mode_desc_concise": {
        "en": "Concise",
        "hi": "संक्षिप्त",
        "ta": "சுருக்கமான",
        "te": "సంక్షిప్తంగా",
        "kn": "ಸಂಕ್ಷಿಪ್ತ",
        "ml": "സംക്ഷിപ്തം",
    },
    "chat_input_placeholder": {
        "en": "Ask MEVA anything about your motorcycle…",
        "hi": "अपनी मोटरसाइकिल के बारे में MEVA से कुछ भी पूछें…",
        "ta": "உங்கள் மோட்டார் சைக்கிளைப் பற்றி MEVA கேளுங்கள்…",
        "te": "మీ మోటార్‌సైకిల్ గురించి MEVA ని అడగండి…",
        "kn": "ನಿಮ್ಮ ಮೋಟಾರ್‌ಸೈಕಲ್ ಬಗ್ಗೆ MEVA ಅನ್ನು ಕೇಳಿ…",
        "ml": "നിങ്ങളുടെ മോട്ടോർസൈക്കിളിനെ കുറിച്ച് MEVA യോട് ചോദിക്കൂ…",
    },
    "error": {
        "en": "Error",
        "hi": "त्रुटि",
        "ta": "பிழை",
        "te": "లోపం",
        "kn": "ದೋಷ",
        "ml": "പിശക്",
    },
    "btn_save_profile": {
        "en": "Save Profile",
        "hi": "प्रोफ़ाइल सेव करें",
        "ta": "சுயவிவரத்தை சேமி",
        "te": "ప్రొఫైల్ సేవ్ చేయండి",
        "kn": "ಪ್ರೊಫೈಲ್ ಉಳಿಸಿ",
        "ml": "പ്രൊഫൈൽ സേവ് ചെയ്യുക",
    },
    "profile_saved": {
        "en": "Profile saved!",
        "hi": "प्रोफ़ाइल सेव हो गई!",
        "ta": "சுயவிவரம் சேமிக்கப்பட்டது!",
        "te": "ప్రొఫైల్ సేవ్ అయింది!",
        "kn": "ಪ್ರೊಫೈಲ್ ಉಳಿಸಲಾಗಿದೆ!",
        "ml": "പ്രൊഫൈൽ സേവ് ചെയ്തു!",
    },
    "welcome_title": {
        "en": "Welcome to MEVA",
        "hi": "MEVA में आपका स्वागत है",
        "ta": "MEVA க்கு வரவேற்கிறோம்",
        "te": "MEVA కి స్వాగతం",
        "kn": "MEVA ಗೆ ಸ್ವಾಗತ",
        "ml": "MEVA യിലേക്ക് സ്വാഗതം",
    },
    "welcome_desc": {
        "en": "Your Motorcycle Expert Virtual Assistant",
        "hi": "आपका मोटरसाइकिल विशेषज्ञ वर्चुअल असिस्टेंट",
        "ta": "உங்கள் மோட்டார் சைக்கிள் நிபுணர் மெய்நிகர் உதவியாளர்",
        "te": "మీ మోటార్‌సైకిల్ నిపుణుల వర్చువల్ అసిస్టెంట్",
        "kn": "ನಿಮ್ಮ ಮೋಟಾರ್‌ಸೈಕಲ್ ತಜ್ಞ ವರ್ಚುವಲ್ ಸಹಾಯಕ",
        "ml": "നിങ്ങളുടെ മോട്ടോർസൈക്കിൾ വിദഗ്ധ വെർച്വൽ അസിസ്റ്റന്റ്",
    },
    "quick_topics_label": {
        "en": "⚡ Quick Topics",
        "hi": "⚡ त्वरित विषय",
        "ta": "⚡ விரைவு தலைப்புகள்",
        "te": "⚡ త్వరిత అంశాలు",
        "kn": "⚡ ತ್ವರಿತ ವಿಷಯಗಳು",
        "ml": "⚡ ദ്രുത വിഷയങ്ങൾ",
    },
    "ev_quick_topics_label": {
        "en": "⚡ EV Quick Topics",
        "hi": "⚡ EV त्वरित विषय",
        "ta": "⚡ EV விரைவு தலைப்புகள்",
        "te": "⚡ EV త్వరిత అంశాలు",
        "kn": "⚡ EV ತ್ವರಿತ ವಿಷಯಗಳು",
        "ml": "⚡ EV ദ്രുത വിഷയങ്ങൾ",
    },
    "search_placeholder": {
        "en": "Search…",
        "hi": "खोजें…",
        "ta": "தேடுங்கள்…",
        "te": "వెతకండి…",
        "kn": "ಹುಡುಕಿ…",
        "ml": "തിരയുക…",
    },
    "pill_maintenance": {
        "en": "Maintenance",
        "hi": "रखरखाव",
        "ta": "பராமரிப்பு",
        "te": "నిర్వహణ",
        "kn": "ನಿರ್ವಹಣೆ",
        "ml": "പരിപാലനം",
    },
    "pill_diagnostics": {
        "en": "Diagnostics",
        "hi": "डायग्नोस्टिक्स",
        "ta": "நோயறிதல்",
        "te": "డయాగ్నస్టిక్స్",
        "kn": "ರೋಗನಿರ್ಣಯ",
        "ml": "ഡയഗ്നോസ്റ്റിക്സ്",
    },
    "pill_repairs": {
        "en": "Repairs",
        "hi": "मरम्मत",
        "ta": "பழுதுபார்ப்பு",
        "te": "మరమ్మత్తులు",
        "kn": "ದುರಸ್ತಿ",
        "ml": "അറ്റകുറ്റപ്പണി",
    },
    "pill_safety": {
        "en": "Safety",
        "hi": "सुरक्षा",
        "ta": "பாதுகாப்பு",
        "te": "భద్రత",
        "kn": "ಸುರಕ್ಷತೆ",
        "ml": "സുരക്ഷ",
    },
    "pill_fuel": {
        "en": "Fuel",
        "hi": "ईंधन",
        "ta": "எரிபொருள்",
        "te": "ఇంధనం",
        "kn": "ಇಂಧನ",
        "ml": "ഇന്ധനം",
    },
    "pill_costs": {
        "en": "Costs",
        "hi": "लागत",
        "ta": "செலவுகள்",
        "te": "ఖర్చులు",
        "kn": "ವೆಚ್ಚಗಳು",
        "ml": "ചെലവുകൾ",
    },
}

load_dotenv()

# ── Concurrency: one persistent requests.Session per thread ──────────────────
# Reusing TCP connections cuts per-request overhead ~30 % under load.
_groq_session_local = threading.local()

def get_groq_session() -> requests.Session:
    """Return a thread-local requests.Session. Auth header is refreshed on
    every call so runtime changes to GROQ_API_KEY take effect immediately."""
    if not hasattr(_groq_session_local, "session"):
        _groq_session_local.session = requests.Session()
    # Always refresh auth in case the env var was updated at runtime
    _groq_session_local.session.headers.update({
        "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY', '').strip()}",
        "Content-Type": "application/json",
    })
    return _groq_session_local.session

# ── Config ────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

QUICK_TOPICS = [
    ("🌡️", "Engine Overheating"),
    ("🔧", "Oil Change Interval"),
    ("⛓️", "Chain Lubrication"),
    ("🔋", "Battery Not Starting"),
    ("🛑", "Spongy Brakes"),
    ("⛽", "Poor Mileage"),
    ("🔌", "Spark Plug Check"),
    ("🏍️", "Tyre Pressure"),
    ("💧", "Coolant Check"),
    ("🔩", "Clutch Adjustment"),
    ("🪛", "Air Filter Cleaning"),
    ("🚨", "Dashboard Warning Light"),
    ("🔊", "Engine Knocking Sound"),
    ("🌫️", "White Smoke Exhaust"),
    ("⚙️", "Gear Shifting Hard"),
    ("🛢️", "Oil Leak Diagnosis"),
]

EV_QUICK_TOPICS = [
    ("⚡", "Battery Range Drop"),
    ("🔌", "Charger Not Working"),
    ("📉", "Reduced Power Mode"),
    ("🌡️", "Battery Overheating"),
    ("❄️", "Cold Weather Range Loss"),
    ("🔇", "Regen Braking Issue"),
    ("🛞", "Motor Noise"),
    ("📱", "App / Connectivity Issue"),
    ("⚠️", "BMS Warning Light"),
    ("🔋", "Battery Won't Charge"),
    ("💨", "Cooling Fan Running Loud"),
    ("🏁", "Acceleration Lag"),
]

# ── Comprehensive Indian Bike List ────────────────────────────────────────────
ICE_BIKES = {
    "Hero": [
        "Hero Splendor Plus", "Hero Splendor+ XTEC", "Hero HF Deluxe",
        "Hero HF 100", "Hero Glamour", "Hero Glamour XTEC",
        "Hero Super Splendor", "Hero Passion Pro", "Hero Passion XPro",
        "Hero Xtreme 125R", "Hero Xtreme 160R", "Hero Xtreme 160R 4V",
        "Hero Xtreme 200R", "Hero Xtreme 200S", "Hero Xpulse 200",
        "Hero Xpulse 200 4V", "Hero Xpulse 200T", "Hero Destini 125",
        "Hero Maestro Edge 110", "Hero Maestro Edge 125",
        "Hero Pleasure+", "Hero Pleasure+ XTEC",
    ],
    "Honda": [
        "Honda Activa 6G", "Honda Activa 125", "Honda Activa 160",
        "Honda Dio", "Honda Grazia 125",
        "Honda CB Shine", "Honda CB Shine SP", "Honda CB100",
        "Honda Livo", "Honda Dream Neo", "Honda Dream Yuga",
        "Honda Unicorn", "Honda Hornet 2.0", "Honda SP 160", "Honda SP 125",
        "Honda CB200X", "Honda CB300R", "Honda CB300F",
        "Honda CB350 H'ness", "Honda CB350RS", "Honda CB500X",
        "Honda CBR650R", "Honda CBR1000RR-R Fireblade",
        "Honda Africa Twin", "Honda Gold Wing",
        "Honda X-Blade", "Honda NX200",
    ],
    "Bajaj": [
        "Bajaj Platina 100", "Bajaj Platina 110 H-Gear", "Bajaj CT 110",
        "Bajaj CT 110X", "Bajaj CT 125X", "Bajaj Discover 110",
        "Bajaj Discover 125", "Bajaj Pulsar 125", "Bajaj Pulsar 150",
        "Bajaj Pulsar N150", "Bajaj Pulsar F150", "Bajaj Pulsar 160NS",
        "Bajaj Pulsar N160", "Bajaj Pulsar 180", "Bajaj Pulsar F250",
        "Bajaj Pulsar N250", "Bajaj Pulsar 200NS", "Bajaj Pulsar RS200",
        "Bajaj Pulsar 220F", "Bajaj Avenger Street 160",
        "Bajaj Avenger Street 220", "Bajaj Avenger Cruise 220",
        "Bajaj Dominar 250", "Bajaj Dominar 400",
    ],
    "TVS": [
        "TVS Sport", "TVS Star City+", "TVS Radeon",
        "TVS Jupiter", "TVS Jupiter 125", "TVS Ntorq 125",
        "TVS Ntorq 125 Race XP", "TVS Scooty Pep+", "TVS Scooty Zest 110",
        "TVS Raider 125", "TVS Ronin", "TVS Apache RTR 160",
        "TVS Apache RTR 160 2V", "TVS Apache RTR 160 4V",
        "TVS Apache RTR 200 4V", "TVS Apache RR 310",
        "TVS Fiero 125", "TVS XL100",
    ],
    "Royal Enfield": [
        "Royal Enfield Bullet 350", "Royal Enfield Classic 350",
        "Royal Enfield Meteor 350", "Royal Enfield Hunter 350",
        "Royal Enfield Thunderbird 350X", "Royal Enfield Guerrilla 450",
        "Royal Enfield Himalayan 450", "Royal Enfield Himalayan 411",
        "Royal Enfield Scram 411", "Royal Enfield Interceptor 650",
        "Royal Enfield Continental GT 650", "Royal Enfield Super Meteor 650",
        "Royal Enfield Shotgun 650",
    ],
    "Yamaha": [
        "Yamaha FZ-S FI V4", "Yamaha FZ-FI V3", "Yamaha FZ 25",
        "Yamaha FZS 25", "Yamaha MT-03", "Yamaha MT-07", "Yamaha MT-09",
        "Yamaha R15 V4", "Yamaha R15M", "Yamaha R15S",
        "Yamaha R3", "Yamaha R7", "Yamaha YZF R15",
        "Yamaha Fascino 125 FI", "Yamaha Ray-ZR 125 FI",
        "Yamaha Ray-ZR Street Rally", "Yamaha Aerox 155",
        "Yamaha Saluto", "Yamaha SZ-RR",
    ],
    "Suzuki": [
        "Suzuki Access 125", "Suzuki Burgman Street",
        "Suzuki Gixxer 150", "Suzuki Gixxer SF 150",
        "Suzuki Gixxer 250", "Suzuki Gixxer SF 250",
        "Suzuki Intruder 150", "Suzuki V-Strom SX",
        "Suzuki Avenis 125", "Suzuki Hayabusa", "Suzuki GSX-S1000",
    ],
    "KTM": [
        "KTM Duke 125", "KTM Duke 200", "KTM Duke 250",
        "KTM Duke 390", "KTM Duke 890",
        "KTM RC 125", "KTM RC 200", "KTM RC 390",
        "KTM Adventure 250", "KTM Adventure 390",
        "KTM Adventure 790", "KTM Adventure 890",
    ],
    "Husqvarna": [
        "Husqvarna Svartpilen 125", "Husqvarna Vitpilen 125",
        "Husqvarna Svartpilen 250", "Husqvarna Vitpilen 250",
        "Husqvarna Svartpilen 401", "Husqvarna Vitpilen 401",
    ],
    "Kawasaki": [
        "Kawasaki Ninja 300", "Kawasaki Ninja 400",
        "Kawasaki Ninja 650", "Kawasaki Ninja ZX-4R",
        "Kawasaki Ninja ZX-6R", "Kawasaki Ninja ZX-10R",
        "Kawasaki Z650", "Kawasaki Z900", "Kawasaki Z H2",
        "Kawasaki Versys 650", "Kawasaki Versys-X 300",
        "Kawasaki W175", "Kawasaki Eliminator",
    ],
    "BMW": [
        "BMW G 310 R", "BMW G 310 GS", "BMW G 310 RR",
        "BMW F 900 R", "BMW F 900 XR",
        "BMW R 1250 GS", "BMW R 1250 RT", "BMW R 1250 R",
        "BMW S 1000 RR", "BMW S 1000 XR", "BMW M 1000 RR",
    ],
    "Triumph": [
        "Triumph Speed 400", "Triumph Scrambler 400 X",
        "Triumph Street Triple R", "Triumph Street Triple RS",
        "Triumph Tiger Sport 660", "Triumph Tiger 900",
        "Triumph Bonneville T120", "Triumph Thruxton RS",
        "Triumph Rocket 3", "Triumph Tiger 1200",
    ],
    "Jawa / Yezdi": [
        "Jawa 42", "Jawa 42 FJ", "Jawa Perak",
        "Yezdi Roadster", "Yezdi Scrambler", "Yezdi Adventure",
    ],
    "Benelli": [
        "Benelli Imperiale 400", "Benelli TRK 502",
        "Benelli TRK 502X", "Benelli Leoncino 500",
        "Benelli 302R", "Benelli 600i",
    ],
    "Other ICE": [
        "Harley-Davidson X440", "Harley-Davidson Sportster S",
        "Harley-Davidson Pan America", "Harley-Davidson Fat Boy",
        "Indian Scout", "Indian Chief", "Indian FTR 1200",
        "Ducati Monster", "Ducati Panigale V2", "Ducati Panigale V4",
        "Ducati Scrambler", "Ducati Multistrada V2",
        "Honda CB750 Hornet", "MV Agusta Brutale",
        "CFMoto 300NK", "CFMoto 650NK", "CFMoto 650GT",
        "Zontes 350R", "QJ SRK 400",
    ],
}

EV_BIKES = {
    "Ola Electric": [
        "Ola S1 Air", "Ola S1 X", "Ola S1 X+",
        "Ola S1 Pro", "Ola S1 Pro Gen 2", "Ola S1 X 4kWh",
        "Ola Roadster X", "Ola Roadster", "Ola Roadster Pro",
    ],
    "Ather": [
        "Ather 450S", "Ather 450X Gen 2", "Ather 450X Gen 3",
        "Ather 450 Apex", "Ather Rizta S", "Ather Rizta Z",
    ],
    "TVS EV": [
        "TVS iQube S", "TVS iQube ST", "TVS iQube Electric",
    ],
    "Bajaj EV": [
        "Bajaj Chetak Premium", "Bajaj Chetak Urbane",
        "Bajaj Chetak 35 Series", "Bajaj Chetak 3202",
    ],
    "Hero EV": [
        "Hero Vida V1", "Hero Vida V1 Pro", "Hero Vida V1 Plus",
        "Hero Vida Z", "Hero Vida S",
        "Hero Optima", "Hero NYX", "Hero Flash",
    ],
    "Revolt": [
        "Revolt RV400", "Revolt RV400 BRZ", "Revolt RV1",
    ],
    "Simple Energy": [
        "Simple One", "Simple Dot One",
    ],
    "Okinawa": [
        "Okinawa Praise Pro", "Okinawa R30", "Okinawa Ridge+",
        "Okinawa Okhi-90", "Okinawa PraisePro",
    ],
    "Ampere": [
        "Ampere Nexus", "Ampere Magnus Pro", "Ampere Zeal",
        "Ampere REO Elite", "Ampere Primus",
    ],
    "Pure EV": [
        "Pure EV ETrance Neo+", "Pure EV eTryst 350",
        "Pure EV EPluto 7G", "Pure EV Ecoline",
    ],
    "Greaves / Ampere": [
        "Greaves Eltra", "Greaves Elmoto HR-3",
    ],
    "Bounce": [
        "Bounce Infinity E1", "Bounce Infinity E1+",
    ],
    "Kabira Mobility": [
        "Kabira KM4000", "Kabira KM3000",
    ],
    "Ultraviolette": [
        "Ultraviolette F77 Mach 2", "Ultraviolette F99",
    ],
    "Other EV": [
        "Matter Aera 5000+", "Tork Kratos R",
        "Orxa Mantis", "Euler HiLoad EV",
        "BGauss B8i", "BGauss C12i",
        "Joy E-bike Wolf+", "Joy E-bike Monster",
        "Lectrix LXS G3.0", "River Indie",
        "Emotorad Doodle V3", "Vihaan EV",
    ],
}

# Flat list helpers for selectboxes
def get_ice_bike_list():
    bikes = ["-- Select your bike --"]
    for brand, models in ICE_BIKES.items():
        bikes.append(f"── {brand} ──")
        bikes.extend(models)
    return bikes

def get_ev_bike_list():
    bikes = ["-- Select your bike --"]
    for brand, models in EV_BIKES.items():
        bikes.append(f"── {brand} ──")
        bikes.extend(models)
    return bikes

# ── Service Center Cities ─────────────────────────────────────────────────────
SERVICE_CENTER_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Surat", "Kanpur",
    "Nagpur", "Indore", "Bhopal", "Patna", "Vadodara", "Coimbatore",
    "Ludhiana", "Agra", "Visakhapatnam", "Vijayawada", "Kochi",
    "Nashik", "Madurai", "Mysore", "Chandigarh", "Guwahati",
    "Ranchi", "Bhubaneswar", "Thiruvananthapuram", "Noida", "Gurgaon",
    "Faridabad", "Meerut", "Varanasi", "Amritsar", "Jabalpur",
    "Jodhpur", "Rajkot", "Mangalore", "Hubli", "Belgaum",
    "Udaipur", "Dehradun", "Shimla", "Goa (Panaji)", "Pondicherry",
]

SERVICE_INTERVALS = {
    "Oil Change":      3000,
    "Chain Lube":      500,
    "Air Filter":      6000,
    "Spark Plug":      8000,
    "Coolant Flush":   20000,
    "Tyre Check":      1000,
    "Brake Fluid":     10000,
    "Fork Oil":        15000,
}

# ── EV Service intervals (km) ─────────────────────────────────────────────────
EV_SERVICE_INTERVALS = {
    "Tyre Check":          1000,
    "Brake Fluid":         10000,
    "Fork Oil":            15000,
    "Battery Health Check": 5000,
    "Coolant (liquid-cooled motor)": 20000,
    "Contactor Inspection": 20000,
    "Software Update Check": 3000,
    "Drive Belt / Chain":   6000,
}

# ── Urgency keywords ──────────────────────────────────────────────────────────
URGENCY_KEYWORDS = [
    "smoke", "fire", "burning", "seized", "seized engine", "brake fail",
    "no brakes", "accident", "overheating badly", "engine off", "stalled",
    "cut out", "locked up", "grinding", "bang", "explosion", "sparks",
    "leaking fuel", "petrol leak", "oil on road", "brake not working",
    "cannot stop", "wheel locked",
    # EV-specific urgency
    "battery fire", "battery smoking", "battery swollen", "thermal runaway",
    "electric shock", "high voltage", "sparks from battery", "charger sparking",
    "motor locked", "sudden power loss", "smoke from motor", "burning smell ev",
]

# ── Parts cost reference (INR) ────────────────────────────────────────────────
PARTS_COST = {
    "Engine Oil (1L)":       ("₹300", "₹800"),
    "Oil Filter":            ("₹80", "₹250"),
    "Air Filter":            ("₹150", "₹500"),
    "Spark Plug":            ("₹80", "₹400"),
    "Chain Set (chain+sprocket)": ("₹800", "₹2500"),
    "Brake Pads (front)":    ("₹200", "₹600"),
    "Brake Pads (rear)":     ("₹150", "₹500"),
    "Brake Shoe (drum)":     ("₹100", "₹350"),
    "Clutch Cable":          ("₹80", "₹200"),
    "Throttle Cable":        ("₹80", "₹200"),
    "Battery":               ("₹800", "₹2500"),
    "Tyre (front)":          ("₹700", "₹3000"),
    "Tyre (rear)":           ("₹900", "₹3500"),
    "Coolant":               ("₹150", "₹400"),
    "Brake Fluid":           ("₹100", "₹250"),
}

# ── Labour cost estimates (INR) — Feature 9 ───────────────────────────────────
LABOUR_COST = {
    "Oil Change":            ("₹100", "₹250"),
    "Chain Lubrication":     ("₹50",  "₹100"),
    "Air Filter Cleaning":   ("₹80",  "₹150"),
    "Spark Plug Replacement":("₹100", "₹200"),
    "Tyre Change (1)":       ("₹150", "₹300"),
    "Brake Pad Replacement": ("₹200", "₹400"),
    "Clutch Cable Change":   ("₹150", "₹250"),
    "Battery Replacement":   ("₹100", "₹200"),
    "Coolant Flush":         ("₹200", "₹400"),
    "Fork Oil Change":       ("₹500", "₹900"),
    "Carburetor Cleaning":   ("₹300", "₹600"),
    "Valve Adjustment":      ("₹400", "₹700"),
}

# ── EV Labour cost estimates (INR) ────────────────────────────────────────────
EV_LABOUR_COST = {
    "Tyre Change (1)":           ("₹150", "₹300"),
    "Brake Pad Replacement":     ("₹200", "₹400"),
    "Battery Module Replacement":("₹500", "₹1500"),
    "Charger Port Inspection":   ("₹200", "₹400"),
    "BMS Reset / Recalibration": ("₹300", "₹600"),
    "Motor Bearing Replacement": ("₹600", "₹1200"),
    "Throttle Sensor Replace":   ("₹300", "₹500"),
    "Contactor Replacement":     ("₹400", "₹800"),
    "Fork Oil Change":           ("₹500", "₹900"),
    "Software Update":           ("₹0",   "₹200"),
}

# ── EV Parts cost reference (INR) ─────────────────────────────────────────────
EV_PARTS_COST = {
    "Tyre (front)":              ("₹700",  "₹3000"),
    "Tyre (rear)":               ("₹900",  "₹3500"),
    "Brake Pads (front)":        ("₹200",  "₹600"),
    "Brake Pads (rear)":         ("₹150",  "₹500"),
    "Brake Fluid":               ("₹100",  "₹250"),
    "Battery Pack (full swap)":  ("₹25000","₹80000"),
    "Battery Module (1 cell)":   ("₹2000", "₹8000"),
    "Charger (onboard replace)": ("₹3000", "₹10000"),
    "Charging Cable":            ("₹500",  "₹2000"),
    "BMS Unit":                  ("₹2000", "₹6000"),
    "BLDC Motor":                ("₹8000", "₹25000"),
    "Throttle Sensor":           ("₹300",  "₹800"),
    "Controller Unit":           ("₹3000", "₹12000"),
    "Fork Oil":                  ("₹200",  "₹500"),
}

# ── Diagnosis wizard tree — Feature 1 ────────────────────────────────────────
DIAGNOSIS_TREE = {
    "🔊 Engine Noises": {
        "Knocking sound at low RPM": "Likely pre-ignition / carbon build-up. Check spark plug grade and fuel octane. Also inspect con-rod bearing if persistent.",
        "Ticking sound from top end": "Usually valve clearance out of spec. Book a valve adjustment. Cheap fix if done early.",
        "Rattling on startup, goes away": "Often cam chain slap. Cold oil is thin — if it stops after warm-up it's manageable. Watch it; replace cam chain tensioner if it worsens.",
        "Grinding near gearbox": "Possible clutch plate wear or shift-fork damage. Avoid riding and get it inspected immediately.",
    },
    "💨 Exhaust Smoke": {
        "White / steam smoke": "Usually coolant entering combustion — suspect blown head gasket. Stop riding, get it checked.",
        "Blue smoke (burning oil)": "Piston rings or valve seals worn. Oil is burning in the combustion chamber. Compression test recommended.",
        "Black smoke (rich mixture)": "Over-fuelling — dirty/blocked air filter, stuck choke, or rich carb/injector tune. Check air filter first.",
        "Light grey smoke intermittently": "Could be normal condensation if only on startup. Monitor — if persistent suspect rings.",
    },
    "⚡ Starting Issues": {
        "Engine cranks but won't fire": "Check spark (remove plug, crank, see spark). If no spark → coil or CDI. If spark OK → check fuel flow and compression.",
        "Starter clicks but nothing": "Weak battery or bad earth connection. Charge / replace battery, clean terminals.",
        "No click at all": "Dead battery, blown fuse, or kill-switch accidentally on. Check kill-switch first!",
        "Starts then dies immediately": "Blocked pilot jet (carb), fuel tap off/vacuum issue, or choke stuck closed.",
    },
    "🛑 Braking Problems": {
        "Spongy / soft lever feel": "Air in brake lines. Bleed the brakes. Also inspect brake fluid level and condition.",
        "Vibration when braking": "Warped disc rotor. Replace disc — don't ignore, it compromises stopping distance.",
        "Brake dragging / always applied": "Caliper piston seized or brake cable adjustment too tight. Free the piston or adjust cable.",
        "Squealing brakes": "Glazed pads, dust, or worn-to-metal pads. Inspect pad thickness immediately.",
    },
    "⛽ Fuel & Mileage": {
        "Sudden drop in mileage": "Check tyre pressure, air filter, and chain tension first. If all OK, carb jetting may be rich.",
        "Fuel smell when parked": "Petcock / fuel tap leaking, or overflow pipe dripping from float chamber. Fix immediately — fire risk.",
        "Engine runs rough at idle": "Idle mixture screw misadjusted, or pilot jet dirty. Clean carb or adjust fuel-air screw.",
        "Hesitation on acceleration": "Blocked main jet or weak accelerator pump. Carb clean or check fuel pump on FI bikes.",
    },
}

# ── EV Diagnosis wizard tree ──────────────────────────────────────────────────
EV_DIAGNOSIS_TREE = {
    "🔋 Battery & Range": {
        "Range dropped suddenly (>20%)": "Check recent charging habits — deep discharges degrade cells faster. Also check tyre pressure & riding mode. If persistent, request a battery health report from the app or service center.",
        "Battery won't charge past 80%": "Normal BMS protection on some models. If it used to charge to 100% and no longer does, a cell imbalance may be developing. Check manufacturer's recommended charge limit setting.",
        "Battery drains overnight (not riding)": "A parasitic drain from the BMS staying active, alarm, or connected accessories. Disconnect any add-ons and check if drain persists.",
        "Low battery warning comes on quickly": "Could be a faulty State-of-Charge (SoC) calibration. Do a full charge to 100% + full discharge cycle once. If warning still appears early, a cell may be degraded.",
    },
    "⚡ Motor & Power": {
        "Reduced power / limp mode activated": "Usually triggered by battery overheating, BMS fault, or motor temperature. Let the bike cool for 15 min. If recurring, check error codes in the app.",
        "Sudden loss of power while riding": "Could be a loose high-voltage connector, blown fuse, or contactor failure. Pull over safely. Do NOT open the battery enclosure — high voltage hazard.",
        "Motor makes grinding noise": "Likely a motor bearing starting to fail. Stop riding — bearing damage spreads fast and can lock the rear wheel.",
        "Jerky / stuttering acceleration": "Throttle sensor miscalibration or loose throttle connector. Try a slow re-calibration via the app. If it persists, replace the throttle position sensor.",
    },
    "🔌 Charging Issues": {
        "Charger not detected / no charging light": "Check the charging port for moisture or bent pins. Try a different outlet. If the port looks fine, the onboard charger may have failed.",
        "Charging is very slow": "Slow charging can indicate a weak power supply, partially failed charger stage, or BMS limiting charge rate due to a cell imbalance. Try a known-good outlet and different cable.",
        "Bike charges but shows error code": "Note the exact error code and look it up in the brand app or manual. Common codes: over-voltage (charger fault), temp fault (charge in shade), comms error (try restart).",
        "Charging stops mid-way": "Thermal cutoff or cell voltage imbalance. Let battery cool. If it stops at the same % every time, a bad cell group is likely — needs service center inspection.",
    },
    "🛑 Braking (EV)": {
        "Regen braking feels weak or inconsistent": "Check regen setting in the app — it may have been accidentally changed. Also check battery SoC; regen reduces when battery is near 100%.",
        "Spongy / soft brake lever feel": "Same as ICE: air in brake lines. Bleed the hydraulic brakes. EV brakes are conventional hydraulic — same procedure applies.",
        "Vibration when braking": "Warped disc rotor. Replace disc. The heavier weight of EV bikes increases disc stress.",
        "ABS activating on dry road unexpectedly": "Wheel speed sensor may be dirty or misaligned. Clean the sensor and ring. If ABS light stays on, the sensor needs replacement.",
    },
}

# ── Pre-ride checklist — Feature 7 ────────────────────────────────────────────
CHECKLIST_ITEMS = [
    ("🛞", "Tyre pressure & condition"),
    ("🔦", "Headlight, tail light & indicators"),
    ("🛢️", "Engine oil level"),
    ("⛽", "Fuel level"),
    ("🔗", "Chain tension & lubrication"),
    ("🛑", "Front & rear brake feel"),
    ("🪞", "Mirrors adjusted"),
    ("🔋", "Battery / electrics (no warning lights)"),
    ("🧤", "Gear: helmet, gloves, jacket"),
    ("💧", "Coolant level (if liquid-cooled)"),
]

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MEVA — Motorcycle Expert",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages"        not in st.session_state: st.session_state.messages        = []
if "bike_profile"    not in st.session_state: st.session_state.bike_profile    = {"model":"","year":"","km":"","notes":"","bike_type":"ICE"}
if "trigger"         not in st.session_state: st.session_state.trigger         = None
if "show_welcome"    not in st.session_state: st.session_state.show_welcome    = True
if "bike_type"       not in st.session_state: st.session_state.bike_type       = "ICE"    # "ICE" or "EV"
if "lang"            not in st.session_state: st.session_state.lang            = "en"     # Language code
# Initialise last_service with keys matching the current bike type
if "last_service" not in st.session_state:
    _init_intervals = EV_SERVICE_INTERVALS if st.session_state.bike_type == "EV" else SERVICE_INTERVALS
    st.session_state.last_service = {k: 0 for k in _init_intervals}
if "ride_log"        not in st.session_state: st.session_state.ride_log        = []
if "search_query"    not in st.session_state: st.session_state.search_query    = ""
if "active_tab"      not in st.session_state: st.session_state.active_tab      = "chat"
# v5 new state
if "ratings"         not in st.session_state: st.session_state.ratings         = {}       # Feature 4: {msg_idx: "up"/"down"}
if "response_mode"   not in st.session_state: st.session_state.response_mode   = "detailed" # Feature 6: "concise"/"detailed"
if "checklist"       not in st.session_state: st.session_state.checklist       = {item: False for _, item in CHECKLIST_ITEMS}  # Feature 7
if "diag_step"       not in st.session_state: st.session_state.diag_step       = 0        # Feature 1: 0=pick category, 1=pick sub, 2=result
if "diag_category"   not in st.session_state: st.session_state.diag_category   = None

# ── Translation helper ────────────────────────────────────────────────────────
def t(key: str) -> str:
    """Return translated string for current language, fallback to English."""
    lang = st.session_state.get("lang", "en")
    entry = T.get(key, {})
    return entry.get(lang) or entry.get("en", key)

if "diag_sub"        not in st.session_state: st.session_state.diag_sub        = None
if "service_city"    not in st.session_state: st.session_state.service_city    = "Mumbai"
if "map_searched"    not in st.session_state: st.session_state.map_searched    = False

# ── Helpers (early, needed before CSS rendering) ─────────────────────────────
def safe_markdown(content: str, **kwargs) -> None:
    """Wrapper around st.markdown that sanitises unicode to avoid
    UnicodeEncodeError in Streamlit's internal clean_text() call (Python 3.14+)."""
    try:
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        content = content.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        st.markdown(content, **kwargs)
    except UnicodeEncodeError:
        content = content.encode("ascii", errors="xmlcharrefreplace").decode("ascii")
        st.markdown(content, **kwargs)


# ── CSS ───────────────────────────────────────────────────────────────────────
safe_markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Variables ── */
:root {
  --bg:        #0a0a0b;
  --surface:   #111114;
  --card:      #17171c;
  --card2:     #1c1c22;
  --border:    rgba(255,255,255,0.07);
  --border2:   rgba(255,255,255,0.12);
  --orange:    #f97316;
  --orange2:   #fb923c;
  --amber:     #fbbf24;
  --green:     #22c55e;
  --red:       #ef4444;
  --blue:      #4f6ef7;
  --purple:    #a855f7;
  --text:      #e8e8ed;
  --muted:     #6b7280;
  --muted2:    #9ca3af;
  --user-bg:   #1c1f2e;
  --user-acc:  #4f6ef7;
  --radius:    14px;
  --font:      'DM Sans', sans-serif;
  --display:   'Bebas Neue', sans-serif;
  --mono:      'DM Mono', monospace;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background: var(--bg) !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"]
{ display: none !important; }

/* ── Sidebar smooth slide animation ── */
section[data-testid="stSidebar"] {
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              width 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* ── Sidebar collapse/expand button ── */
[data-testid="stSidebarCollapseButton"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {
  background: #1a1a20 !important;
  border: 1px solid rgba(249,115,22,0.35) !important;
  border-radius: 10px !important;
  width: 38px !important; height: 38px !important;
  min-width: 38px !important; min-height: 38px !important;
  display: flex !important;
  align-items: center !important; justify-content: center !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 0 14px rgba(249,115,22,0.18), inset 0 1px 0 rgba(255,255,255,0.05) !important;
  position: relative !important; overflow: hidden !important;
}
[data-testid="stSidebarCollapseButton"]:hover,
button[aria-label="Close sidebar"]:hover,
button[aria-label="Open sidebar"]:hover {
  background: rgba(249,115,22,0.14) !important;
  border-color: rgba(249,115,22,0.7) !important;
  box-shadow: 0 0 22px rgba(249,115,22,0.35) !important;
  transform: scale(1.1) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
button[aria-label="Close sidebar"] svg,
button[aria-label="Open sidebar"] svg { display: none !important; }
[data-testid="stSidebarCollapseButton"]::after,
button[aria-label="Close sidebar"]::after,
button[aria-label="Open sidebar"]::after {
  content: "🏍️"; font-size: 19px; line-height: 1; display: block;
}

/* ── Fonts globally ── */
*, .stMarkdown, .stTextInput, label, p, span, div {
  font-family: var(--font) !important;
  color: var(--text);
}

/* ── Global input / textarea dark override ── */
input, textarea, select,
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox select,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="base-input"] input {
  background: var(--card) !important;
  background-color: var(--card) !important;
  color: var(--text) !important;
  caret-color: var(--orange) !important;
}
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"] {
  background: var(--card) !important;
  background-color: var(--card) !important;
}

/* ═══════════════════════════════════
   SIDEBAR
═══════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] > div {
  background: transparent !important;
  padding: 0 !important;
}

/* Sidebar logo */
.meva-sidebar-logo {
  padding: 28px 20px 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.meva-wordmark {
  font-family: var(--display) !important;
  font-size: 38px !important;
  letter-spacing: 4px;
  color: #fff !important;
  line-height: 1;
}
.meva-wordmark span { color: var(--orange) !important; }
.meva-tagline {
  font-size: 11px !important;
  color: var(--muted) !important;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 4px;
}
.meva-version-badge {
  display: inline-block;
  background: rgba(249,115,22,0.12);
  border: 1px solid rgba(249,115,22,0.3);
  color: var(--orange) !important;
  font-size: 10px !important;
  font-weight: 600;
  letter-spacing: 1px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-top: 8px;
}

/* Sidebar section headers */
.sb-section-title {
  font-size: 10px !important;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600 !important;
  padding: 0 20px 10px;
}

/* Sidebar inputs */
section[data-testid="stSidebar"] .stTextInput label {
  font-size: 11px !important;
  color: var(--muted2) !important;
  font-weight: 500 !important;
  letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] .stTextInput input {
  background: var(--card2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-size: 13px !important;
  padding: 9px 12px !important;
  transition: all 0.2s;
}
section[data-testid="stSidebar"] .stTextInput input:focus {
  border-color: var(--orange) !important;
  background: rgba(249,115,22,0.05) !important;
  box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important;
  outline: none !important;
}
section[data-testid="stSidebar"] .stTextInput input::placeholder {
  color: rgba(107,114,128,0.6) !important;
}

/* Sidebar number input */
section[data-testid="stSidebar"] .stNumberInput input {
  background: var(--card2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-size: 13px !important;
  padding: 9px 12px !important;
  transition: all 0.2s;
}
section[data-testid="stSidebar"] .stNumberInput input:focus {
  border-color: var(--orange) !important;
  box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid var(--border2) !important;
  color: var(--muted2) !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 9px 16px !important;
  transition: all 0.2s !important;
  width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(249,115,22,0.1) !important;
  border-color: rgba(249,115,22,0.35) !important;
  color: var(--orange2) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--orange), #ea580c) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  letter-spacing: 0.3px;
  box-shadow: 0 4px 14px rgba(249,115,22,0.3);
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #fb923c, var(--orange)) !important;
  box-shadow: 0 6px 20px rgba(249,115,22,0.4) !important;
  transform: translateY(-1px);
}

/* Sidebar download button */
section[data-testid="stSidebar"] .stDownloadButton > button {
  background: rgba(251,191,36,0.07) !important;
  border: 1px solid rgba(251,191,36,0.2) !important;
  color: var(--amber) !important;
  border-radius: 10px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 9px 16px !important;
  width: 100% !important;
  transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stDownloadButton > button:hover {
  background: rgba(251,191,36,0.14) !important;
  border-color: rgba(251,191,36,0.4) !important;
}

/* Success / info alert */
section[data-testid="stSidebar"] .stAlert {
  background: rgba(34,197,94,0.07) !important;
  border: 1px solid rgba(34,197,94,0.2) !important;
  border-radius: 10px !important;
  color: #86efac !important;
  font-size: 12px !important;
}

/* Sidebar selectbox */
section[data-testid="stSidebar"] .stSelectbox > div > div {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-size: 13px !important;
}

/* Sidebar stats */
.stat-box {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-label { font-size: 11px !important; color: var(--muted) !important; }
.stat-value {
  font-family: var(--display) !important;
  font-size: 20px !important;
  color: var(--orange) !important;
  line-height: 1;
}

/* ═══════════════════════════════════
   MAIN LAYOUT
═══════════════════════════════════ */
.main .block-container {
  padding: 0 !important;
  max-width: 860px !important;
  margin: 0 auto !important;
}

/* ═══════════════════════════════════
   EXPANDERS — dark theme fix
═══════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  width: 100% !important;
  box-sizing: border-box !important;
}
[data-testid="stExpander"] summary,
details > summary {
  background: var(--card) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
  padding: 14px 18px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  width: 100% !important;
  box-sizing: border-box !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}
[data-testid="stExpander"] summary:hover {
  background: var(--card2) !important;
}
[data-testid="stExpander"] details {
  background: var(--card) !important;
  width: 100% !important;
}
[data-testid="stExpanderDetails"] {
  background: var(--card) !important;
  border-top: 1px solid var(--border) !important;
  padding: 16px 18px !important;
}
[data-testid="stExpanderToggleIcon"] {
  margin-left: auto !important;
  flex-shrink: 0 !important;
}
/* Expander header label text — prevent overflow clipping */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
details > summary p {
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  max-width: calc(100% - 32px) !important;
  margin: 0 !important;
  color: var(--text) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}
/* Prevent Streamlit internal negative-margin clipping */
.main .block-container > div,
.main .block-container section,
.element-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {
  overflow: visible !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

/* ═══════════════════════════════════
   TOP HEADER BAR
═══════════════════════════════════ */
.meva-topbar {
  background: rgba(10,10,11,0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  padding: 14px 28px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.topbar-icon {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, var(--orange), #c2410c);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  box-shadow: 0 0 0 1px rgba(249,115,22,0.5), 0 4px 16px rgba(249,115,22,0.25);
  flex-shrink: 0;
}
.topbar-title {
  font-family: var(--display) !important;
  font-size: 22px !important;
  color: #fff !important;
  letter-spacing: 3px;
  line-height: 1;
}
.topbar-subtitle {
  font-size: 11px !important;
  color: var(--muted) !important;
  margin-top: 2px;
  letter-spacing: 0.5px;
}
.topbar-status {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  background: rgba(34,197,94,0.08);
  border: 1px solid rgba(34,197,94,0.2);
  border-radius: 20px;
  padding: 5px 12px;
}
.status-pulse {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #22c55e;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity:1; transform:scale(1); }
  50%      { opacity:0.4; transform:scale(0.75); }
}
.status-text { font-size: 11px !important; color: #4ade80 !important; font-weight: 600 !important; }
.topbar-bike-tag {
  background: rgba(79,110,247,0.1);
  border: 1px solid rgba(79,110,247,0.25);
  border-radius: 8px;
  padding: 5px 12px;
  font-size: 11px !important;
  color: #818cf8 !important;
  font-weight: 600 !important;
  letter-spacing: 0.3px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
/* Mode badge in topbar */
.topbar-mode-badge {
  background: rgba(168,85,247,0.1);
  border: 1px solid rgba(168,85,247,0.25);
  border-radius: 8px;
  padding: 5px 10px;
  font-size: 10px !important;
  color: #c084fc !important;
  font-weight: 700 !important;
  letter-spacing: 1px;
  text-transform: uppercase;
}

/* ═══════════════════════════════════
   OVERDUE SERVICE TOAST — Feature 5
═══════════════════════════════════ */
.overdue-toast {
  margin: 12px 28px 0;
  background: rgba(239,68,68,0.07);
  border: 1px solid rgba(239,68,68,0.3);
  border-left: 3px solid var(--red);
  border-radius: 10px;
  padding: 11px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: fadeUp 0.4s ease-out;
}
.overdue-toast-icon { font-size: 18px; flex-shrink: 0; }
.overdue-toast-text { font-size: 12px !important; color: #fca5a5 !important; line-height: 1.5; flex: 1; }
.overdue-toast-text strong { color: #f87171 !important; }

/* ═══════════════════════════════════
   URGENCY BANNER
═══════════════════════════════════ */
.urgency-banner {
  margin: 16px 28px 0;
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.35);
  border-radius: 12px;
  padding: 12px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: fadeUp 0.3s ease-out;
}
.urgency-icon { font-size: 20px; flex-shrink: 0; }
.urgency-text { font-size: 13px !important; color: #fca5a5 !important; line-height: 1.5; }
.urgency-text strong { color: #f87171 !important; }

/* ═══════════════════════════════════
   SEARCH BAR
═══════════════════════════════════ */
.search-bar-wrap {
  padding: 12px 28px 0;
}
.search-bar-wrap .stTextInput input {
  background: var(--card2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-size: 13px !important;
  padding: 8px 14px !important;
}
.search-bar-wrap .stTextInput input:focus {
  border-color: var(--orange) !important;
  box-shadow: 0 0 0 3px rgba(249,115,22,0.1) !important;
}
.search-result-count {
  font-size: 11px !important;
  color: var(--muted) !important;
  padding: 4px 28px 0;
}

/* ═══════════════════════════════════
   WELCOME CARD
═══════════════════════════════════ */
.welcome-wrap { padding: 36px 28px 8px; }
.welcome-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 32px 36px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.welcome-emoji { font-size: 44px; display: block; margin-bottom: 16px; }
.welcome-title {
  font-family: var(--display) !important;
  font-size: 32px !important;
  color: #fff !important;
  letter-spacing: 4px;
  margin-bottom: 10px;
}
.welcome-title span { color: var(--orange) !important; }
.welcome-desc {
  font-size: 14px !important;
  color: var(--muted2) !important;
  line-height: 1.7;
  max-width: 480px;
  margin: 0 auto;
}
.welcome-pills {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}
.welcome-pill {
  background: rgba(249,115,22,0.08);
  border: 1px solid rgba(249,115,22,0.2);
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 11px !important;
  color: var(--orange2) !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px;
}

/* ═══════════════════════════════════
   CHAT AREA
═══════════════════════════════════ */
.chat-wrap { padding: 20px 28px 8px; }

.date-chip { text-align: center; margin: 0 0 20px; }
.date-chip span {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 11px !important;
  color: var(--muted) !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px;
}

/* ── Bot message ── */
.msg-bot {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
  animation: fadeUp 0.25s ease-out;
}
@keyframes fadeUp {
  from { opacity:0; transform:translateY(10px); }
  to   { opacity:1; transform:translateY(0); }
}
.bot-av {
  width: 36px; height: 36px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--orange), #c2410c);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 17px;
  box-shadow: 0 2px 10px rgba(249,115,22,0.3);
}
.bot-bubble {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 0 18px 18px 18px;
  padding: 14px 18px;
  max-width: 78%;
  font-size: 14px !important;
  line-height: 1.7;
  color: var(--text) !important;
  box-shadow: 0 2px 14px rgba(0,0,0,0.3);
}
.bot-bubble strong { color: var(--orange2) !important; font-weight: 700; }
.bot-bubble code {
  background: rgba(255,255,255,0.07);
  border-radius: 5px;
  padding: 1px 6px;
  font-family: var(--mono) !important;
  font-size: 12px;
}
.msg-ts {
  font-size: 10px !important;
  color: var(--muted) !important;
  margin-top: 5px;
  padding-left: 2px;
}

/* ── Highlight search matches ── */
.search-highlight {
  background: rgba(249,115,22,0.25);
  border-radius: 3px;
  padding: 0 2px;
  color: var(--orange2) !important;
}

/* ── User message ── */
.msg-user {
  display: flex;
  flex-direction: row-reverse;
  gap: 12px;
  margin-bottom: 18px;
  animation: fadeUp 0.25s ease-out;
}
.user-av {
  width: 36px; height: 36px; flex-shrink: 0;
  background: linear-gradient(135deg, #334155, #1e293b);
  border-radius: 10px;
  border: 1px solid var(--border2);
  display: flex; align-items: center; justify-content: center;
  font-size: 17px;
}
.user-bubble {
  background: linear-gradient(135deg, #1c1f2e, #1a1d2e);
  border: 1px solid rgba(79,110,247,0.25);
  border-radius: 18px;
  padding: 14px 18px;
  display: inline-block;
  width: auto !important;
  min-width: 120px;
  max-width: 500px;
  white-space: pre-wrap;
  word-break: break-word;
  color: #c7d2fe !important;
  font-size: 14px !important;
  line-height: 1.7;
  box-shadow: 0 2px 14px rgba(0,0,0,0.3);
}
.user-wrap { display: flex; flex-direction: column; align-items: flex-end; }
.user-wrap .msg-ts { text-align: right; }

/* ═══════════════════════════════════
   FOLLOW-UP CHIPS
═══════════════════════════════════ */
.followup-wrap { margin: 4px 0 16px 48px; }
.followup-head {
  font-size: 10px !important;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 600 !important;
  margin-bottom: 8px;
}
.followup-wrap .stButton > button {
  background: rgba(23,23,28,0.8) !important;
  border: 1px solid var(--border2) !important;
  color: var(--muted2) !important;
  border-radius: 8px !important;
  font-size: 12.5px !important;
  font-weight: 500 !important;
  padding: 7px 14px !important;
  text-align: left !important;
  transition: all 0.2s !important;
  width: auto !important;
  margin-bottom: 4px !important;
}
.followup-wrap .stButton > button:hover {
  background: rgba(249,115,22,0.1) !important;
  border-color: rgba(249,115,22,0.3) !important;
  color: var(--orange2) !important;
}

/* ═══════════════════════════════════
   QUICK TOPICS STRIP
═══════════════════════════════════ */
.quick-section {
  padding: 16px 28px 0;
  border-top: 1px solid var(--border);
}
.quick-head {
  font-size: 10px !important;
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700 !important;
  margin-bottom: 10px;
}
div[data-testid="stHorizontalBlock"] .stButton > button {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  color: var(--muted2) !important;
  border-radius: 10px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 9px 10px !important;
  width: 100% !important;
  transition: all 0.2s !important;
  text-align: center !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
  background: rgba(249,115,22,0.1) !important;
  border-color: rgba(249,115,22,0.3) !important;
  color: var(--orange2) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(249,115,22,0.15) !important;
}

/* ═══════════════════════════════════
   COMPOSER (chat input)
═══════════════════════════════════ */
[data-testid="stChatInput"] {
  background: var(--card) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 14px !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--orange) !important;
  box-shadow: 0 0 0 3px rgba(249,115,22,0.12), 0 4px 20px rgba(0,0,0,0.3) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text) !important;
  font-size: 14px !important;
  font-family: var(--font) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
[data-testid="stChatInputSubmitButton"] {
  background: linear-gradient(135deg, var(--orange), #c2410c) !important;
  border-radius: 10px !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 2px 10px rgba(249,115,22,0.3) !important;
}
/* Bottom sticky bar wrapper — force dark */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
  background: var(--bg) !important;
  background-color: var(--bg) !important;
  border-top: 1px solid var(--border) !important;
}

/* ═══════════════════════════════════
   MISC
═══════════════════════════════════ */
hr { border-color: var(--border) !important; }
.stSpinner { color: var(--orange) !important; }
[data-testid="stSpinner"] > div { border-top-color: var(--orange) !important; }

.bot-bubble-err {
  background: rgba(239,68,68,0.07) !important;
  border-color: rgba(239,68,68,0.25) !important;
  color: #fca5a5 !important;
}

/* ── Typing indicator ── */
.typing-indicator {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
  align-items: flex-start;
}
.typing-bubble {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 0 18px 18px 18px;
  padding: 14px 18px;
  display: flex;
  gap: 5px;
  align-items: center;
}
.typing-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--orange);
  animation: typingBounce 1.2s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
  0%, 80%, 100% { opacity: 0.25; transform: scale(0.8); }
  40%           { opacity: 1;    transform: scale(1.1); }
}

/* ── Service Tracker Progress ── */
.svc-item { margin-bottom: 10px; }
.svc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
.svc-name { font-size: 12px !important; color: var(--muted2) !important; font-weight: 500 !important; }
.svc-km   { font-size: 11px !important; font-weight: 600 !important; }
.svc-km.ok      { color: var(--green) !important; }
.svc-km.warn    { color: var(--amber) !important; }
.svc-km.overdue { color: var(--red) !important; }
.svc-bar-track {
  height: 5px;
  background: rgba(255,255,255,0.06);
  border-radius: 99px;
  overflow: hidden;
}
.svc-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
}
.svc-bar-fill.ok      { background: linear-gradient(90deg, #16a34a, var(--green)); }
.svc-bar-fill.warn    { background: linear-gradient(90deg, #d97706, var(--amber)); }
.svc-bar-fill.overdue { background: linear-gradient(90deg, #b91c1c, var(--red)); }

/* ── Copy button on bot bubbles ── */
.copy-btn {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--muted) !important;
  font-size: 11px !important;
  padding: 3px 10px;
  cursor: pointer;
  margin-top: 6px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}
.copy-btn:hover {
  background: rgba(249,115,22,0.1);
  border-color: rgba(249,115,22,0.3);
  color: var(--orange2) !important;
}

/* ── Voice mic button ── */
#meva-mic-btn {
  position: fixed;
  bottom: 88px;
  right: 28px;
  z-index: 999;
  width: 46px; height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--orange), #c2410c);
  border: none;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 18px rgba(249,115,22,0.4);
  transition: all 0.2s;
  font-size: 20px;
}
#meva-mic-btn:hover { transform: scale(1.1); box-shadow: 0 6px 24px rgba(249,115,22,0.55); }
#meva-mic-btn.listening {
  animation: micPulse 1s ease-in-out infinite;
  background: linear-gradient(135deg, #ef4444, #dc2626);
}
@keyframes micPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }
  50%      { box-shadow: 0 0 0 12px rgba(239,68,68,0); }
}

/* ── Markdown in bot bubbles ── */
.bot-bubble h1,.bot-bubble h2,.bot-bubble h3 {
  color: var(--orange2) !important;
  font-family: var(--display) !important;
  margin: 10px 0 4px;
}
.bot-bubble ul, .bot-bubble ol { padding-left: 20px; margin: 6px 0; }
.bot-bubble li { margin-bottom: 4px; }
.bot-bubble hr { border-color: var(--border) !important; margin: 10px 0; }
.bot-bubble a { color: var(--orange2) !important; }
.bot-bubble table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 13px !important; }
.bot-bubble th { background: rgba(249,115,22,0.12); color: var(--orange2) !important; padding: 6px 10px; border: 1px solid var(--border2); }
.bot-bubble td { padding: 5px 10px; border: 1px solid var(--border); color: var(--muted2) !important; }

/* ── Parts Cost Card ── */
.parts-card {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 8px;
}
.parts-name  { font-size: 12px !important; color: var(--muted2) !important; }
.parts-range { font-size: 13px !important; color: var(--orange2) !important; font-weight: 600 !important; font-family: var(--mono) !important; }

/* ── Fuel Calculator ── */
.fuel-result {
  background: rgba(34,197,94,0.07);
  border: 1px solid rgba(34,197,94,0.2);
  border-radius: 10px;
  padding: 14px;
  text-align: center;
  margin-top: 8px;
}
.fuel-value {
  font-family: var(--display) !important;
  font-size: 32px !important;
  color: var(--green) !important;
  line-height: 1;
}
.fuel-label { font-size: 11px !important; color: var(--muted) !important; margin-top: 4px; letter-spacing: 1px; }

/* ── Ride Log ── */
.ride-entry {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ride-date { font-size: 10px !important; color: var(--muted) !important; }
.ride-km   { font-size: 13px !important; color: var(--orange2) !important; font-weight: 600 !important; font-family: var(--mono) !important; }

/* ── Feature 11: Service Center Map ── */
.map-search-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(79,110,247,0.1);
  border: 1px solid rgba(79,110,247,0.25);
  border-radius: 8px;
  padding: 5px 12px;
  font-size: 12px !important;
  color: #818cf8 !important;
  font-weight: 600 !important;
  margin-right: 6px;
  margin-bottom: 4px;
  text-decoration: none !important;
  transition: all 0.2s;
}
.map-search-tag:hover {
  background: rgba(79,110,247,0.2) !important;
  border-color: rgba(79,110,247,0.5) !important;
}



/* ── Feature 4: Rating buttons ── */
.rating-row {
  display: flex;
  gap: 6px;
  margin-top: 6px;
  align-items: center;
}
.rating-label {
  font-size: 10px !important;
  color: var(--muted) !important;
  margin-right: 2px;
}

/* ── Feature 1: Diagnosis Wizard ── */
.diag-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 16px;
  padding: 20px 22px;
  margin: 16px 28px;
  animation: fadeUp 0.3s ease-out;
}
.diag-title {
  font-family: var(--display) !important;
  font-size: 18px !important;
  color: #fff !important;
  letter-spacing: 2px;
  margin-bottom: 6px;
}
.diag-subtitle {
  font-size: 12px !important;
  color: var(--muted) !important;
  margin-bottom: 14px;
}
.diag-result {
  background: rgba(249,115,22,0.07);
  border: 1px solid rgba(249,115,22,0.25);
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 13px !important;
  color: var(--text) !important;
  line-height: 1.7;
  margin-top: 8px;
}

/* ── Feature 2: Mileage Chart placeholder ── */
.mileage-chart-wrap {
  padding: 0 28px 8px;
}

/* ── Feature 7: Checklist ── */
.checklist-card {
  background: var(--card);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 16px 18px;
  margin: 12px 0;
}
.checklist-title {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--orange2) !important;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}
.checklist-prog {
  height: 3px;
  background: rgba(255,255,255,0.06);
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 10px;
}
.checklist-prog-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--orange), var(--amber));
  border-radius: 99px;
  transition: width 0.4s ease;
}

/* ── Feature 8: Topics Sidebar ── */
.topic-chip {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  margin-bottom: 5px;
  font-size: 12px !important;
  color: var(--muted2) !important;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.topic-chip:hover {
  background: rgba(249,115,22,0.08) !important;
  border-color: rgba(249,115,22,0.3) !important;
  color: var(--orange2) !important;
}

/* ── Feature 9: Labour cost card ── */
.labour-card {
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.labour-job { font-size: 12px !important; color: var(--muted2) !important; }
.labour-cost { font-size: 12px !important; color: #86efac !important; font-weight: 600 !important; font-family: var(--mono) !important; }

/* ── Feature 3: Weather/road tag chips ── */
.road-tag {
  display: inline-block;
  background: rgba(79,110,247,0.1);
  border: 1px solid rgba(79,110,247,0.25);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 10px !important;
  color: #818cf8 !important;
  font-weight: 600 !important;
  margin-left: 6px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def html_escape(text: str) -> str:
    """Escape user-supplied text before embedding in raw HTML."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
    )


def now_time():
    return datetime.datetime.now().strftime("%I:%M %p")


@st.cache_data(max_entries=256)
def render_md(text: str) -> str:
    try:
        # Ensure text is clean unicode before passing to markdown
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        # Re-encode/decode to strip any surrogate or non-encodable characters
        text = text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
        return md_lib.markdown(text, extensions=["nl2br", "tables", "fenced_code"])
    except Exception:
        return text.replace("\n", "<br>")


def highlight_search(text: str, query: str) -> str:
    if not query:
        return text
    escaped = re.escape(query)
    return re.sub(f"({escaped})", r'<mark class="search-highlight">\1</mark>', text, flags=re.IGNORECASE)


def is_urgent(text: str) -> bool:
    tl = text.lower()
    return any(kw in tl for kw in URGENCY_KEYWORDS)


def build_system_prompt(bike: dict, mode: str = "detailed") -> str:
    bike_type = st.session_state.get("bike_type", "ICE")
    bike_info = ""
    if bike.get("model"):
        parts = [bike["model"]]
        if bike.get("year"):  parts.append(f"({bike['year']})")
        if bike.get("km"):    parts.append(f"{bike['km']} km")
        if bike.get("notes"): parts.append(f"Notes: {bike['notes']}")
        bike_info = f"\n\nUser's bike: {' '.join(parts)} [{'ELECTRIC' if bike_type == 'EV' else 'ICE/Petrol'}]. Tailor all advice specifically to this bike model and type."

    mode_instruction = ""
    if mode == "concise":
        mode_instruction = "\n\nRESPONSE MODE: CONCISE — Keep answers short and punchy. Max 3-4 bullet points or 2-3 sentences. No lengthy explanations."
    else:
        mode_instruction = "\n\nRESPONSE MODE: DETAILED — Give thorough explanations with context, steps, and cost estimates where relevant."

    ev_addendum = ""
    if bike_type == "EV":
        ev_addendum = """

EV EXPERTISE MODE ACTIVE:
- This user rides an ELECTRIC bike. Do NOT give advice about engine oil, spark plugs, carburettors, or petrol unless asked about ICE bikes generically.
- Focus on: battery health, BMS (Battery Management System), BLDC motor, regenerative braking, charging habits, thermal management, controller, throttle sensor, and software/firmware.
- EV safety rules: NEVER advise opening the high-voltage battery pack at home — electrocution risk. Always recommend authorised EV service for battery/motor internals.
- Give INR cost estimates for EV parts: battery packs (₹25,000–₹80,000+), controllers (₹3,000–₹12,000), BLDC motors (₹8,000–₹25,000).
- Common Indian EV bikes: Ola S1 Pro, Ather 450X, TVS iQube, Bajaj Chetak, Hero Vida V1, Revolt RV400, Pure EV, Okinawa, Ampere, Greaves.
- Tips for Indian EV riders: charge at night for lower electricity tariffs, avoid deep discharge below 15%, keep away from heavy rain (IP rating dependent), watch for charging infrastructure issues on long trips."""

    return f"""You are MEVA — Motorcycle Expert Virtual Assistant — a friendly, knowledgeable motorcycle mechanic AI with 20+ years of hands-on experience in India, now fully trained on both ICE (petrol) and Electric bikes.

Rules:
- ONLY answer motorcycle-related questions (maintenance, repair, diagnostics, parts, costs in INR, riding tips for Indian roads)
- If asked anything off-topic, reply only: "I'm MEVA, your motorcycle expert! I can only help with bike-related questions 🏍️"
- Be concise and conversational — use bullet points only when listing multiple steps or items
- Always mention safety precautions when relevant
- Give INR cost estimates when asked about repairs or parts (labour + parts separately if possible)
- For urgent/dangerous issues (smoke, brake failure, seizure, EV battery fire), lead with a clear safety warning in bold
- For diagnostic questions, follow: Symptom → Likely Cause(s) → DIY Fix (if safe) → When to see mechanic
- End EVERY response with "---FOLLOWUPS---" followed by exactly 3 short follow-up questions the user might ask, each on a new line prefixed with "Q:"
{bike_info}{mode_instruction}{ev_addendum}"""


def parse_response(raw: str):
    followups = []
    if "---FOLLOWUPS---" in raw:
        main, rest = raw.split("---FOLLOWUPS---", 1)
        for line in rest.strip().split("\n"):
            line = line.strip()
            if line.startswith("Q:"):
                q = line[2:].strip()
                if q: followups.append(q)
        return main.strip(), followups[:3]
    return raw.strip(), []


def call_groq(history: list, bike: dict, mode: str = "detailed"):
    if not GROQ_API_KEY:
        return None, "⚠️ GROQ_API_KEY not found. Please add it to your .env file."
    messages = [{"role": "system", "content": build_system_prompt(bike, mode)}]
    # Cap to last 20 messages to keep cost/latency sane as conversations grow
    for m in history[-20:]:
        messages.append({"role": m["role"], "content": m["content"]})
    try:
        # Use thread-local session: reuses TCP connection, safe for 10+ concurrent users
        session = get_groq_session()
        resp = session.post(
            GROQ_URL,
            json={"model": GROQ_MODEL, "messages": messages, "max_tokens": 800, "temperature": 0.45},
            timeout=(5, 90),   # (connect timeout, read timeout) — avoids thread stalls
        )
        data = resp.json()
        if not resp.ok:
            if resp.status_code == 401: return None, "🔑 Invalid API key. Check your GROQ_API_KEY."
            if resp.status_code == 429: return None, "⏱️ Rate limit hit. Wait a minute and retry."
            return None, f"⚠️ API error {resp.status_code}: {data.get('error', {}).get('message', 'Unknown')}"
        raw = data["choices"][0]["message"]["content"].strip()
        return parse_response(raw)
    except requests.exceptions.Timeout:
        return None, "⏳ Request timed out. Please try again."
    except Exception as e:
        return None, f"⚠️ Error: {e}"


def export_chat(fmt="txt"):
    bp = st.session_state.bike_profile
    if fmt == "md":
        lines = [
            "# MEVA — Chat Export",
            "",
            f"**Exported:** {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        ]
        if bp.get("model"):
            lines.append(f"**Bike:** {bp['model']} {bp.get('year','')} · {bp.get('km','')} km")
        lines += ["", "---", ""]
        for m in st.session_state.messages:
            role = "🏍️ **MEVA**" if m["role"] == "assistant" else "👤 **You**"
            ts_ = m.get("time","")
            lines.append(f"{role} _{ts_}_")
            lines.append("")
            lines.append(m["content"])
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)
    else:
        lines = [
            "═" * 50,
            "  MEVA — Motorcycle Expert Virtual Assistant v6.0",
            "  Chat Export",
            "═" * 50, "",
        ]
        if bp.get("model"):
            lines.append(f"  Bike     : {bp['model']} {bp.get('year','')}")
            if bp.get("km"):   lines.append(f"  Odometer : {bp['km']}")
            if bp.get("notes"): lines.append(f"  Notes    : {bp['notes']}")
        lines.append(f"  Exported : {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}")
        lines.append(f"  Messages : {len([m for m in st.session_state.messages if m['role'] == 'user'])} questions")
        lines += ["", "─" * 50, ""]
        for m in st.session_state.messages:
            role = "MEVA" if m["role"] == "assistant" else "You"
            ts = m.get("time", "")
            prefix = f"[{ts}] " if ts else ""
            lines.append(f"{prefix}{role}:")
            lines.append(m["content"])
            lines.append("")
        lines += ["─" * 50, "  End of export", "═" * 50]
        return "\n".join(lines)


def service_bar_html(service, interval, last, current_km):
    if not interval:
        return ""
    due_at  = last + interval
    km_used = current_km - last
    pct     = min(km_used / interval * 100, 100)
    km_left = due_at - current_km
    overdue = km_left <= 0

    if overdue:
        cls  = "overdue"
        label = f"⚠️ {abs(km_left):,} km overdue"
    elif pct >= 80:
        cls  = "warn"
        label = f"Due in {km_left:,} km"
    else:
        cls  = "ok"
        label = f"Due in {km_left:,} km"

    return f"""
    <div class="svc-item">
      <div class="svc-header">
        <span class="svc-name">{service}</span>
        <span class="svc-km {cls}">{label}</span>
      </div>
      <div class="svc-bar-track">
        <div class="svc-bar-fill {cls}" style="width:{pct:.1f}%"></div>
      </div>
    </div>
    """


def get_overdue_services(current_km):
    """Return list of overdue service names."""
    if current_km is None:
        return []
    active_intervals = EV_SERVICE_INTERVALS if st.session_state.get("bike_type", "ICE") == "EV" else SERVICE_INTERVALS
    overdue = []
    for service, interval in active_intervals.items():
        last = st.session_state.last_service.get(service, 0)
        km_left = (last + interval) - current_km
        if km_left <= 0:
            overdue.append(service)
    return overdue


def extract_topics(messages):
    """Extract short topic labels from user messages."""
    topics = []
    for m in messages:
        if m["role"] == "user":
            text = m["content"][:50].strip()
            if len(m["content"]) > 50:
                text += "…"
            topics.append(text)
    return topics


def get_current_km():
    raw = st.session_state.bike_profile.get("km", "")
    cleaned = raw.lower().replace("km", "").replace(",", "").replace(" ", "").strip()
    if not cleaned:
        return None
    try:
        return int(float(cleaned))   # handles "12000.0", "12,000 km", "12000KM" etc.
    except (ValueError, OverflowError):
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="meva-sidebar-logo">
      <div class="meva-wordmark">ME<span>V</span>A</div>
      <div class="meva-tagline">Motorcycle Expert AI</div>
      <div class="meva-version-badge">CAPSTONE v6.2 ⚡ EV + 🗺️ MAP</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bike Profile ─────────────────────────────────────────────────────────
    st.markdown(f'<div class="sb-section-title">🔧 {t("sec_bike_profile")}</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 4px;">', unsafe_allow_html=True)

    # Bike type toggle (ICE vs EV) — NEW in v6.0
    bike_type_options = {t("type_ice"): "ICE", t("type_ev"): "EV"}
    current_type_label = t("type_ev") if st.session_state.bike_type == "EV" else t("type_ice")
    selected_type_label = st.radio(
        t("bike_type_label"), list(bike_type_options.keys()),
        index=list(bike_type_options.keys()).index(current_type_label),
        horizontal=True,
        label_visibility="visible",
        key="bike_type_radio",
    )
    new_bike_type = bike_type_options[selected_type_label]
    if new_bike_type != st.session_state.bike_type:
        st.session_state.bike_type = new_bike_type
        # Reset service tracker to match bike type
        intervals = EV_SERVICE_INTERVALS if new_bike_type == "EV" else SERVICE_INTERVALS
        st.session_state.last_service = {k: 0 for k in intervals}
        st.rerun()

    # Bike model dropdown — filtered by ICE / EV type
    active_bike_list = get_ev_bike_list() if st.session_state.bike_type == "EV" else get_ice_bike_list()
    saved_model = st.session_state.bike_profile.get("model", "")
    # Determine current index (skip separator lines starting with ──)
    try:
        _idx = active_bike_list.index(saved_model) if saved_model in active_bike_list else 0
    except ValueError:
        _idx = 0
    selected_bike = st.selectbox(
        t("bike_model_label"),
        active_bike_list,
        index=_idx,
        key=f"bike_model_sel_{st.session_state.bike_type}",
        help="Can't find your bike? Type a custom name below.",
    )
    # Disable separator lines — if user picks a group header, reset to blank
    if selected_bike and selected_bike.startswith("──"):
        selected_bike = ""
    # Allow custom override
    bike_model_custom = st.text_input(
        t("custom_model_label"),
        value="" if (selected_bike and not selected_bike.startswith("--")) else saved_model,
        placeholder="e.g. Custom / Modified / Older model…",
        key="bike_model_custom",
    )
    # Resolve: custom entry takes priority if filled
    bike_model = bike_model_custom.strip() if bike_model_custom.strip() else (
        selected_bike if selected_bike and not selected_bike.startswith("--") else ""
    )
    c1, c2 = st.columns(2)
    bike_year = c1.text_input(t("year_label"),
        value=st.session_state.bike_profile.get("year",""), placeholder="2022")
    bike_km = c2.text_input(t("odometer_label"),
        value=st.session_state.bike_profile.get("km",""), placeholder="12000 km")
    bike_notes = st.text_input(t("notes_label"),
        value=st.session_state.bike_profile.get("notes",""),
        placeholder="Mods, recurring issues…")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding:0 12px 16px;">', unsafe_allow_html=True)
    if st.button(f"💾  {t('btn_save_profile')}", type="primary", use_container_width=True):
        st.session_state.bike_profile = {
            "model": bike_model.strip(), "year": bike_year.strip(),
            "km": bike_km.strip(), "notes": bike_notes.strip(),
        }
        st.success(f"✅ {t('profile_saved')}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Feature 6: Mood/Tone Toggle ───────────────────────────────────────────
    st.markdown(f'<div class="sb-section-title">🎨 {t("sec_response_mode")}</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 16px;">', unsafe_allow_html=True)
    mode_options = {f"🎯 {t('mode_concise')}": "concise", f"📚 {t('mode_detailed')}": "detailed"}
    current_label = f"🎯 {t('mode_concise')}" if st.session_state.response_mode == "concise" else f"📚 {t('mode_detailed')}"
    selected_mode_label = st.radio(
        "Tone", list(mode_options.keys()),
        index=list(mode_options.keys()).index(current_label),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.response_mode = mode_options[selected_mode_label]
    mode_desc = t("mode_desc_concise") if st.session_state.response_mode == "concise" else t("mode_desc_detailed")
    st.markdown(f'<div style="font-size:11px;color:#6b7280;margin-top:4px;">{mode_desc}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Language Selector ─────────────────────────────────────────────────────
    st.markdown(f'<div class="sb-section-title">🌐 {t("sec_language")}</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 16px;">', unsafe_allow_html=True)
    lang_labels = list(LANGUAGES.values())
    lang_codes  = list(LANGUAGES.keys())
    current_lang_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0
    selected_lang_label = st.selectbox(
        "Select Language",
        lang_labels,
        index=current_lang_idx,
        key="lang_selector",
        label_visibility="collapsed",
    )
    selected_lang_code = lang_codes[lang_labels.index(selected_lang_label)]
    if selected_lang_code != st.session_state.lang:
        st.session_state.lang = selected_lang_code
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Feature 7: Pre-ride Checklist ────────────────────────────────────────
    st.markdown(f'<div class="sb-section-title">📋 {t("sec_checklist")}</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 8px;">', unsafe_allow_html=True)

    checked_count = sum(1 for v in st.session_state.checklist.values() if v)
    total_count = len(CHECKLIST_ITEMS)
    pct_done = int(checked_count / total_count * 100)
    st.markdown(f"""
    <div class="checklist-card">
      <div class="checklist-title">Ride Ready? {checked_count}/{total_count}</div>
      <div class="checklist-prog">
        <div class="checklist-prog-fill" style="width:{pct_done}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    for icon, item in CHECKLIST_ITEMS:
        checked = st.checkbox(
            f"{icon} {item}",
            value=st.session_state.checklist.get(item, False),
            key=f"chk_{item}"
        )
        st.session_state.checklist[item] = checked
    if st.button("🔄 Reset Checklist", use_container_width=True, key="chk_reset"):
        st.session_state.checklist = {item: False for _, item in CHECKLIST_ITEMS}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Feature 8: Conversation Topics Sidebar ────────────────────────────────
    if st.session_state.messages:
        st.markdown('<div class="sb-section-title">💬 Past Topics</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:0 12px 12px;">', unsafe_allow_html=True)
        topics = extract_topics(st.session_state.messages)
        for i, topic in enumerate(reversed(topics[-8:])):
            if st.button(f"↩  {topic}", key=f"topic_{i}", use_container_width=True):
                st.session_state.trigger = topic[:50]
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Session Stats ────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">📊 Session Stats</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 16px;">', unsafe_allow_html=True)
    msg_count   = len([m for m in st.session_state.messages if m["role"] == "user"])
    reply_count = len([m for m in st.session_state.messages if m["role"] == "assistant" and not m.get("error")])
    thumbs_up   = sum(1 for v in st.session_state.ratings.values() if v == "up")
    rides_count = len(st.session_state.ride_log)
    st.markdown(f"""
    <div class="stat-box" style="margin-bottom:8px;">
      <span class="stat-label">Questions Asked</span>
      <span class="stat-value">{msg_count}</span>
    </div>
    <div class="stat-box" style="margin-bottom:8px;">
      <span class="stat-label">Answers Given</span>
      <span class="stat-value">{reply_count}</span>
    </div>
    <div class="stat-box" style="margin-bottom:8px;">
      <span class="stat-label">👍 Helpful Ratings</span>
      <span class="stat-value">{thumbs_up}</span>
    </div>
    <div class="stat-box">
      <span class="stat-label">Rides Logged</span>
      <span class="stat-value">{rides_count}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Chat Controls ────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">💬 Controls</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 8px;">', unsafe_allow_html=True)
    c1e, c2e = st.columns(2)
    with c1e:
        st.download_button(
            label="⬇️ .txt",
            data=export_chat("txt"),
            file_name=f"meva_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2e:
        st.download_button(
            label="⬇️ .md",
            data=export_chat("md"),
            file_name=f"meva_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    if st.session_state.messages:
        if st.button("🗑️  Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.show_welcome = True
            st.session_state.search_query = ""
            st.session_state.ratings = {}
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Service Tracker ───────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">🛠️ Service Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 12px;">', unsafe_allow_html=True)

    current_km = get_current_km()
    active_intervals = EV_SERVICE_INTERVALS if st.session_state.bike_type == "EV" else SERVICE_INTERVALS

    if current_km is None:
        st.markdown('<div style="font-size:12px;color:#6b7280;padding:6px 0;">Set odometer in Bike Profile to see service alerts.</div>', unsafe_allow_html=True)
    else:
        bars_html = ""
        for service, interval in active_intervals.items():
            last = st.session_state.last_service.get(service, 0)
            bars_html += service_bar_html(service, interval, last, current_km)
        st.markdown(bars_html, unsafe_allow_html=True)

        st.markdown('<div style="font-size:10px;color:#4b5563;margin-top:8px;margin-bottom:4px;">Mark service done to reset:</div>', unsafe_allow_html=True)
        svc_done = st.selectbox("", ["-- Select --"] + list(active_intervals.keys()), key="svc_sel", label_visibility="collapsed")
        if st.button("✅  Mark as Done", use_container_width=True, key="svc_done_btn"):
            if svc_done != "-- Select --":
                st.session_state.last_service[svc_done] = current_km
                st.success(f"✅ {svc_done} reset at {current_km:,} km")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Fuel Efficiency Calculator ────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">⛽ Fuel Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 12px;">', unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)
    dist_km   = fc1.number_input("Distance (km)", min_value=0, value=0, step=10, key="fc_dist")
    fuel_lt   = fc2.number_input("Fuel used (L)", min_value=0.0, value=0.0, step=0.1, format="%.1f", key="fc_fuel")
    if dist_km > 0 and fuel_lt > 0:
        mileage = dist_km / fuel_lt
        petrol_rs = fuel_lt * 102
        st.markdown(f"""
        <div class="fuel-result">
          <div class="fuel-value">{mileage:.1f}</div>
          <div class="fuel-label">KM / LITRE</div>
          <div style="margin-top:8px;font-size:12px;color:#6b7280;">≈ ₹{petrol_rs:.0f} spent (@ ₹102/L)</div>
        </div>
        """, unsafe_allow_html=True)
    elif dist_km > 0 or fuel_lt > 0:
        st.markdown('<div style="font-size:12px;color:#6b7280;text-align:center;">Enter both values to calculate</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Feature 9: Labour Cost Estimator ──────────────────────────────────────
    is_ev = st.session_state.bike_type == "EV"
    st.markdown(f'<div class="sb-section-title">🔧 Labour Estimator {"⚡ EV" if is_ev else ""}</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 12px;">', unsafe_allow_html=True)
    active_labour = EV_LABOUR_COST if is_ev else LABOUR_COST
    labour_html = ""
    for job, (lo, hi) in active_labour.items():
        labour_html += f'<div class="labour-card"><span class="labour-job">{job}</span><span class="labour-cost">{lo}–{hi}</span></div>'
    st.markdown(labour_html, unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;color:#4b5563;margin-top:2px;">Labour only. Add parts cost separately.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Parts Cost Reference ──────────────────────────────────────────────────
    st.markdown(f'<div class="sb-section-title">🔩 Parts Cost (INR) {"⚡ EV" if is_ev else ""}</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 12px;">', unsafe_allow_html=True)
    active_parts = EV_PARTS_COST if is_ev else PARTS_COST
    parts_html = ""
    for part, (lo, hi) in active_parts.items():
        parts_html += f'<div class="parts-card"><div class="parts-name">{part}</div><div class="parts-range">{lo} – {hi}</div></div>'
    st.markdown(parts_html, unsafe_allow_html=True)
    note = "EV prices vary widely by brand & warranty status." if is_ev else "Prices vary by city & bike brand."
    st.markdown(f'<div style="font-size:10px;color:#4b5563;margin-top:2px;">{note}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 12px 16px;"></div>', unsafe_allow_html=True)

    # ── Ride Log ─────────────────────────────────────────────────────────────
    # Feature 3: road condition tag added
    st.markdown('<div class="sb-section-title">📍 Ride Log</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 12px 12px;">', unsafe_allow_html=True)
    rl1, rl2 = st.columns(2)
    ride_km_in   = rl1.number_input("km ridden", min_value=1, value=50, step=5, key="rl_km")
    ride_date_in = rl2.date_input("Date", value=datetime.date.today(), key="rl_date")
    road_condition = st.selectbox(
        "Road Condition",
        ["🌞 Dry/City", "🌧️ Rain", "🛣️ Highway", "🌧️🛣️ Rainy Highway", "🪨 Off-road"],
        key="rl_cond",
        label_visibility="visible",
    )
    if st.button("➕  Log Ride", use_container_width=True, key="rl_add"):
        st.session_state.ride_log.append({
            "km": ride_km_in,
            "date": ride_date_in.strftime("%d %b %Y"),
            "condition": road_condition,
        })
        st.success(f"✅ {ride_km_in} km logged ({road_condition})")
        st.rerun()
    if st.session_state.ride_log:
        total_logged = sum(r["km"] for r in st.session_state.ride_log)
        st.markdown(f'<div style="font-size:11px;color:#6b7280;margin:4px 0 6px;">Total logged: <strong style="color:var(--orange)">{total_logged:,} km</strong></div>', unsafe_allow_html=True)
        recent = st.session_state.ride_log[-5:][::-1]
        ride_html = ""
        for r in recent:
            cond = r.get("condition", "")
            cond_short = cond.split(" ")[0] if cond else ""
            ride_html += f'<div class="ride-entry"><span class="ride-date">{r["date"]} <span class="road-tag">{cond_short}</span></span><span class="ride-km">+{r["km"]} km</span></div>'
        st.markdown(ride_html, unsafe_allow_html=True)
        if st.button("🗑️ Clear Ride Log", use_container_width=True, key="rl_clear"):
            st.session_state.ride_log = []
            st.rerun()
    else:
        st.markdown('<div style="font-size:12px;color:#4b5563;">No rides logged yet.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="padding:12px 20px 20px;text-align:center;">
      <div style="font-size:10px;color:#4b5563;font-weight:600;letter-spacing:0.5px;">
        Powered by Groq · Llama 3.3-70b · v6.2
      </div>
      <div style="font-size:10px;color:#374151;margin-top:2px;">⚡ EV + 🛢️ ICE · 🔒 Private · Secure</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════════════════════════════
bp = st.session_state.bike_profile
bike_label = (
    f"🏍️ {bp['model']}" + (f" · {bp['year']}" if bp.get("year") else "")
    if bp.get("model") else "🏍️ No Bike Set"
)
mode_label = "⚡ CONCISE" if st.session_state.response_mode == "concise" else "📚 DETAILED"
ev_badge = ' <span style="background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.35);border-radius:6px;padding:3px 8px;font-size:10px;color:#4ade80;font-weight:700;letter-spacing:1px;margin-left:6px;">⚡ EV MODE</span>' if st.session_state.bike_type == "EV" else ""

st.markdown(f"""
<div class="meva-topbar">
  <div class="topbar-icon">🏍️</div>
  <div>
    <div class="topbar-title">MEVA{ev_badge}</div>
    <div class="topbar-subtitle">Motorcycle Expert Virtual Assistant</div>
  </div>
  <div class="topbar-mode-badge">{mode_label}</div>
  <div class="topbar-status">
    <div class="status-pulse"></div>
    <span class="status-text">Online</span>
  </div>
  <div class="topbar-bike-tag">{bike_label}</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 5: OVERDUE SERVICE TOAST (auto-shows on load if any overdue)
# ══════════════════════════════════════════════════════════════════════════════
current_km = get_current_km()
active_intervals = EV_SERVICE_INTERVALS if st.session_state.bike_type == "EV" else SERVICE_INTERVALS
overdue_services = get_overdue_services(current_km)
if overdue_services:
    overdue_list = ", ".join(overdue_services[:4])
    if len(overdue_services) > 4:
        overdue_list += f" +{len(overdue_services)-4} more"
    st.markdown(f"""
    <div class="overdue-toast">
      <div class="overdue-toast-icon">🔔</div>
      <div class="overdue-toast-text">
        <strong>Service Overdue:</strong> {overdue_list} — check the Service Tracker in the sidebar.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# WELCOME CARD (only when no messages)
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome-wrap">
      <div class="welcome-card">
        <span class="welcome-emoji">🏍️</span>
        <div class="welcome-title">{t('welcome_title')} <span>MEVA</span></div>
        <div class="welcome-desc">
          {t('welcome_desc')}
        </div>
        <div class="welcome-pills">
          <span class="welcome-pill">{t('pill_maintenance')}</span>
          <span class="welcome-pill">{t('pill_diagnostics')}</span>
          <span class="welcome-pill">{t('pill_repairs')}</span>
          <span class="welcome-pill">{t('pill_costs')}</span>
          <span class="welcome-pill">{t('pill_safety')}</span>
          <span class="welcome-pill">{t('pill_fuel')}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)





# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 11: NEARBY SERVICE CENTER MAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="padding:12px 28px 0; box-sizing:border-box; width:100%; overflow:hidden;">', unsafe_allow_html=True)
def get_bike_brand(model_name: str, bike_type: str) -> str:
    """Extract brand from a model name using the bike lists."""
    source = EV_BIKES if bike_type == "EV" else ICE_BIKES
    for brand, models in source.items():
        if any(model_name.lower() in m.lower() or m.lower() in model_name.lower() for m in models):
            # Simplify brand label for search
            clean = brand.replace(" EV", "").replace(" Electric", "").replace(" / Yezdi", "").strip()
            return clean
    return ""

with st.expander("🗺️ Nearby Service Centers — find authorised workshops", expanded=False):
    bp_model = st.session_state.bike_profile.get("model", "")
    detected_brand = get_bike_brand(bp_model, st.session_state.bike_type) if bp_model else ""

    mc1, mc2 = st.columns(2)
    city_idx = SERVICE_CENTER_CITIES.index(st.session_state.service_city) if st.session_state.service_city in SERVICE_CENTER_CITIES else 0
    map_city = mc1.selectbox(
        "📍 Your City",
        SERVICE_CENTER_CITIES,
        index=city_idx,
        key="map_city_sel",
    )
    st.session_state.service_city = map_city

    map_brand = mc2.text_input(
        "🏷️ Brand / Type",
        value=detected_brand if detected_brand else ("Electric bike" if st.session_state.bike_type == "EV" else "motorcycle"),
        placeholder="e.g. Hero, Honda, Ather…",
        key="map_brand_input",
    )

    col_ev, col_info = st.columns([0.4, 0.6])
    search_radius = col_ev.selectbox(
        "📏 Radius",
        ["2 km", "5 km", "10 km", "20 km"],
        index=1,
        key="map_radius_sel",
    )
    show_map_btn = col_info.button(
        "🔍  Find Service Centers",
        use_container_width=True,
        key="map_find_btn",
        type="primary",
    )

    if show_map_btn or st.session_state.get("map_searched"):
        st.session_state.map_searched = True
        # Build Google Maps search URL for embedding
        radius_km = search_radius.replace(" km", "")
        query_parts = [map_brand, "service center", "authorised workshop", map_city, "India"]
        query = "+".join(p.replace(" ", "+") for p in query_parts if p)
        maps_embed_url = (
            f"https://www.google.com/maps/search/{query}/"
            f"@?entry=ttu"
        )
        # Use iframe embed — works without API key
        maps_search_url = (
            f"https://www.google.com/maps/search/"
            f"{map_brand.replace(' ', '+')}+service+center+{map_city.replace(' ', '+')}+India"
        )
        # Leaflet-based OpenStreetMap embed (no API key needed)
        # We'll build a Nominatim geocode call to get city center coords for the iframe
        import urllib.parse
        encoded_query = urllib.parse.quote(f"{map_brand} authorised service center {map_city}")

        # City bounding box lookup (approximate centers for major Indian cities)
        CITY_COORDS = {
            "Mumbai": (19.0760, 72.8777), "Delhi": (28.6139, 77.2090),
            "Bangalore": (12.9716, 77.5946), "Hyderabad": (17.3850, 78.4867),
            "Chennai": (13.0827, 80.2707), "Kolkata": (22.5726, 88.3639),
            "Pune": (18.5204, 73.8567), "Ahmedabad": (23.0225, 72.5714),
            "Jaipur": (26.9124, 75.7873), "Lucknow": (26.8467, 80.9462),
            "Surat": (21.1702, 72.8311), "Kanpur": (26.4499, 80.3319),
            "Nagpur": (21.1458, 79.0882), "Indore": (22.7196, 75.8577),
            "Bhopal": (23.2599, 77.4126), "Patna": (25.5941, 85.1376),
            "Vadodara": (22.3072, 73.1812), "Coimbatore": (11.0168, 76.9558),
            "Ludhiana": (30.9010, 75.8573), "Agra": (27.1767, 78.0081),
            "Visakhapatnam": (17.6868, 83.2185), "Vijayawada": (16.5062, 80.6480),
            "Kochi": (9.9312, 76.2673), "Nashik": (19.9975, 73.7898),
            "Madurai": (9.9252, 78.1198), "Mysore": (12.2958, 76.6394),
            "Chandigarh": (30.7333, 76.7794), "Guwahati": (26.1445, 91.7362),
            "Ranchi": (23.3441, 85.3096), "Bhubaneswar": (20.2961, 85.8245),
            "Thiruvananthapuram": (8.5241, 76.9366), "Noida": (28.5355, 77.3910),
            "Gurgaon": (28.4595, 77.0266), "Faridabad": (28.4089, 77.3178),
            "Meerut": (28.9845, 77.7064), "Varanasi": (25.3176, 82.9739),
            "Amritsar": (31.6340, 74.8723), "Jabalpur": (23.1815, 79.9864),
            "Jodhpur": (26.2389, 73.0243), "Rajkot": (22.3039, 70.8022),
            "Mangalore": (12.9141, 74.8560), "Hubli": (15.3647, 75.1240),
            "Belgaum": (15.8497, 74.4977), "Udaipur": (24.5854, 73.7125),
            "Dehradun": (30.3165, 78.0322), "Shimla": (31.1048, 77.1734),
            "Goa (Panaji)": (15.4909, 73.8278), "Pondicherry": (11.9416, 79.8083),
        }
        lat, lon = CITY_COORDS.get(map_city, (20.5937, 78.9629))  # fallback: India center
        zoom = 13

        osm_iframe = f"""
        <div style="border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.1);margin-top:10px;">
          <iframe
            width="100%" height="420"
            frameborder="0" scrolling="no" marginheight="0" marginwidth="0"
            src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.08},{lat-0.06},{lon+0.08},{lat+0.06}&amp;layer=mapnik&amp;marker={lat},{lon}"
            style="border:0;display:block;"
            allowfullscreen="">
          </iframe>
        </div>
        <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">
          <a href="https://www.google.com/maps/search/{encoded_query}" target="_blank"
             style="display:inline-flex;align-items:center;gap:6px;background:rgba(79,110,247,0.12);border:1px solid rgba(79,110,247,0.3);border-radius:8px;padding:7px 14px;font-size:12px;color:#818cf8;text-decoration:none;font-weight:600;">
            🗺️ Open in Google Maps
          </a>
          <a href="https://maps.apple.com/?q={encoded_query}" target="_blank"
             style="display:inline-flex;align-items:center;gap:6px;background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);border-radius:8px;padding:7px 14px;font-size:12px;color:#4ade80;text-decoration:none;font-weight:600;">
            🍎 Apple Maps
          </a>
        </div>
        <div style="margin-top:10px;background:rgba(249,115,22,0.07);border:1px solid rgba(249,115,22,0.2);border-radius:10px;padding:12px 14px;">
          <div style="font-size:11px;font-weight:700;color:#fb923c;letter-spacing:1px;margin-bottom:8px;">💡 SEARCH TIPS</div>
          <div style="font-size:12px;color:#9ca3af;line-height:1.7;">
            The map shows <strong style="color:#e8e8ed;">{map_city}</strong> centre.
            Click <em>Open in Google Maps</em> above to search for
            <strong style="color:#fb923c;">"{map_brand} service center {map_city}"</strong>
            with live results, ratings, and directions.<br><br>
            🔍 <strong style="color:#e8e8ed;">Pro tips:</strong> Search for
            "<em>{map_brand} authorised service center near me</em>" when you're on-location,
            or call the brand helpline to get the nearest ASC number.<br>
            {"⚡ For EV bikes, always prefer <strong style='color:#4ade80;'>brand-authorised EV service</strong> — third-party shops may void warranty or mishandle high-voltage systems." if st.session_state.bike_type == "EV" else "🔧 Always ask for <strong style='color:#fb923c;'>authorised service center</strong> to keep warranty valid."}
          </div>
        </div>
        """
        st.markdown(osm_iframe, unsafe_allow_html=True)

        # Helpline numbers
        BRAND_HELPLINES = {
            "Hero": "1800-266-0018", "Honda": "1800-108-1441",
            "Bajaj": "1800-233-6500", "TVS": "1800-258-7555",
            "Royal Enfield": "1800-210-0007", "Yamaha": "1800-420-1600",
            "Suzuki": "1800-200-0006", "KTM": "1800-212-4586",
            "Kawasaki": "+91 22 6222 5590", "BMW": "1800-419-2269",
            "Ola Electric": "1800-102-0180", "Ather": "1800-270-5543",
            "Bajaj EV": "1800-233-6500", "Hero EV": "1800-26-00018",
            "TVS EV": "1800-258-7555", "Revolt": "1800-123-4855",
        }
        # Match brand
        matched_helpline = None
        for brand_key, number in BRAND_HELPLINES.items():
            if brand_key.lower() in map_brand.lower() or map_brand.lower() in brand_key.lower():
                matched_helpline = (brand_key, number)
                break

        if matched_helpline:
            st.markdown(f"""
            <div style="margin-top:8px;background:rgba(251,191,36,0.07);border:1px solid rgba(251,191,36,0.2);border-radius:10px;padding:10px 14px;display:flex;align-items:center;gap:10px;">
              <span style="font-size:18px;">📞</span>
              <div>
                <div style="font-size:10px;color:#6b7280;font-weight:700;letter-spacing:1px;">BRAND HELPLINE</div>
                <div style="font-size:14px;color:#fbbf24;font-weight:700;font-family:var(--mono);">{matched_helpline[0]}: {matched_helpline[1]}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
if len(st.session_state.ride_log) >= 2:
    try:
        import pandas as pd
        st.markdown('<div class="mileage-chart-wrap">', unsafe_allow_html=True)
        with st.expander("📈 Mileage History Chart", expanded=False):
            rides = st.session_state.ride_log
            # Build chart data: km per ride with condition context
            chart_data = []
            for r in rides:
                chart_data.append({
                    "Date": r["date"],
                    "km": r["km"],
                    "Condition": r.get("condition", "Unknown"),
                })
            df = pd.DataFrame(chart_data)
            df["Ride #"] = range(1, len(df) + 1)

            st.markdown(f'<div style="font-size:12px;color:#6b7280;margin-bottom:8px;">Showing {len(df)} logged rides · Total: <strong style="color:var(--orange)">{df["km"].sum():,} km</strong> · Avg: <strong style="color:var(--amber)">{df["km"].mean():.0f} km/ride</strong></div>', unsafe_allow_html=True)

            # Use streamlit's native chart with custom color
            st.bar_chart(
                df.set_index("Ride #")["km"],
                use_container_width=True,
                height=180,
                color="#f97316",
            )

            # Condition breakdown table
            cond_counts = df["Condition"].value_counts().reset_index()
            cond_counts.columns = ["Condition", "Rides"]
            st.markdown('<div style="font-size:11px;color:#6b7280;margin-top:6px;">Ride conditions breakdown:</div>', unsafe_allow_html=True)
            st.dataframe(cond_counts, hide_index=True, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
    except ImportError:
        pass  # pandas not available, skip chart silently


# ══════════════════════════════════════════════════════════════════════════════
# CONVERSATION SEARCH
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.messages:
    st.markdown('<div class="search-bar-wrap">', unsafe_allow_html=True)
    search_q = st.text_input(
        "Search conversation", placeholder=f"🔍  {t('search_placeholder')}",
        value=st.session_state.search_query,
        key="search_input",
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.search_query = search_q

    if search_q:
        matches = sum(
            1 for m in st.session_state.messages
            if search_q.lower() in m["content"].lower()
        )
        st.markdown(
            f'<div class="search-result-count">{matches} message(s) match "{search_q}"</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# CHAT MESSAGES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

if st.session_state.messages:
    st.markdown(f"""
    <div class="date-chip">
      <span>{datetime.datetime.now().strftime('%A, %d %b %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

sq = st.session_state.search_query.lower()

for idx, msg in enumerate(st.session_state.messages):
    role    = msg["role"]
    content = msg["content"]
    ts      = msg.get("time", "")
    followups = msg.get("followups", [])
    is_last   = (idx == len(st.session_state.messages) - 1)
    is_err    = msg.get("error", False)

    # Filter by search
    if sq and sq not in content.lower():
        continue

    if role == "assistant":
        bubble_cls = "bot-bubble bot-bubble-err" if is_err else "bot-bubble"
        rendered   = render_md(content) if not is_err else content
        copy_data = json.dumps(content)   # produces a valid JS string literal incl. escaping
        copy_btn  = f'<button class="copy-btn" data-copy={copy_data} onclick="(function(b){{navigator.clipboard.writeText(b.dataset.copy).then(()=>{{b.textContent=\'✅ Copied\';setTimeout(()=>b.textContent=\'📋 Copy\',2000)}})}})(this)">📋 Copy</button>'
        st.markdown(f"""
        <div class="msg-bot">
          <div class="bot-av">🏍️</div>
          <div>
            <div class="{bubble_cls}">{rendered}</div>
            {copy_btn if not is_err else ""}
            {"<div class='msg-ts'>" + ts + "</div>" if ts else ""}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Feature 4: Rating buttons (thumbs up/down)
        if not is_err:
            current_rating = st.session_state.ratings.get(idx)
            r_col1, r_col2, r_col3 = st.columns([0.08, 0.08, 0.84])
            up_label   = "👍" if current_rating != "up"   else "✅"
            down_label = "👎" if current_rating != "down" else "❌"
            if r_col1.button(up_label,   key=f"rate_up_{idx}",   help="Helpful"):
                st.session_state.ratings[idx] = "up" if current_rating != "up" else None
                st.rerun()
            if r_col2.button(down_label, key=f"rate_down_{idx}", help="Not helpful"):
                st.session_state.ratings[idx] = "down" if current_rating != "down" else None
                st.rerun()

        if followups and is_last and not is_err:
            st.markdown('<div class="followup-wrap">', unsafe_allow_html=True)
            st.markdown('<div class="followup-head">💡 Suggested follow-ups</div>', unsafe_allow_html=True)
            for j, fq in enumerate(followups):
                if st.button(f"↗  {fq}", key=f"fq_{idx}_{j}"):
                    st.session_state.trigger = fq
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        safe_content = html_escape(content)
        disp = highlight_search(safe_content, html_escape(st.session_state.search_query)) if sq else safe_content
        st.markdown(f"""
        <div class="msg-user">
          <div class="user-av">👤</div>
          <div class="user-wrap">
            <div class="user-bubble">{disp}</div>
            {"<div class='msg-ts'>" + ts + "</div>" if ts else ""}
          </div>
        </div>
        """, unsafe_allow_html=True)

# Auto-scroll anchor
st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # chat-wrap


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TOPICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="quick-section">', unsafe_allow_html=True)
is_ev_mode = st.session_state.bike_type == "EV"
active_topics = EV_QUICK_TOPICS if is_ev_mode else QUICK_TOPICS
topic_label = f"⚡ {t('ev_quick_topics_label')}" if is_ev_mode else f"⚡ {t('quick_topics_label')}"
st.markdown(f'<div class="quick-head">{topic_label}</div>', unsafe_allow_html=True)
cols = st.columns(4)
for i, (emoji, label) in enumerate(active_topics):
    if cols[i % 4].button(f"{emoji} {label}", key=f"qr_{i}"):
        st.session_state.trigger = label
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
user_input = st.chat_input(t("chat_input_placeholder"))

if st.session_state.trigger:
    user_input = st.session_state.trigger
    st.session_state.trigger = None

if user_input and user_input.strip():
    text = user_input.strip()
    ts   = now_time()

    # ── Urgency detection banner ──────────────────────────────────────────────
    if is_urgent(text):
        st.markdown(f"""
        <div class="urgency-banner">
          <span class="urgency-icon">🚨</span>
          <div class="urgency-text">
            <strong>Safety Alert:</strong> This sounds like an urgent issue. Pull over safely if riding.
            MEVA will help diagnose — but visit a mechanic immediately if in doubt.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "user", "content": text, "time": ts, "followups": [], "error": False,
    })

    st.markdown(f"""
    <div class="msg-user">
      <div class="user-av">👤</div>
      <div class="user-wrap">
        <div class="user-bubble">{html_escape(text)}</div>
        <div class="msg-ts">{ts}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="typing-indicator">
      <div class="bot-av">🏍️</div>
      <div class="typing-bubble">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    content, followups = call_groq(
        st.session_state.messages,
        st.session_state.bike_profile,
        st.session_state.response_mode,
    )
    is_err = content is None
    if is_err:
        content, followups = followups, []

    t2 = now_time()
    st.session_state.messages.append({
        "role": "assistant", "content": content, "time": t2,
        "followups": followups, "error": is_err,
    })
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# VOICE INPUT — Web Speech API floating mic
# ══════════════════════════════════════════════════════════════════════════════
safe_markdown("""
<button id="meva-mic-btn" title="Voice Input (click to speak)">🎙️</button>
<script>
(function() {
  const btn = document.getElementById('meva-mic-btn');
  if (!btn) return;
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    btn.title = 'Voice input not supported in this browser';
    btn.style.opacity = '0.4';
    btn.style.cursor = 'not-allowed';
    return;
  }
  const rec = new SpeechRec();
  rec.lang = 'en-IN';
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  let listening = false;
  btn.addEventListener('click', () => { if (listening) { rec.stop(); return; } rec.start(); });
  rec.onstart  = () => { listening = true;  btn.classList.add('listening');    btn.textContent = '\u23F9\uFE0F'; btn.title = 'Listening\u2026 click to stop'; };
  rec.onend    = () => { listening = false; btn.classList.remove('listening'); btn.textContent = '\uD83C\uDF99\uFE0F'; btn.title = 'Voice Input (click to speak)'; };
  rec.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    const ta = document.querySelector('[data-testid="stChatInput"] textarea');
    if (ta) {
      const nativeInput = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
      nativeInput.set.call(ta, transcript);
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      ta.focus();
    }
  };
  rec.onerror = (e) => { btn.title = 'Error: ' + e.error; };
})();
</script>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 10: KEYBOARD SHORTCUT — Ctrl+K focuses chat input
# ══════════════════════════════════════════════════════════════════════════════
safe_markdown("""
<script>
(function() {
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const ta = document.querySelector('[data-testid="stChatInput"] textarea');
      if (ta) {
        ta.focus();
        ta.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  });
})();
</script>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-SCROLL TO BOTTOM
# ══════════════════════════════════════════════════════════════════════════════
safe_markdown("""
<script>
(function autoScroll() {
  function scroll() {
    const el = document.getElementById('chat-bottom');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }
  setTimeout(scroll, 400);
  setTimeout(scroll, 900);
})();
</script>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# JS — Dynamically style sidebar toggle button
# ══════════════════════════════════════════════════════════════════════════════
safe_markdown("""
<script>
(function patchSidebarBtn() {
  function styleBtn(btn) {
    if (!btn || btn._mevaDone) return;
    btn._mevaDone = true;
    Object.assign(btn.style, {
      background: '#1a1a20', border: '1px solid rgba(249,115,22,0.45)',
      borderRadius: '10px', width: '38px', height: '38px',
      minWidth: '38px', minHeight: '38px',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      cursor: 'pointer', boxShadow: '0 0 14px rgba(249,115,22,0.2)',
      transition: 'all 0.2s cubic-bezier(0.4,0,0.2,1)',
      position: 'relative', overflow: 'hidden',
    });
    const svg = btn.querySelector('svg');
    if (svg) svg.style.display = 'none';
    if (!btn.querySelector('.meva-icon')) {
      const ic = document.createElement('span');
      ic.className = 'meva-icon';
      ic.textContent = '&#x1F3CD;&#xFE0F;';
      Object.assign(ic.style, { fontSize:'19px', lineHeight:'1', pointerEvents:'none' });
      btn.appendChild(ic);
    }
    btn.addEventListener('mouseenter', () => Object.assign(btn.style, {
      background: 'rgba(249,115,22,0.16)', borderColor: 'rgba(249,115,22,0.75)',
      boxShadow: '0 0 22px rgba(249,115,22,0.4)', transform: 'scale(1.1)',
    }));
    btn.addEventListener('mouseleave', () => Object.assign(btn.style, {
      background: '#1a1a20', borderColor: 'rgba(249,115,22,0.45)',
      boxShadow: '0 0 14px rgba(249,115,22,0.2)', transform: 'scale(1)',
    }));
  }
  function findAndPatch() {
    ['[data-testid="stSidebarCollapseButton"]','[data-testid="collapsedControl"]',
     'button[aria-label="Close sidebar"]','button[aria-label="Open sidebar"]',
     'button[aria-label="collapse sidebar"]','button[aria-label="expand sidebar"]',
    ].forEach(sel => document.querySelectorAll(sel).forEach(styleBtn));
  }
  findAndPatch();
  new MutationObserver(findAndPatch).observe(document.body, { childList:true, subtree:true });
})();
</script>
""", unsafe_allow_html=True)
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.entities import (
    User, UserRole, Property, Booking, BookingStatus, 
    PaymentStatus, Review, Favourite, RecommendationFeedback
)
from backend.app.utils.geo import CHENNAI_NEIGHBOURHOODS

# High quality demonstration imagery from curated architecture/workspace photo collections
DEMO_IMAGES = {
    "workspace_studio": [
        "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=800&q=80",
    ],
    "private_room": [
        "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80",
    ],
    "guest_suite": [
        "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=800&q=80",
    ],
    "entire_apartment": [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
    ],
    "day_cabin": [
        "https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=800&q=80",
    ],
}

PROPERTIES_DATA = [
    # 1. Guindy
    {
        "title": "Olympia Tech Quiet Work Hub",
        "description": "Ergonomic executive desk with fiber gigabit internet, dual monitors, and complimentary espresso. Ideal for tech professionals needing 2-4 hours of undisturbed productivity near Guindy Metro.",
        "property_type": "workspace_studio",
        "neighbourhood": "Guindy",
        "lat_offset": 0.002, "lon_offset": 0.003,
        "public_location_description": "2 mins walk from Guindy Metro Station and Olympia Tech Park",
        "exact_address": "Suite 304, Green Tree Towers, GST Road, Guindy, Chennai 600032",
        "price_per_hour": 280.0, "price_per_half_day": 1100.0, "price_per_day": 2100.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "work_desk", "power_backup", "coffee_tea", "quiet_zone"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "No smoking. Maintain low phone call volume in common areas.",
    },
    {
        "title": "Transit Day Suite at Guindy",
        "description": "Comfortable private bedroom with en-suite shower, luggage storage, and blackout blinds for travelers with long layovers or early morning meetings.",
        "property_type": "private_room",
        "neighbourhood": "Guindy",
        "lat_offset": -0.003, "lon_offset": -0.002,
        "public_location_description": "Close to Kathipara Junction and Airport corridor",
        "exact_address": "Flat 12B, Park Avenue Enclave, Race Course Road, Guindy, Chennai 600032",
        "price_per_hour": 350.0, "price_per_half_day": 1400.0, "price_per_day": 2600.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "power_backup", "parking"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "Government photo ID required at check-in. Quiet hours after 10 PM.",
    },
    {
        "title": "Guindy Executive Conference Studio",
        "description": "Modern mini-boardroom setup seating up to 6 persons, complete with 4K HDMI presentation display and video conferencing camera.",
        "property_type": "workspace_studio",
        "neighbourhood": "Guindy",
        "lat_offset": 0.005, "lon_offset": -0.004,
        "public_location_description": "Near Guindy Industrial Estate Main Road",
        "exact_address": "Plot 45, SIDCO Industrial Estate, Guindy, Chennai 600032",
        "price_per_hour": 600.0, "price_per_half_day": 2400.0, "price_per_day": 4500.0,
        "maximum_guests": 6,
        "amenities": ["wifi", "air_conditioning", "work_desk", "power_backup", "parking", "coffee_tea"],
        "supported_durations": ["hourly", "half_day"],
        "house_rules": "Respect reservation slot timings. Outside catering permitted with prior notice.",
    },

    # 2. Velachery
    {
        "title": "Phoenix Mall Cozy Studio Retreat",
        "description": "Bright, air-conditioned studio apartment directly opposite Phoenix MarketCity. Perfect for a relaxing shopping break or remote work afternoon.",
        "property_type": "entire_apartment",
        "neighbourhood": "Velachery",
        "lat_offset": 0.003, "lon_offset": 0.002,
        "public_location_description": "Opposite Phoenix MarketCity Velachery",
        "exact_address": "Unit 402, Royal Palms, Velachery Bypass Road, Chennai 600042",
        "price_per_hour": 400.0, "price_per_half_day": 1600.0, "price_per_day": 2900.0,
        "maximum_guests": 3,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "kitchenette", "power_backup", "parking"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "No parties or loud music. Self-checkin with smart lock.",
    },
    {
        "title": "Velachery Garden Work Pod",
        "description": "Private standalone garden cabin with tranquil greenery, noise-cancellation acoustics, high-speed Wi-Fi, and artisanal pour-over coffee.",
        "property_type": "day_cabin",
        "neighbourhood": "Velachery",
        "lat_offset": -0.004, "lon_offset": 0.004,
        "public_location_description": "Quiet residential street near Dhandeeswaram Nagar",
        "exact_address": "7/2, 3rd Main Road, Dhandeeswaram Nagar, Velachery, Chennai 600042",
        "price_per_hour": 220.0, "price_per_half_day": 850.0, "price_per_day": 1600.0,
        "maximum_guests": 1,
        "amenities": ["wifi", "air_conditioning", "work_desk", "coffee_tea", "quiet_zone"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Strictly single occupant. Peaceful residential ambiance.",
    },
    {
        "title": "Velachery Lakeview Guest Suite",
        "description": "Serene bedroom with a balcony overlooking the lake. Enjoy cross-breeze ventilation, cozy lounge seating, and an ensuite bath.",
        "property_type": "guest_suite",
        "neighbourhood": "Velachery",
        "lat_offset": 0.006, "lon_offset": -0.003,
        "public_location_description": "Near Velachery Lake Promenade",
        "exact_address": "22 Lake View Drive, AGS Colony, Velachery, Chennai 600042",
        "price_per_hour": 320.0, "price_per_half_day": 1300.0, "price_per_day": 2400.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "power_backup", "parking"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Balcony door must be kept latched during monsoons.",
    },

    # 3. Adyar
    {
        "title": "Kasturba Nagar Designer Workstation",
        "description": "Sunlit creative workspace located in a charming colonial-inspired bungalow. High ceilings, standing desk converter, and leafy terrace.",
        "property_type": "workspace_studio",
        "neighbourhood": "Adyar",
        "lat_offset": 0.002, "lon_offset": -0.002,
        "public_location_description": "Heart of Kasturba Nagar, walking distance to cafes",
        "exact_address": "14, 2nd Cross Street, Kasturba Nagar, Adyar, Chennai 600020",
        "price_per_hour": 250.0, "price_per_half_day": 950.0, "price_per_day": 1800.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "work_desk", "power_backup", "coffee_tea", "quiet_zone"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Shoes off inside the studio please.",
    },
    {
        "title": "Adyar Riverbank Rest Haven",
        "description": "Quiet private room tucked away in green Adyar. Soft natural linens, hot shower, filtered RO water, and high-speed Wi-Fi.",
        "property_type": "private_room",
        "neighbourhood": "Adyar",
        "lat_offset": -0.003, "lon_offset": 0.003,
        "public_location_description": "Near Theosophical Society gardens",
        "exact_address": "8 River View Enclave, Gandhi Nagar, Adyar, Chennai 600020",
        "price_per_hour": 300.0, "price_per_half_day": 1200.0, "price_per_day": 2200.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "quiet_zone", "parking"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "Respect neighborhood quiet hours.",
    },
    {
        "title": "Besant Avenue Coastal Flat",
        "description": "Breezy entire apartment 5 minutes drive from Elliot's Beach. Spacious living room, dining nook, and full kitchen.",
        "property_type": "entire_apartment",
        "neighbourhood": "Adyar",
        "lat_offset": 0.004, "lon_offset": 0.005,
        "public_location_description": "Off Besant Avenue Road, near Elliot's Beach",
        "exact_address": "Flat 3A, Sea Breeze Manor, Besant Avenue, Adyar, Chennai 600020",
        "price_per_hour": 500.0, "price_per_half_day": 2000.0, "price_per_day": 3600.0,
        "maximum_guests": 4,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "kitchenette", "parking", "power_backup"],
        "supported_durations": ["half_day", "full_day", "multi_day"],
        "house_rules": "Beach sand to be washed off at ground floor tap before entering.",
    },

    # 4. T. Nagar
    {
        "title": "Pondy Bazaar Shopper's Rest Stop",
        "description": "Air-conditioned private room to recharge between shopping sprees. Secure bag storage, clean shower, and electric kettle.",
        "property_type": "private_room",
        "neighbourhood": "T. Nagar",
        "lat_offset": 0.002, "lon_offset": 0.001,
        "public_location_description": "Just off Pondy Bazaar Pedestrian Plaza",
        "exact_address": "52 Sivaprakasam Street, T. Nagar, Chennai 600017",
        "price_per_hour": 220.0, "price_per_half_day": 850.0, "price_per_day": 1600.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "power_backup"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "No unregistered visitors allowed.",
    },
    {
        "title": "Panagal Park Executive Lounge",
        "description": "Chic 1-bedroom suite featuring Italian leather recliner, 50-inch smart TV, high-speed Wi-Fi, and soundproof double-glazed windows.",
        "property_type": "guest_suite",
        "neighbourhood": "T. Nagar",
        "lat_offset": -0.003, "lon_offset": -0.002,
        "public_location_description": "2 minutes walk from Panagal Park",
        "exact_address": "Flat 201, Elite Residency, Usman Road, T. Nagar, Chennai 600017",
        "price_per_hour": 450.0, "price_per_half_day": 1800.0, "price_per_day": 3200.0,
        "maximum_guests": 3,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "work_desk", "parking", "coffee_tea"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "Strictly non-smoking property.",
    },
    {
        "title": "T. Nagar Creator Day Studio",
        "description": "Content creator day studio equipped with ring lights, neutral backdrop panels, ultra-fast broadband, and acoustic baffling.",
        "property_type": "workspace_studio",
        "neighbourhood": "T. Nagar",
        "lat_offset": 0.005, "lon_offset": 0.003,
        "public_location_description": "Near G.N. Chetty Road commercial strip",
        "exact_address": "18 North Boag Road, T. Nagar, Chennai 600017",
        "price_per_hour": 400.0, "price_per_half_day": 1500.0, "price_per_day": 2800.0,
        "maximum_guests": 4,
        "amenities": ["wifi", "air_conditioning", "work_desk", "power_backup", "quiet_zone"],
        "supported_durations": ["hourly", "half_day"],
        "house_rules": "Equipment handling with care. Cleanup after production.",
    },

    # 5. Anna Nagar
    {
        "title": "Tower Park Green Sanctuary",
        "description": "Quiet modern apartment overlooking the tree canopy of Anna Nagar Tower Park. Premium workstation with Herman Miller ergonomic chair.",
        "property_type": "entire_apartment",
        "neighbourhood": "Anna Nagar",
        "lat_offset": 0.002, "lon_offset": 0.003,
        "public_location_description": "Directly facing Anna Nagar Tower Park entrance",
        "exact_address": "Penthouse B, Tower View Apartments, 3rd Avenue, Anna Nagar, Chennai 600040",
        "price_per_hour": 480.0, "price_per_half_day": 1900.0, "price_per_day": 3500.0,
        "maximum_guests": 4,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "work_desk", "parking", "coffee_tea", "power_backup"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "No unauthorized parties. Pet-friendly with prior notification.",
    },
    {
        "title": "Shanti Colony Designer Pod",
        "description": "Minimalist Scandinavian-style compact studio for digital nomads and focused researchers. High-speed broadband and silent AC.",
        "property_type": "day_cabin",
        "neighbourhood": "Anna Nagar",
        "lat_offset": -0.003, "lon_offset": -0.002,
        "public_location_description": "Steps from Shanti Colony gourmet restaurants",
        "exact_address": "12 Shanti Colony 4th Avenue, Anna Nagar West, Chennai 600040",
        "price_per_hour": 240.0, "price_per_half_day": 900.0, "price_per_day": 1700.0,
        "maximum_guests": 1,
        "amenities": ["wifi", "air_conditioning", "work_desk", "coffee_tea", "quiet_zone"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Only one guest. Perfect for focused work or Zoom calls.",
    },
    {
        "title": "Anna Nagar East Family Suite",
        "description": "Spacious two-bedroom short-stay home with comfortable bedding, child-safe amenities, and parking space for an SUV.",
        "property_type": "entire_apartment",
        "neighbourhood": "Anna Nagar",
        "lat_offset": 0.004, "lon_offset": -0.004,
        "public_location_description": "Near Anna Nagar East Metro Station",
        "exact_address": "Flat 101, Oakwood Residency, 6th Avenue, Anna Nagar, Chennai 600102",
        "price_per_hour": 550.0, "price_per_half_day": 2200.0, "price_per_day": 4000.0,
        "maximum_guests": 5,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "parking", "kitchenette", "power_backup"],
        "supported_durations": ["half_day", "full_day", "multi_day"],
        "house_rules": "Quiet hours 10 PM - 7 AM.",
    },

    # 6. Mylapore
    {
        "title": "Kapaleeshwarar Heritage Day Room",
        "description": "Traditional South Indian courtyard home with teak wood pillars, brass touches, modern high-speed Wi-Fi, and cool limestone floors.",
        "property_type": "private_room",
        "neighbourhood": "Mylapore",
        "lat_offset": 0.001, "lon_offset": 0.002,
        "public_location_description": "Near Kapaleeshwarar Temple North Tank Street",
        "exact_address": "24 North Mada Street, Mylapore, Chennai 600004",
        "price_per_hour": 260.0, "price_per_half_day": 1000.0, "price_per_day": 1900.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "coffee_tea", "quiet_zone"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Vegetarian household. Traditional home etiquette appreciated.",
    },
    {
        "title": "Luz Corner Meeting & Rest Suite",
        "description": "Conveniently situated near Luz Church road, this quiet room offers an oasis of calm with a plush daybed and writing bureau.",
        "property_type": "guest_suite",
        "neighbourhood": "Mylapore",
        "lat_offset": -0.002, "lon_offset": -0.003,
        "public_location_description": "Near Luz Church Road intersection",
        "exact_address": "8B, Temple View Court, Luz Church Road, Mylapore, Chennai 600004",
        "price_per_hour": 340.0, "price_per_half_day": 1350.0, "price_per_day": 2500.0,
        "maximum_guests": 3,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "work_desk", "power_backup"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Check-out on scheduled time to facilitate prompt room sanitization.",
    },

    # 7. OMR (Thoraipakkam)
    {
        "title": "OMR Cyber Corridor Dev Studio",
        "description": "High-octane coder's studio with dual 4K monitors, mechanical keyboard, standing desk, 500 Mbps redundant fiber, and backup UPS.",
        "property_type": "workspace_studio",
        "neighbourhood": "OMR (Thoraipakkam)",
        "lat_offset": 0.003, "lon_offset": 0.002,
        "public_location_description": "Near ASV Suntech Park, OMR Expressway",
        "exact_address": "Tech Bay 102, Silicon Heights, Rajiv Gandhi Salai, Thoraipakkam, Chennai 600097",
        "price_per_hour": 300.0, "price_per_half_day": 1150.0, "price_per_day": 2200.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "work_desk", "power_backup", "coffee_tea", "parking"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Developer friendly. High volume coding allowed 24/7.",
    },
    {
        "title": "Thoraipakkam Lakeview Executive Flat",
        "description": "Modern high-rise condo offering panoramic sunset views over the marshlands. Smart TV with streaming, full modular kitchen, and swimming pool access.",
        "property_type": "entire_apartment",
        "neighbourhood": "OMR (Thoraipakkam)",
        "lat_offset": -0.004, "lon_offset": -0.003,
        "public_location_description": "Off Radial Road, near Toll Plaza",
        "exact_address": "Tower 4, Apt 1403, Cyber City Residences, Thoraipakkam, Chennai 600097",
        "price_per_hour": 520.0, "price_per_half_day": 2100.0, "price_per_day": 3800.0,
        "maximum_guests": 4,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "parking", "kitchenette", "power_backup"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "Building security requires digital pass check-in at gate.",
    },

    # 8. Nungambakkam
    {
        "title": "College Road Diplomatic Haven",
        "description": "Stately private room in upscale Nungambakkam. Polished rosewood writing desk, ensuite marble bath, and shaded driveway parking.",
        "property_type": "private_room",
        "neighbourhood": "Nungambakkam",
        "lat_offset": 0.002, "lon_offset": -0.002,
        "public_location_description": "Off College Road, near Alliance Française",
        "exact_address": "15 College Road, Nungambakkam, Chennai 600006",
        "price_per_hour": 380.0, "price_per_half_day": 1500.0, "price_per_day": 2800.0,
        "maximum_guests": 2,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "work_desk", "parking", "quiet_zone"],
        "supported_durations": ["hourly", "half_day", "full_day", "multi_day"],
        "house_rules": "Strict privacy assured. Quiet residential zone.",
    },
    {
        "title": "Khader Nawaz Khan Designer Lounge",
        "description": "Exclusive boutique lounge located above upscale fashion cafes on KNK road. Perfect for private client meetings or luxury day rest.",
        "property_type": "guest_suite",
        "neighbourhood": "Nungambakkam",
        "lat_offset": -0.003, "lon_offset": 0.003,
        "public_location_description": "Heart of Khader Nawaz Khan Road",
        "exact_address": "Suite 5, KNK Galleria, Khader Nawaz Khan Road, Chennai 600006",
        "price_per_hour": 580.0, "price_per_half_day": 2300.0, "price_per_day": 4200.0,
        "maximum_guests": 3,
        "amenities": ["wifi", "air_conditioning", "private_restroom", "work_desk", "coffee_tea", "parking", "power_backup"],
        "supported_durations": ["hourly", "half_day", "full_day"],
        "house_rules": "Commercial photography requires prior approval.",
    },
]

DEMO_USERS = [
    {
        "name": "Harish Renter",
        "email": "renter@staynearby.dev",
        "password": "demopass123",
        "role": UserRole.RENTER.value,
        "preferred_budget": 400.0,
        "preferred_amenities": ["wifi", "air_conditioning", "work_desk"],
    },
    {
        "name": "Priya Traveler",
        "email": "traveller@staynearby.dev",
        "password": "demopass123",
        "role": UserRole.RENTER.value,
        "preferred_budget": 800.0,
        "preferred_amenities": ["parking", "private_restroom", "power_backup"],
    },
    {
        "name": "Karthik Host",
        "email": "host@staynearby.dev",
        "password": "demopass123",
        "role": UserRole.HOST.value,
        "preferred_budget": None,
        "preferred_amenities": [],
    },
    {
        "name": "Meera Host",
        "email": "host2@staynearby.dev",
        "password": "demopass123",
        "role": UserRole.HOST.value,
        "preferred_budget": None,
        "preferred_amenities": [],
    },
    {
        "name": "System Administrator",
        "email": "admin@staynearby.dev",
        "password": "adminpass123",
        "role": UserRole.ADMIN.value,
        "preferred_budget": None,
        "preferred_amenities": [],
    },
]

def seed_database():
    print("=== Seeding StayNearby Database ===")
    db = SessionLocal()
    try:
        # 1. Seed Users (Idempotent: skip existing emails)
        users_map = {}
        for u_data in DEMO_USERS:
            existing = db.query(User).filter(User.email == u_data["email"]).first()
            if not existing:
                u = User(
                    name=u_data["name"],
                    email=u_data["email"],
                    password_hash=get_password_hash(u_data["password"]),
                    role=u_data["role"],
                    preferred_budget=u_data["preferred_budget"],
                    preferred_amenities=u_data["preferred_amenities"],
                )
                db.add(u)
                db.commit()
                db.refresh(u)
                users_map[u.email] = u
                print(f"Created user: {u.email} ({u.role})")
            else:
                users_map[u_data["email"]] = existing

        host1 = users_map["host@staynearby.dev"]
        host2 = users_map["host2@staynearby.dev"]
        renter1 = users_map["renter@staynearby.dev"]
        renter2 = users_map["traveller@staynearby.dev"]

        # 2. Seed Properties (Idempotent: skip existing title)
        created_properties = []
        for idx, p_data in enumerate(PROPERTIES_DATA):
            existing = db.query(Property).filter(Property.title == p_data["title"]).first()
            if not existing:
                area_coords = CHENNAI_NEIGHBOURHOODS.get(p_data["neighbourhood"], (13.0, 80.2))
                lat = round(area_coords[0] + p_data["lat_offset"], 6)
                lon = round(area_coords[1] + p_data["lon_offset"], 6)
                host = host1 if (idx % 2 == 0) else host2
                
                # Image list
                imgs = DEMO_IMAGES.get(p_data["property_type"], DEMO_IMAGES["workspace_studio"])

                prop = Property(
                    host_id=host.id,
                    title=p_data["title"],
                    description=p_data["description"],
                    property_type=p_data["property_type"],
                    neighbourhood=p_data["neighbourhood"],
                    latitude=lat,
                    longitude=lon,
                    public_location_description=p_data["public_location_description"],
                    exact_address=p_data["exact_address"],
                    price_per_hour=p_data["price_per_hour"],
                    price_per_half_day=p_data["price_per_half_day"],
                    price_per_day=p_data["price_per_day"],
                    maximum_guests=p_data["maximum_guests"],
                    amenities=p_data["amenities"],
                    supported_durations=p_data["supported_durations"],
                    house_rules=p_data["house_rules"],
                    images=imgs,
                    active=True,
                )
                db.add(prop)
                db.commit()
                db.refresh(prop)
                created_properties.append(prop)
            else:
                created_properties.append(existing)

        print(f"Total active properties in database: {len(created_properties)}")

        # 3. Seed Sample Bookings & Reviews
        sample_reviews_text = [
            (5.0, "Incredible setup! Gigabit wifi was rock solid for my 3-hour client video calls. Will definitely book again."),
            (4.5, "Very clean and quiet room. Great air conditioning and easy access. Perfect place to rest."),
            (5.0, "Host was very responsive. The workspace setup had multiple power outlets and a super comfortable chair."),
            (4.0, "Great location near the metro station. Check-in was smooth and straightforward."),
            (5.0, "Exceptional cleanliness and complimentary coffee. Exactly what I needed during my transit layover!"),
        ]

        now = datetime.now(timezone.utc)
        for i, prop in enumerate(created_properties[:8]):
            # Check if booking exists for this property
            b_existing = db.query(Booking).filter(Booking.property_id == prop.id).first()
            if not b_existing:
                renter = renter1 if (i % 2 == 0) else renter2
                b_start = now - timedelta(days=2 + i, hours=4)
                b_end = b_start + timedelta(hours=3)
                
                booking = Booking(
                    renter_id=renter.id,
                    property_id=prop.id,
                    start_datetime=b_start,
                    end_datetime=b_end,
                    duration_type="hourly",
                    guest_count=1,
                    base_price=round(prop.price_per_hour * 3, 2),
                    fees=round(prop.price_per_hour * 3 * 0.05, 2),
                    total_price=round(prop.price_per_hour * 3 * 1.05, 2),
                    status=BookingStatus.COMPLETED.value,
                    payment_status=PaymentStatus.SIMULATED_PAID.value,
                    created_at=b_start - timedelta(days=1),
                )
                db.add(booking)
                db.commit()
                db.refresh(booking)

                # Add review
                rating, text = sample_reviews_text[i % len(sample_reviews_text)]
                review = Review(
                    booking_id=booking.id,
                    renter_id=renter.id,
                    property_id=prop.id,
                    rating=rating,
                    review_text=text,
                    created_at=b_end + timedelta(hours=1),
                )
                db.add(review)
                db.commit()

        # Seed 1 upcoming confirmed booking & 1 pending booking
        if len(created_properties) >= 10:
            target_p = created_properties[0]
            existing_conf = db.query(Booking).filter(
                Booking.property_id == target_p.id,
                Booking.status == BookingStatus.CONFIRMED.value
            ).first()
            if not existing_conf:
                future_start = now + timedelta(days=1, hours=2)
                future_end = future_start + timedelta(hours=4)
                conf_b = Booking(
                    renter_id=renter1.id,
                    property_id=target_p.id,
                    start_datetime=future_start,
                    end_datetime=future_end,
                    duration_type="hourly",
                    guest_count=1,
                    base_price=round(target_p.price_per_hour * 4, 2),
                    fees=round(target_p.price_per_hour * 4 * 0.05, 2),
                    total_price=round(target_p.price_per_hour * 4 * 1.05, 2),
                    status=BookingStatus.CONFIRMED.value,
                    payment_status=PaymentStatus.SIMULATED_PAID.value,
                )
                db.add(conf_b)
                db.commit()

            # Pending request for host2
            target_p2 = created_properties[1]
            existing_pend = db.query(Booking).filter(
                Booking.property_id == target_p2.id,
                Booking.status == BookingStatus.PENDING.value
            ).first()
            if not existing_pend:
                pend_start = now + timedelta(days=2, hours=1)
                pend_end = pend_start + timedelta(hours=6)
                pend_b = Booking(
                    renter_id=renter2.id,
                    property_id=target_p2.id,
                    start_datetime=pend_start,
                    end_datetime=pend_end,
                    duration_type="half_day",
                    guest_count=2,
                    base_price=target_p2.price_per_half_day,
                    fees=round(target_p2.price_per_half_day * 0.05, 2),
                    total_price=round(target_p2.price_per_half_day * 1.05, 2),
                    status=BookingStatus.PENDING.value,
                    payment_status=PaymentStatus.SIMULATED_PAID.value,
                )
                db.add(pend_b)
                db.commit()

        # Seed sample favourite
        if len(created_properties) >= 3:
            fav_existing = db.query(Favourite).filter(Favourite.user_id == renter1.id).first()
            if not fav_existing:
                fav = Favourite(user_id=renter1.id, property_id=created_properties[0].id)
                db.add(fav)
                db.commit()

        print("Database seed completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

class FirstAidService:
    GUIDES = {
        "cpr": {
            "title": "Cardiopulmonary Resuscitation (CPR) Guide",
            "steps": [
                "1. Confirm safety and check responsiveness.",
                "2. Call emergency services (911 or localized rescue) immediately.",
                "3. Position the victim flat on their back on a firm surface.",
                "4. Perform chest compressions: push hard and fast in the center of the chest (100-120 per minute, 2 inches deep).",
                "5. Open the airway and provide rescue breaths (if trained) in a 30:2 ratio.",
                "6. Continue cycles until professional responders arrive or an AED is ready."
            ],
            "warnings": ["Do not interrupt compressions for more than 10 seconds.", "Avoid excessive ventilation."]
        },
        "bleeding": {
            "title": "Severe Hemorrhage Control Guide",
            "steps": [
                "1. Wear protective gloves if available.",
                "2. Apply direct, firm pressure on the wound with a clean sterile dressing.",
                "3. Elevate the injured limb above the heart level if possible.",
                "4. If bleeding doesn't stop, apply a secondary pressure bandage.",
                "5. For severe extremity arterial bleeding, prepare and apply a tourniquet 2-3 inches above the wound.",
                "6. Monitor victim closely for signs of shock."
            ],
            "warnings": ["Do not remove the primary soaked dressing; add more layers on top.", "Do not apply tourniquets directly over joints."]
        },
        "burns": {
            "title": "Thermal Burns Management Guide",
            "steps": [
                "1. Stop the burning process: eliminate the heat source.",
                "2. Cool the burn using cool running tap water for at least 10 minutes.",
                "3. Remove restrictive items like rings or clothing before swelling begins.",
                "4. Cover the burn loosely with sterile non-adherent gauze or clean plastic wrap.",
                "5. Keep the victim warm to prevent hypothermia.",
                "6. Seek urgent medical attention for 2nd/3rd-degree burns or facial burns."
            ],
            "warnings": ["Do not use ice, ice water, butter, or ointments on the burn.", "Do not pop blisters."]
        },
        "fractures": {
            "title": "Fracture and Bone Splinting Guide",
            "steps": [
                "1. Keep the injured area completely still. Do not try to realign the bone.",
                "2. Control any bleeding by applying direct pressure on the surrounding tissue.",
                "3. Apply a cold pack wrapped in a cloth to reduce swelling.",
                "4. Splint the joint above and below the fracture site to prevent movement.",
                "5. Check circulation below the splint (pulses, warmth, color).",
                "6. Keep the victim calm and warm while waiting for rescue."
            ],
            "warnings": ["Do not force a protruding bone back into the wound.", "Do not wrap splints too tightly to restrict circulation."]
        },
        "shock": {
            "title": "Shock Management Guide",
            "steps": [
                "1. Lay the victim down on their back and elevate their legs 12 inches (if no head, neck, or spine injuries are suspected).",
                "2. Keep the victim warm and comfortable using blankets.",
                "3. Loosen tight clothing around their neck, chest, and waist.",
                "4. Monitor breathing and pulse; prepare to perform CPR if they stop breathing.",
                "5. Reassure the victim and keep them calm."
            ],
            "warnings": ["Do not give the victim anything to eat or drink.", "Do not move the victim if a spinal injury is suspected."]
        }
    }

    @classmethod
    def get_instructions(cls, query: str) -> dict:
        q_lower = query.lower()
        matched_key = None

        # Simple keyword matching
        if "cpr" in q_lower or "unconscious" in q_lower or "breathing" in q_lower:
            matched_key = "cpr"
        elif "bleed" in q_lower or "blood" in q_lower or "wound" in q_lower:
            matched_key = "bleeding"
        elif "burn" in q_lower or "fire" in q_lower:
            matched_key = "burns"
        elif "fracture" in q_lower or "bone" in q_lower or "broken" in q_lower or "splint" in q_lower:
            matched_key = "fractures"
        elif "shock" in q_lower or "dizzy" in q_lower or "pale" in q_lower:
            matched_key = "shock"

        if matched_key:
            return {
                "found": True,
                "category": matched_key,
                **cls.GUIDES[matched_key]
            }

        # Default fallback guide
        return {
            "found": False,
            "title": "General First Aid Protocol",
            "steps": [
                "1. Ensure the scene is safe for you and the victim.",
                "2. Call local emergency responders immediately.",
                "3. Keep the victim calm, warm, and static.",
                "4. Check responsiveness, breathing, and pulses.",
                "5. Describe symptoms clearly to the emergency operator."
            ],
            "warnings": ["Do not move the victim unless they are in immediate danger.", "Do not administer medications."]
        }

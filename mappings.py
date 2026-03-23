# mappings.py - Complete IPC to BNS Mapping with Unbundling Logic
# Categorized by Primary (General) and Related (Specific/Aggravated)

LAW_MAP = {
    # FORMAT: "IPC_SECTION": [{"bns": "XX", "type": "Primary/Related", "subject": "Title", "summary": "Desc"}]

    # --- RAPE & SEXUAL OFFENCES ---
    "375": [{"bns": "63", "type": "Primary", "subject": "Rape Definition", "summary": "Age of consent for exception raised from 15 to 18 years."}],
    "376": [
        {"bns": "64", "type": "Primary", "subject": "Punishment for Rape", "summary": "General punishment for rape (Standard case)."},
        {"bns": "66", "type": "Related", "subject": "Aggravated (Death/Vegetative State)", "summary": "Punishment for causing death or persistent vegetative state of victim."},
        {"bns": "70(1)", "type": "Related", "subject": "Gang Rape", "summary": "General punishment for gang rape."},
        {"bns": "71", "type": "Related", "subject": "Repeat Offender", "summary": "Enhanced punishment for repeat rape offenders."}
    ],
    "376AB": [{"bns": "65(2)", "type": "Primary", "subject": "Rape on child under 12", "summary": "Specific punishment for rape of a woman under 12 years."}],
    
    # --- MURDER & HOMICIDE ---
    "300": [{"bns": "101", "type": "Primary", "subject": "Murder Definition", "summary": "Definition of murder; numbered clauses (a)-(d) replace old structure."}],
    "302": [
        {"bns": "103(1)", "type": "Primary", "subject": "Punishment for Murder", "summary": "General punishment for murder."},
        {"bns": "103(2)", "type": "Related", "subject": "Mob Lynching", "summary": "Murder by group of 5+ on grounds of race, caste, community, etc."}
    ],
    "304A": [
        {"bns": "106(1)", "type": "Primary", "subject": "Death by Negligence", "summary": "General negligence; imprisonment increased."},
        {"bns": "106(2)", "type": "Related", "subject": "Hit and Run", "summary": "New addition for escaping scene (Currently on hold by Govt)."}
    ],

    # --- CRUELTY & MARRIAGE ---
    "498A": [
        {"bns": "85", "type": "Primary", "subject": "Cruelty by Husband/Relative", "summary": "Punishment for subjecting a woman to cruelty."},
        {"bns": "86", "type": "Related", "subject": "Cruelty Defined", "summary": "Specific legal definition of 'Cruelty' now separated into its own section."}
    ],

    # --- HURT & GRIEVOUS HURT ---
    "319": [{"bns": "114", "type": "Primary", "subject": "Hurt Definition", "summary": "No change to core definition."}],
    "320": [{"bns": "116", "type": "Primary", "subject": "Grievous Hurt Definition", "summary": "Suffering threshold reduced from 20 days to 15 days."}],
    "325": [{"bns": "117(2)", "type": "Primary", "subject": "Punishment for Grievous Hurt", "summary": "General punishment for voluntarily causing grievous hurt."}],
    "New_Mob_Hurt": [
        {"bns": "117(4)", "type": "Related", "subject": "Mob Grievous Hurt", "summary": "Grievous hurt by group of 5+ on grounds of race, caste, community, etc."}
    ],

    # --- DEFINITIONS & GENERAL ---
    "10": [
        {"bns": "2(19)", "type": "Primary", "subject": "Man", "summary": "Bifurcated definition for 'Man'."},
        {"bns": "2(35)", "type": "Primary", "subject": "Woman", "summary": "Bifurcated definition for 'Woman'."}
    ],
    "33": [
        {"bns": "2(1)", "type": "Primary", "subject": "Act", "summary": "Now defined separately from omission."},
        {"bns": "2(25)", "type": "Primary", "subject": "Omission", "summary": "Now defined separately from act."}
    ],
    "34": [{"bns": "3(5)", "type": "Primary", "subject": "Common Intention", "summary": "Moved to General Explanations; essence unchanged."}],
    "124A": [{"bns": "152", "type": "Primary", "subject": "Sedition (Replacement)", "summary": "Acts endangering sovereignty/unity. Word 'Sedition' removed."}],
    "420": [{"bns": "318", "type": "Primary", "subject": "Cheating", "summary": "Punishment for cheating and inducing delivery of property."}],
    "511": [{"bns": "62", "type": "Primary", "subject": "Attempt", "summary": "General provision for attempting offences."}]
}

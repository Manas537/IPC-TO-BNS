# mappings.py - Definitive IPC to BNS Mapping
# Optimized for "Unbundled" Legal AI Logic

LAW_MAP = {
    # --- CHAPTER I & II: PRELIMINARY & DEFINITIONS ---
    "1": [
        {"bns": "1(1)", "type": "Primary", "subject": "Short title & Application", "summary": "BNS covers the operation of the code in 6 subsections; IPC had 5 separate sections."},
        {"bns": "1(2)", "type": "Related", "subject": "Commencement", "summary": "Power to appoint date delegated to Central Govt (Absent in IPC)."}
    ],
    "8": [{"bns": "2(10)", "type": "Primary", "subject": "Gender", "summary": "Word 'transgender' added alongside male and female."}],
    "10": [
        {"bns": "2(19)", "type": "Primary", "subject": "Definition of 'Man'", "summary": "Bifurcated from IPC 10. Standalone definition for male human of any age."},
        {"bns": "2(35)", "type": "Primary", "subject": "Definition of 'Woman'", "summary": "Bifurcated from IPC 10. Standalone definition for female human of any age."}
    ],
    "19": [{"bns": "2(16)", "type": "Primary", "subject": "Judge", "summary": "Simplified definition; only 1 out of 4 original illustrations retained."}],
    "21": [{"bns": "2(28)", "type": "Primary", "subject": "Public Servant", "summary": "'Military/Naval' updated to 'Army/Navy'; 'Juryman' excluded."}],
    "22": [{"bns": "2(21)", "type": "Primary", "subject": "Movable Property", "summary": "Scope expanded by removing the word 'corporeal'."}],
    "29": [{"bns": "2(8)", "type": "Primary", "subject": "Document", "summary": "Consolidates IPC 29 and 29A; explicitly includes electronic/digital records."}],
    "33": [
        {"bns": "2(1)", "type": "Primary", "subject": "Act", "summary": "Bifurcated. 'Act' is now defined separately from 'Omission'."},
        {"bns": "2(25)", "type": "Primary", "subject": "Omission", "summary": "Bifurcated. 'Omission' is now defined separately from 'Act'."}
    ],
    "40": [{"bns": "2(24)", "type": "Primary", "subject": "Offence", "summary": "Definition clarified; 'denotes' replaced with 'means'."}],

    # --- CHAPTER III: PUNISHMENTS ---
    "53": [
        {"bns": "4", "type": "Primary", "subject": "Punishments", "summary": "New punishment added: 'Community Service' (Defined in BNSS Sec 23)."}
    ],
    "73": [{"bns": "11", "type": "Primary", "subject": "Solitary Confinement", "summary": "Phrasing updated for clarity ('namely' replaces 'that is to say')."}],

    # --- CHAPTER VI: OFFENCES AGAINST WOMEN & CHILDREN ---
    "375": [{"bns": "63", "type": "Primary", "subject": "Rape Definition", "summary": "Age of consent for exception raised from 15 to 18 years."}],
    "376": [
        {"bns": "64", "type": "Primary", "subject": "Punishment for Rape", "summary": "General punishment for rape."},
        {"bns": "66", "type": "Related", "subject": "Death/Vegetative State", "summary": "Specific punishment for rape causing death or persistent vegetative state."},
        {"bns": "70(1)", "type": "Related", "subject": "Gang Rape", "summary": "General gang rape punishment."},
        {"bns": "71", "type": "Related", "subject": "Repeat Offender", "summary": "Enhanced punishment for repeat rape offenders."}
    ],
    "498A": [
        {"bns": "85", "type": "Primary", "subject": "Cruelty by Husband/Relative", "summary": "Retains core punitive framework of IPC 498A."},
        {"bns": "86", "type": "Related", "subject": "Cruelty Defined", "summary": "The definition of 'Cruelty' is now a standalone section for legal clarity."}
    ],

    # --- CHAPTER XVI: OFFENCES AGAINST THE HUMAN BODY ---
    "300": [{"bns": "101", "type": "Primary", "subject": "Murder Definition", "summary": "Structural re-formatting of clauses (a) to (d)."}],
    "302": [
        {"bns": "103(1)", "type": "Primary", "subject": "Punishment for Murder", "summary": "General punishment for murder."},
        {"bns": "103(2)", "type": "Related", "subject": "Mob Lynching", "summary": "Murder by group of 5+ based on race, caste, community, or similar grounds."}
    ],
    "304A": [
        {"bns": "106(1)", "type": "Primary", "subject": "Death by Negligence", "summary": "Imprisonment increased from 2 to 5 years (General negligence)."},
        {"bns": "106(2)", "type": "Related", "subject": "Hit and Run", "summary": "Enhanced punishment for escaping scene (Implementation currently stayed)."}
    ],
    "307": [{"bns": "109", "type": "Primary", "subject": "Attempt to Murder", "summary": "Adds death penalty/natural life imprisonment for life-convicts who attempt murder."}],
    "320": [{"bns": "116", "type": "Primary", "subject": "Grievous Hurt", "summary": "Suffering threshold reduced from 20 days to 15 days."}],
    "326A": [{"bns": "124(1)", "type": "Primary", "subject": "Acid Attack", "summary": "Adds 'permanent vegetative state' to the criteria for grievous hurt by acid."}],

    # --- OTHER CRITICAL SECTIONS ---
    "124A": [{"bns": "152", "type": "Primary", "subject": "Sovereignty/Unity of India", "summary": "Replaces Sedition. Focuses on acts endangering unity and integrity of India."}],
    "420": [{"bns": "318", "type": "Primary", "subject": "Cheating", "summary": "Replaces the classic cheating and dishonestly inducing delivery of property."},],
    "511": [{"bns": "62", "type": "Primary", "subject": "Attempt", "summary": "General section for attempt to commit life-imprisonment offences."}]
}

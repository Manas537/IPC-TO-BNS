# mappings.py - Definitive IPC to BNS Mapping
# Optimized for "Unbundled" Legal AI Logic with Special Context & Mirror Support

LAW_MAP = {
    # --- CHAPTER I & II: PRELIMINARY & DEFINITIONS ---
    "1": [
        {
            "bns": "1(1)", 
            "type": "Primary", 
            "subject": "Short title & Application", 
            "summary": "BNS covers the operation of the code in 6 subsections; IPC had 5 separate sections.",
            "special_note": "Consolidates the entire territorial scope of the code into a single entry point."
        },
        {
            "bns": "1(2)", 
            "type": "Related", 
            "subject": "Commencement", 
            "summary": "Power to appoint date delegated to Central Govt (Absent in IPC).",
            "special_note": "This allows the government to notify the implementation date via the Official Gazette."
        }
    ],
    "8": [
        {
            "bns": "2(10)", 
            "type": "Primary", 
            "subject": "Gender", 
            "summary": "Word 'transgender' added alongside male and female.",
            "special_note": "A landmark step for inclusivity, explicitly recognizing third-gender individuals in criminal law."
        }
    ],
    "10": [
        {
            "bns": "2(19)", 
            "type": "Primary", 
            "subject": "Definition of 'Man'", 
            "summary": "Bifurcated from IPC 10. Now a standalone definition for a male human of any age."
        },
        {
            "bns": "2(35)", 
            "type": "Primary", 
            "subject": "Definition of 'Woman'", 
            "summary": "Bifurcated from IPC 10. Now a standalone definition for a female human of any age."
        }
    ],
    "19": [{"bns": "2(16)", "type": "Primary", "subject": "Judge", "summary": "Simplified definition; only 1 out of 4 original illustrations retained."}],
    "21": [{"bns": "2(28)", "type": "Primary", "subject": "Public Servant", "summary": "'Military/Naval' updated to 'Army/Navy'; 'Juryman' excluded."}],
    "22": [{"bns": "2(21)", "type": "Primary", "subject": "Movable Property", "summary": "Scope expanded by removing the word 'corporeal', now potentially covering digital assets."}],
    "29": [
        {
            "bns": "2(8)", 
            "type": "Primary", 
            "subject": "Document", 
            "summary": "Consolidates IPC 29 and 29A; explicitly includes electronic/digital records.",
            "special_note": "Modernizes evidence standards by giving digital records the same legal standing as paper."
        }
    ],
    "33": [
        {"bns": "2(1)", "type": "Primary", "subject": "Act", "summary": "Bifurcated. 'Act' is now defined separately from 'Omission'."},
        {"bns": "2(25)", "type": "Primary", "subject": "Omission", "summary": "Bifurcated. 'Omission' is now defined separately from 'Act'."}
    ],
    "40": [{"bns": "2(24)", "type": "Primary", "subject": "Offence", "summary": "Definition clarified; 'denotes' replaced with 'means'."}],

    # --- CHAPTER III: PUNISHMENTS ---
    "53": [
        {
            "bns": "4", 
            "type": "Primary", 
            "subject": "Punishments", 
            "summary": "New punishment added: 'Community Service' (Defined in BNSS Sec 23).",
            "special_note": "First-time introduction of restorative justice in Indian criminal law for petty offences."
        }
    ],
    "73": [{"bns": "11", "type": "Primary", "subject": "Solitary Confinement", "summary": "Phrasing updated for clarity ('namely' replaces 'that is to say')."}],

    # --- CHAPTER VI: OFFENCES AGAINST WOMEN & CHILDREN ---
    "354": [
        {
            "bns": "74", 
            "type": "Mirror", 
            "subject": "Assault to Outrage Modesty", 
            "summary": "Assault or criminal force to a woman with intent to outrage her modesty.",
            "special_note": "A direct carry-over of the core protection for women's dignity."
        }
    ],
    "354C": [{"bns": "77", "type": "Mirror", "subject": "Voyeurism", "summary": "Watching or capturing images of a woman in a private act."}],
    "354D": [{"bns": "78", "type": "Mirror", "subject": "Stalking", "summary": "Following or monitoring a woman repeatedly despite disinterest."}],
    "375": [{"bns": "63", "type": "Primary", "subject": "Rape Definition", "summary": "Age of consent for exception raised from 15 to 18 years."}],
    "376": [
        {"bns": "64", "type": "Primary", "subject": "Punishment for Rape", "summary": "General punishment for rape.", "special_note": "The BNS prioritizes these crimes by placing them at the start of the code in Chapter V."},
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
        {
            "bns": "103(2)", 
            "type": "Related", 
            "subject": "Mob Lynching", 
            "summary": "Murder by group of 5+ based on race, caste, community, or similar grounds.",
            "special_note": "For the first time, Mob Lynching is codified as a distinct aggravated offence."
        }
    ],
    "304A": [
        {"bns": "106(1)", "type": "Primary", "subject": "Death by Negligence", "summary": "Imprisonment increased from 2 to 5 years (General negligence)."},
        {
            "bns": "106(2)", 
            "type": "Related", 
            "subject": "Hit and Run", 
            "summary": "Enhanced punishment for escaping scene.",
            "special_note": "Subject of major protests; raises jail time to 10 years for drivers who flee without reporting."
        }
    ],
    "307": [{"bns": "109", "type": "Primary", "subject": "Attempt to Murder", "summary": "Adds death penalty/natural life imprisonment for life-convicts who attempt murder."}],
    "320": [{"bns": "116", "type": "Primary", "subject": "Grievous Hurt", "summary": "Suffering threshold reduced from 20 days to 15 days."}],

    # --- PUBLIC TRANQUILLITY ---
    "141": [{"bns": "189", "type": "Mirror", "subject": "Unlawful Assembly", "summary": "Definition remains the same (Assembly of 5+ with common illegal object)."}],
    "159": [{"bns": "194", "type": "Mirror", "subject": "Affray", "summary": "Fighting in public disturbing peace."}],

    # --- PROPERTY & TRUST ---
    "378": [{"bns": "303(1)", "type": "Primary", "subject": "Theft", "summary": "General theft provision.", "special_note": "BNS 304 now creates a specific category for 'Snatching' distinct from theft."}],
    "405": [{"bns": "316(1)", "type": "Mirror", "subject": "Criminal Breach of Trust", "summary": "Dishonest misappropriation of property entrusted to a person."}],
    "415": [{"bns": "318(1)", "type": "Mirror", "subject": "Cheating Definition", "summary": "Foundational definition of cheating remains consistent with IPC."}],
    "420": [
        {
            "bns": "318(4)", 
            "type": "Primary", 
            "subject": "Cheating & Inducing Delivery", 
            "summary": "Replaces the classic fraud section.",
            "special_note": "The legendary 'Section 420' has been retired and relocated to 318(4). End of an era for legal slang!"
        }
    ],

    # --- OTHER CRITICAL SECTIONS ---
    "124A": [
        {
            "bns": "152", 
            "type": "Primary", 
            "subject": "Sovereignty/Unity of India", 
            "summary": "Replaces Sedition. Focuses on acts endangering unity and integrity of India.",
            "special_note": "The word 'Sedition' is officially gone. Focus is now on national integrity rather than disaffection against the Government."
        }
    ],
    "499": [
        {
            "bns": "356", 
            "type": "Primary", 
            "subject": "Defamation", 
            "summary": "Criminal defamation remains, but adds community service options.",
            "special_note": "Modernizes the penalty by allowing restorative work instead of jail time."
        }
    ],
    "511": [{"bns": "62", "type": "Primary", "subject": "Attempt", "summary": "General section for attempt to commit life-imprisonment offences."}]
}

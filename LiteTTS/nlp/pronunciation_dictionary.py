#!/usr/bin/env python3
"""
Comprehensive pronunciation dictionary for Kokoro TTS system
Contains common mispronounced words and their correct pronunciations
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class PronunciationDictionary:
    """Comprehensive pronunciation dictionary for TTS accuracy"""
    
    def __init__(self):
        self.common_mispronunciations = self._load_common_mispronunciations()
        self.technical_terms = self._load_technical_terms()
        self.proper_nouns = self._load_proper_nouns()
        self.foreign_words = self._load_foreign_words()
        
    def _load_common_mispronunciations(self) -> Dict[str, str]:
        """Load commonly mispronounced words with correct pronunciations"""
        return {
            # Words identified in the audit - removed hedonism and inherently for natural pronunciation
            # 'asterisk': 'AS-ter-isk',  # Let natural pronunciation handle this too
            
            # Additional commonly mispronounced words
            'often': 'OF-en',  # Not "OF-ten"
            'comfortable': 'KUMF-ter-bul',  # Not "com-FOR-table"
            'nuclear': 'NEW klee er',  # Not "NEW-kyuh-ler"
            'library': 'LY brer ee',  # Not "LY-berry"
            'february': 'FEB roo er ee',  # Not "FEB-yoo-ary"
            'wednesday': 'WENZ-day',  # Not "WED-nes-day"
            'colonel': 'KER-nel',  # Not "ko-lo-NEL"
            'salmon': 'SAM-un',  # Silent 'l'
            'almond': 'AH-mund',  # Silent 'l'
            'palm': 'PAHM',  # Silent 'l'
            'calm': 'KAHM',  # Silent 'l'
            'half': 'HAF',  # Silent 'l'
            'walk': 'WAWK',  # Silent 'l'
            'talk': 'TAWK',  # Silent 'l'
            'chalk': 'CHAWK',  # Silent 'l'
            'folk': 'FOHK',  # Silent 'l'
            'yolk': 'YOHK',  # Silent 'l'
            'debt': 'DET',  # Silent 'b'
            'doubt': 'DOWT',  # Silent 'b'
            'lamb': 'LAM',  # Silent 'b'
            'thumb': 'THUM',  # Silent 'b'
            'comb': 'KOHM',  # Silent 'b'
            'tomb': 'TOOM',  # Silent 'b'
            'womb': 'WOOM',  # Silent 'b'
            'knee': 'NEE',  # Silent 'k'
            'knife': 'NYF',  # Silent 'k'
            'knight': 'NYT',  # Silent 'k'
            'know': 'NOH',  # Silent 'k'
            'knowledge': 'NOL-ij',  # Silent 'k'
            'gnome': 'NOHM',  # Silent 'g'
            'gnat': 'NAT',  # Silent 'g'
            'sign': 'SYN',  # Silent 'g'
            'design': 'di-ZYN',  # Silent 'g'
            'resign': 'ri-ZYN',  # Silent 'g'
            'foreign': 'FOR-in',  # Silent 'g'
            'campaign': 'kam-PAYN',  # Silent 'g'
            'champagne': 'sham-PAYN',  # Silent 'g'
            'island': 'EYE-land',  # Silent 's'
            'aisle': 'EYL',  # Silent 's'
            'castle': 'KAS-ul',  # Silent 't'
            'listen': 'LIS-en',  # Silent 't'
            'fasten': 'FAS-en',  # Silent 't'
            'christmas': 'KRIS-mas',  # Silent 't'
            'mortgage': 'MOR-gij',  # Silent 't'
            'answer': 'AN-ser',  # Silent 'w'
            'sword': 'SORD',  # Silent 'w'
            'two': 'TOO',  # Silent 'w'
            'write': 'RYT',  # Silent 'w'
            'wrong': 'RONG',  # Silent 'w'
            'wrist': 'RIST',  # Silent 'w'
            'wrap': 'RAP',  # Silent 'w'
            'wreck': 'REK',  # Silent 'w'
            'honest': 'ON-ist',  # Silent 'h'
            'hour': 'OW-er',  # Silent 'h'
            'honor': 'ON-er',  # Silent 'h'
            'heir': 'AIR',  # Silent 'h'
            'vehicle': 'VEE-ih-kul',  # Not "VEE-hik-ul"
            'mischievous': 'MIS-chuh-vus',  # Not "mis-CHEE-vee-us"
            'pronunciation': 'pro-NUN-see-AY-shun',  # Not "pro-NOWN-see-ay-shun"
            'espresso': 'es-PRES-oh',  # Not "ex-PRES-oh"
            'supposedly': 'suh-POHZ-id-lee',  # Not "suh-POHZ-ab-lee"
            'escape': 'es-KAYP',  # Not "ex-KAYP"
            'especially': 'es-PESH-uh-lee',  # Not "ex-PESH-uh-lee"
            'et cetera': 'et-SET-er-uh',  # Not "ek-SET-er-uh"
            'arctic': 'ARK-tik',  # Not "AR-tik"
            'antarctic': 'ant-ARK-tik',  # Not "ant-AR-tik"
            'athlete': 'ATH-leet',  # Not "ATH-uh-leet"
            'athletics': 'ath-LET-iks',  # Not "ath-uh-LET-iks"
            'jewelry': 'JOO-ul-ree',  # Not "JOO-luh-ree"
            'miniature': 'MIN-ee-uh-chur',  # Not "MIN-uh-chur"
            'temperature': 'TEM-per-uh-chur',  # Not "TEM-pruh-chur"
            'literature': 'LIT-er-uh-chur',  # Not "LIT-ruh-chur"
            'picture': 'PIK-chur',  # Not "PIK-shur"
            'nature': 'NAY-chur',  # Not "NAY-shur"
            'mature': 'muh-CHUR',  # Not "muh-SHUR"
            'future': 'FYOO-chur',  # Not "FYOO-shur"
            'culture': 'KUL-chur',  # Not "KUL-shur"
            'adventure': 'ad-VEN-chur',  # Not "ad-VEN-shur"
            'furniture': 'FUR-ni-chur',  # Not "FUR-ni-shur"
            'legislature': 'LEJ-is-lay-chur',  # Not "LEJ-is-lay-shur"
        }
    
    def _load_technical_terms(self) -> Dict[str, str]:
        """Load technical terms and their pronunciations"""
        return {
            # Computer science terms
            'algorithm': 'AL guh rith um',
            'algorithms': 'AL guh rith ums',
            'boolean': 'BOO-lee-un',
            'cache': 'KASH',
            'daemon': 'DEE-mun',
            'facade': 'fuh-SAHD',
            'gui': 'GOO-ee',
            'jpeg': 'JAY-peg',
            'linux': 'LIN-uks',
            'mysql': 'MY-es-kyoo-el',
            'nginx': 'EN-jin-eks',
            'oauth': 'OH-auth',
            'postgresql': 'POST-gres-kyoo-el',
            'queue': 'KYOO',
            'regex': 'REJ-eks',
            'sql': 'es-kyoo-el',
            'ubuntu': 'oo-BOON-too',
            'wifi': 'WY-fy',
            'xml': 'eks-em-el',
            'yaml': 'YAM-ul',
            
            # Scientific terms
            'genome': 'JEE-nohm',
            'enzyme': 'EN-zym',
            'isotope': 'EYE-suh-tohp',
            'molecule': 'MOL-uh-kyool',
            'photosynthesis': 'foh-toh-SIN-thuh-sis',
            'chromosome': 'KROH-muh-sohm',
            'mitochondria': 'my-tuh-KON-dree-uh',
            'deoxyribonucleic': 'dee-ok-see-ry-boh-noo-KLEE-ik',
            
            # Medical terms
            'alzheimer': 'ALTS-hy-mer',
            'diabetes': 'dy-uh-BEE-teez',
            'pneumonia': 'noo-MOHN-yuh',
            'antibiotic': 'an-ty-by-OT-ik',
            'anesthesia': 'an-us-THEE-zhuh',
            'diagnosis': 'dy-ug-NOH-sis',
            'prognosis': 'prog-NOH-sis',
            'stethoscope': 'STETH-uh-skohp',
            
            # Mathematical terms
            'coefficient': 'koh-uh-FISH-unt',
            'derivative': 'duh-RIV-uh-tiv',
            'exponential': 'ek-spoh-NEN-shul',
            'fibonacci': 'fee-buh-NAH-chee',
            'geometric': 'jee-uh-MET-rik',
            'hyperbola': 'hy-PUR-buh-luh',
            'integral': 'IN-ti-grul',
            'logarithm': 'LOG-uh-rith-um',
            'polynomial': 'pol-ee-NOH-mee-ul',
            'trigonometry': 'trig-uh-NOM-uh-tree',

            # Business and finance terms
            'entrepreneur': 'ahn-truh-pruh-NUR',
            'entrepreneurial': 'ahn-truh-pruh-NUR-ee-ul',
            'acquisition': 'ak-wih-ZIH-shuhn',  # Fixed pronunciation - not "equisition"
            'merger': 'MUR-jur',
            'revenue': 'REV-uh-noo',
            'quarterly': 'KWAR-tur-lee',

            # Real estate (compound words - no pause)
            'real estate': 'real estate',  # Ensure no pause between words
            'realtor': 'REEL-tur',
            'mortgage': 'MOR-gij',
        }
    
    def _load_proper_nouns(self) -> Dict[str, str]:
        """Load proper nouns and their pronunciations"""
        return {
            # Geographic locations
            'worcestershire': 'WUS-ter-shur',
            'leicester': 'LES-ter',
            'gloucester': 'GLOS-ter',
            'edinburgh': 'ED-in-bur-uh',
            'arkansas': 'AR-kun-saw',
            'illinois': 'il-uh-NOY',
            'nevada': 'nuh-VAD-uh',
            'oregon': 'OR-uh-gun',
            'missouri': 'muh-ZUR-ee',
            'louisiana': 'loo-ee-zee-AN-uh',
            'massachusetts': 'mas-uh-CHOO-sits',
            'connecticut': 'kuh-NET-ih-kut',
            
            # Brand names
            'nike': 'NY-kee',
            'adidas': 'uh-DEE-dus',
            'hyundai': 'HUN-day',
            'volkswagen': 'FOHKS-vah-gun',
            'porsche': 'POR-shuh',
            'lamborghini': 'lam-bor-GEE-nee',
            'maserati': 'mas-uh-RAH-tee',
            'ferrari': 'fuh-RAR-ee',
            'jaguar': 'JAG-wahr',

            # Stock symbols and financial terms
            'tsla': 'TESS-lah',  # Tesla stock symbol
            'aapl': 'apple',     # Apple stock symbol
            'msft': 'microsoft', # Microsoft stock symbol
            'googl': 'google',   # Google stock symbol
            'amzn': 'amazon',    # Amazon stock symbol
            'nvda': 'en-VID-ee-ah',  # NVIDIA stock symbol
            'meta': 'META',      # Meta stock symbol
            'nflx': 'netflix',   # Netflix stock symbol

            # People names (proper pronunciation)
            'elon': 'EE-lahn',   # Elon Musk - not "alon"
            
            # Names
            'joaquin': 'wah-KEEN',
            'siobhan': 'shuh-VAWN',
            'niamh': 'NEEV',
            'caoimhe': 'KEE-vuh',
            'saoirse': 'SUR-shuh',
            'xavier': 'ZAY-vee-er',
            'yves': 'EEV',
            'jacques': 'ZHAHK',
            'guillaume': 'gee-YOHM',
        }
    
    def _load_foreign_words(self) -> Dict[str, str]:
        """Load foreign words commonly used in English"""
        return {
            # French
            'bourgeois': 'boor-ZHWAH',
            'entrepreneur': 'ahn-truh-pruh-NUR',
            'renaissance': 'REN-uh-sahns',
            'croissant': 'kruh-SAHNT',
            'ballet': 'ba-LAY',
            'cafe': 'ka-FAY',
            'cliche': 'klee-SHAY',
            'debris': 'duh-BREE',
            'genre': 'ZHAHN-ruh',
            'liaison': 'LEE-uh-zahn',
            'naive': 'ny-EEV',
            'premiere': 'pruh-MEER',
            'resume': 'REZ-oo-may',
            'sabotage': 'SAB-uh-tahzh',
            'valet': 'va-LAY',
            
            # German
            'schadenfreude': 'SHAH-den-froy-duh',
            'zeitgeist': 'TSYT-gyst',
            'kindergarten': 'KIN-der-gar-ten',
            'gesundheit': 'guh-ZOONT-hyt',
            'wanderlust': 'WAN-der-lust',
            
            # Italian
            'cappuccino': 'kap-oo-CHEE-noh',
            'paparazzi': 'pap-uh-RAT-see',
            'graffiti': 'gruh-FEE-tee',
            'spaghetti': 'spuh-GET-ee',
            'bruschetta': 'broo-SKET-uh',
            'gnocchi': 'NYOH-kee',
            'chianti': 'kee-AHN-tee',
            
            # Spanish
            'jalapeno': 'hah-luh-PEH-nyoh',
            'quinoa': 'KEEN-wah',
            'chorizo': 'chuh-REE-soh',
            'tortilla': 'tor-TEE-yah',
            'quesadilla': 'kay-suh-DEE-yah',
            
            # Japanese
            'karaoke': 'kar-ee-OH-kee',
            'tsunami': 'tsoo-NAH-mee',
            'origami': 'or-ih-GAH-mee',
            'wasabi': 'wah-SAH-bee',
            'sushi': 'SOO-shee',
            'sake': 'SAH-kay',
            'karate': 'kuh-RAH-tay',
            'anime': 'AN-ih-may',
            'manga': 'MAHN-gah',
            
            # Other languages
            'schadenfreude': 'SHAH-den-froy-duh',  # German
            'fjord': 'fee-YORD',  # Norwegian
            'sauna': 'SOW-nah',  # Finnish
            'yoga': 'YOH-gah',  # Sanskrit
            'karma': 'KAR-mah',  # Sanskrit
            'nirvana': 'nir-VAH-nah',  # Sanskrit

            # Common filler words and conversational markers
            'ok': 'oh-KAY',  # Clear pronunciation
            'okay': 'oh-KAY',  # Clear pronunciation
            'let\'s see': 'lets SEE',  # Natural pronunciation
            'lets see': 'lets SEE',  # Alternative without apostrophe
            'um': 'uhm',  # Natural filler
            'uh': 'uh',  # Natural filler
            'er': 'er',  # Natural filler
            'ah': 'ah',  # Natural filler
            'hmm': 'hmm',  # Natural thinking sound
            'well': 'wel',  # Natural conversation starter
        }
    
    def get_pronunciation(self, word: str) -> str:
        """Get the correct pronunciation for a word if available"""
        word_lower = word.lower()
        
        # Check all dictionaries
        for dictionary in [self.common_mispronunciations, self.technical_terms, 
                          self.proper_nouns, self.foreign_words]:
            if word_lower in dictionary:
                return dictionary[word_lower]
        
        return word  # Return original if no pronunciation found
    
    def has_pronunciation(self, word: str) -> bool:
        """Check if a pronunciation is available for a word"""
        word_lower = word.lower()
        
        for dictionary in [self.common_mispronunciations, self.technical_terms, 
                          self.proper_nouns, self.foreign_words]:
            if word_lower in dictionary:
                return True
        
        return False
    
    def get_all_words(self) -> List[str]:
        """Get all words that have pronunciation entries"""
        all_words = []
        for dictionary in [self.common_mispronunciations, self.technical_terms, 
                          self.proper_nouns, self.foreign_words]:
            all_words.extend(dictionary.keys())
        return sorted(list(set(all_words)))
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the pronunciation dictionary"""
        return {
            'common_mispronunciations': len(self.common_mispronunciations),
            'technical_terms': len(self.technical_terms),
            'proper_nouns': len(self.proper_nouns),
            'foreign_words': len(self.foreign_words),
            'total_words': len(self.get_all_words())
        }

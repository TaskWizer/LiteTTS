#!/usr/bin/env python3
"""
Enhanced Units and Measurements Processor for Phase 6: Advanced Text Processing
Handles temperature units, energy units, flight designations, and other specialized units
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class UnitsProcessingResult:
    """Result of units processing"""
    processed_text: str
    original_text: str
    changes_made: List[str]
    units_processed: int

class EnhancedUnitsProcessor:
    """Enhanced processor for units and measurements"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize enhanced units processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.unit_patterns = self._compile_unit_patterns()
        self.unit_expansions = self._load_unit_expansions()
        
        logger.info("Enhanced Units Processor initialized")
    
    def _compile_unit_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for unit processing"""
        return {
            # Temperature units
            'temperature_f': re.compile(r'\b(\d+(?:\.\d+)?)\s*°F\b', re.IGNORECASE),
            'temperature_c': re.compile(r'\b(\d+(?:\.\d+)?)\s*°C\b', re.IGNORECASE),
            'temperature_k': re.compile(r'\b(\d+(?:\.\d+)?)\s*°K\b', re.IGNORECASE),
            'temperature_degree': re.compile(r'\b(\d+(?:\.\d+)?)\s*degrees?\s*(fahrenheit|celsius|kelvin)\b', re.IGNORECASE),
            
            # Energy units
            'kilowatt_hours': re.compile(r'\b(\d+(?:\.\d+)?)\s*kWh\b'),
            'megawatt_hours': re.compile(r'\b(\d+(?:\.\d+)?)\s*MWh\b'),
            'watt_hours': re.compile(r'\b(\d+(?:\.\d+)?)\s*Wh\b'),
            'kilowatts': re.compile(r'\b(\d+(?:\.\d+)?)\s*kW\b'),
            'megawatts': re.compile(r'\b(\d+(?:\.\d+)?)\s*MW\b'),
            'watts': re.compile(r'\b(\d+(?:\.\d+)?)\s*W\b'),
            
            # Flight and transportation
            'flight_number': re.compile(r'\bflight\s*no\.?\s*(\d+)\b', re.IGNORECASE),
            'gate_number': re.compile(r'\bgate\s*no\.?\s*(\w+)\b', re.IGNORECASE),
            'terminal_number': re.compile(r'\bterminal\s*no\.?\s*(\w+)\b', re.IGNORECASE),
            
            # Distance and measurement
            'miles_per_hour': re.compile(r'\b(\d+(?:\.\d+)?)\s*mph\b', re.IGNORECASE),
            'kilometers_per_hour': re.compile(r'\b(\d+(?:\.\d+)?)\s*km/h\b', re.IGNORECASE),
            'feet_per_second': re.compile(r'\b(\d+(?:\.\d+)?)\s*ft/s\b', re.IGNORECASE),
            'meters_per_second': re.compile(r'\b(\d+(?:\.\d+)?)\s*m/s\b', re.IGNORECASE),
            
            # Weight and mass
            'pounds': re.compile(r'\b(\d+(?:\.\d+)?)\s*lbs?\b', re.IGNORECASE),
            'kilograms': re.compile(r'\b(\d+(?:\.\d+)?)\s*kg\b'),
            'grams': re.compile(r'\b(\d+(?:\.\d+)?)\s*g\b'),
            'ounces': re.compile(r'\b(\d+(?:\.\d+)?)\s*oz\b', re.IGNORECASE),
            
            # Volume
            'liters': re.compile(r'\b(\d+(?:\.\d+)?)\s*L\b'),
            'milliliters': re.compile(r'\b(\d+(?:\.\d+)?)\s*mL\b'),
            'gallons': re.compile(r'\b(\d+(?:\.\d+)?)\s*gal\b', re.IGNORECASE),
            'fluid_ounces': re.compile(r'\b(\d+(?:\.\d+)?)\s*fl\.?\s*oz\b', re.IGNORECASE),
            
            # Length
            'feet': re.compile(r'\b(\d+(?:\.\d+)?)\s*ft\b'),
            'inches': re.compile(r'\b(\d+(?:\.\d+)?)\s*in\b'),
            'meters': re.compile(r'\b(\d+(?:\.\d+)?)\s*m\b'),
            'centimeters': re.compile(r'\b(\d+(?:\.\d+)?)\s*cm\b'),
            'millimeters': re.compile(r'\b(\d+(?:\.\d+)?)\s*mm\b'),
            'kilometers': re.compile(r'\b(\d+(?:\.\d+)?)\s*km\b'),
            'miles': re.compile(r'\b(\d+(?:\.\d+)?)\s*mi\b'),
            
            # Area
            'square_feet': re.compile(r'\b(\d+(?:\.\d+)?)\s*sq\.?\s*ft\b', re.IGNORECASE),
            'square_meters': re.compile(r'\b(\d+(?:\.\d+)?)\s*sq\.?\s*m\b', re.IGNORECASE),
            'acres': re.compile(r'\b(\d+(?:\.\d+)?)\s*acres?\b', re.IGNORECASE),
            
            # Pressure
            'psi': re.compile(r'\b(\d+(?:\.\d+)?)\s*psi\b', re.IGNORECASE),
            'pascals': re.compile(r'\b(\d+(?:\.\d+)?)\s*Pa\b'),
            'atmospheres': re.compile(r'\b(\d+(?:\.\d+)?)\s*atm\b', re.IGNORECASE),
            
            # Frequency
            'hertz': re.compile(r'\b(\d+(?:\.\d+)?)\s*Hz\b'),
            'kilohertz': re.compile(r'\b(\d+(?:\.\d+)?)\s*kHz\b'),
            'megahertz': re.compile(r'\b(\d+(?:\.\d+)?)\s*MHz\b'),
            'gigahertz': re.compile(r'\b(\d+(?:\.\d+)?)\s*GHz\b'),
            
            # Data storage
            'bytes': re.compile(r'\b(\d+(?:\.\d+)?)\s*B\b'),
            'kilobytes': re.compile(r'\b(\d+(?:\.\d+)?)\s*KB\b'),
            'megabytes': re.compile(r'\b(\d+(?:\.\d+)?)\s*MB\b'),
            'gigabytes': re.compile(r'\b(\d+(?:\.\d+)?)\s*GB\b'),
            'terabytes': re.compile(r'\b(\d+(?:\.\d+)?)\s*TB\b'),
        }
    
    def _load_unit_expansions(self) -> Dict[str, str]:
        """Load unit expansion mappings"""
        return {
            # Temperature
            '°F': 'degrees Fahrenheit',
            '°C': 'degrees Celsius', 
            '°K': 'degrees Kelvin',
            
            # Energy
            'kWh': 'kilowatt hours',
            'MWh': 'megawatt hours',
            'Wh': 'watt hours',
            'kW': 'kilowatts',
            'MW': 'megawatts',
            'W': 'watts',
            
            # Speed
            'mph': 'miles per hour',
            'km/h': 'kilometers per hour',
            'ft/s': 'feet per second',
            'm/s': 'meters per second',
            
            # Weight
            'lbs': 'pounds',
            'lb': 'pounds',
            'kg': 'kilograms',
            'g': 'grams',
            'oz': 'ounces',
            
            # Volume
            'L': 'liters',
            'mL': 'milliliters',
            'gal': 'gallons',
            'fl oz': 'fluid ounces',
            'fl. oz': 'fluid ounces',
            
            # Length
            'ft': 'feet',
            'in': 'inches',
            'm': 'meters',
            'cm': 'centimeters',
            'mm': 'millimeters',
            'km': 'kilometers',
            'mi': 'miles',
            
            # Area
            'sq ft': 'square feet',
            'sq. ft': 'square feet',
            'sq m': 'square meters',
            'sq. m': 'square meters',
            
            # Pressure
            'psi': 'pounds per square inch',
            'Pa': 'pascals',
            'atm': 'atmospheres',
            
            # Frequency
            'Hz': 'hertz',
            'kHz': 'kilohertz',
            'MHz': 'megahertz',
            'GHz': 'gigahertz',
            
            # Data storage
            'B': 'bytes',
            'KB': 'kilobytes',
            'MB': 'megabytes',
            'GB': 'gigabytes',
            'TB': 'terabytes',
        }
    
    def process_units(self, text: str) -> UnitsProcessingResult:
        """Main units processing method
        
        Args:
            text: Input text to process
            
        Returns:
            UnitsProcessingResult with processed text and metadata
        """
        logger.debug(f"Processing units in text: {text[:100]}...")
        
        original_text = text
        changes_made = []
        units_processed = 0
        
        # Process temperature units (highest priority)
        text, temp_changes = self._process_temperature_units(text)
        if temp_changes:
            changes_made.extend(temp_changes)
            units_processed += len(temp_changes)
        
        # Process energy units
        text, energy_changes = self._process_energy_units(text)
        if energy_changes:
            changes_made.extend(energy_changes)
            units_processed += len(energy_changes)
        
        # Process flight and transportation
        text, flight_changes = self._process_flight_designations(text)
        if flight_changes:
            changes_made.extend(flight_changes)
            units_processed += len(flight_changes)
        
        # Process speed units
        text, speed_changes = self._process_speed_units(text)
        if speed_changes:
            changes_made.extend(speed_changes)
            units_processed += len(speed_changes)
        
        # Process weight and mass units
        text, weight_changes = self._process_weight_units(text)
        if weight_changes:
            changes_made.extend(weight_changes)
            units_processed += len(weight_changes)
        
        # Process volume units
        text, volume_changes = self._process_volume_units(text)
        if volume_changes:
            changes_made.extend(volume_changes)
            units_processed += len(volume_changes)
        
        # Process length units
        text, length_changes = self._process_length_units(text)
        if length_changes:
            changes_made.extend(length_changes)
            units_processed += len(length_changes)
        
        # Process area units
        text, area_changes = self._process_area_units(text)
        if area_changes:
            changes_made.extend(area_changes)
            units_processed += len(area_changes)
        
        # Process pressure units
        text, pressure_changes = self._process_pressure_units(text)
        if pressure_changes:
            changes_made.extend(pressure_changes)
            units_processed += len(pressure_changes)
        
        # Process frequency units
        text, freq_changes = self._process_frequency_units(text)
        if freq_changes:
            changes_made.extend(freq_changes)
            units_processed += len(freq_changes)
        
        # Process data storage units
        text, data_changes = self._process_data_storage_units(text)
        if data_changes:
            changes_made.extend(data_changes)
            units_processed += len(data_changes)
        
        result = UnitsProcessingResult(
            processed_text=text,
            original_text=original_text,
            changes_made=changes_made,
            units_processed=units_processed
        )
        
        logger.debug(f"Units processing complete: {units_processed} units processed")
        return result

    def _process_temperature_units(self, text: str) -> Tuple[str, List[str]]:
        """Process temperature units: °F → degrees Fahrenheit"""
        changes = []

        # Process °F
        def replace_fahrenheit(match):
            number = match.group(1)
            result = f"{number} degrees Fahrenheit"
            changes.append(f"Temperature: {match.group()} → {result}")
            return result

        text = self.unit_patterns['temperature_f'].sub(replace_fahrenheit, text)

        # Process °C
        def replace_celsius(match):
            number = match.group(1)
            result = f"{number} degrees Celsius"
            changes.append(f"Temperature: {match.group()} → {result}")
            return result

        text = self.unit_patterns['temperature_c'].sub(replace_celsius, text)

        # Process °K
        def replace_kelvin(match):
            number = match.group(1)
            result = f"{number} degrees Kelvin"
            changes.append(f"Temperature: {match.group()} → {result}")
            return result

        text = self.unit_patterns['temperature_k'].sub(replace_kelvin, text)

        return text, changes

    def _process_energy_units(self, text: str) -> Tuple[str, List[str]]:
        """Process energy units: kWh → kilowatt hours"""
        changes = []

        # Process kWh
        def replace_kwh(match):
            number = match.group(1)
            result = f"{number} kilowatt hours"
            changes.append(f"Energy: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilowatt_hours'].sub(replace_kwh, text)

        # Process MWh
        def replace_mwh(match):
            number = match.group(1)
            result = f"{number} megawatt hours"
            changes.append(f"Energy: {match.group()} → {result}")
            return result

        text = self.unit_patterns['megawatt_hours'].sub(replace_mwh, text)

        # Process Wh
        def replace_wh(match):
            number = match.group(1)
            result = f"{number} watt hours"
            changes.append(f"Energy: {match.group()} → {result}")
            return result

        text = self.unit_patterns['watt_hours'].sub(replace_wh, text)

        # Process kW
        def replace_kw(match):
            number = match.group(1)
            result = f"{number} kilowatts"
            changes.append(f"Power: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilowatts'].sub(replace_kw, text)

        # Process MW
        def replace_mw(match):
            number = match.group(1)
            result = f"{number} megawatts"
            changes.append(f"Power: {match.group()} → {result}")
            return result

        text = self.unit_patterns['megawatts'].sub(replace_mw, text)

        # Process W
        def replace_w(match):
            number = match.group(1)
            result = f"{number} watts"
            changes.append(f"Power: {match.group()} → {result}")
            return result

        text = self.unit_patterns['watts'].sub(replace_w, text)

        return text, changes

    def _process_flight_designations(self, text: str) -> Tuple[str, List[str]]:
        """Process flight designations: Flight no. → Flight Number"""
        changes = []

        # Process flight numbers
        def replace_flight(match):
            number = match.group(1)
            result = f"Flight Number {number}"
            changes.append(f"Flight: {match.group()} → {result}")
            return result

        text = self.unit_patterns['flight_number'].sub(replace_flight, text)

        # Process gate numbers
        def replace_gate(match):
            number = match.group(1)
            result = f"Gate Number {number}"
            changes.append(f"Gate: {match.group()} → {result}")
            return result

        text = self.unit_patterns['gate_number'].sub(replace_gate, text)

        # Process terminal numbers
        def replace_terminal(match):
            number = match.group(1)
            result = f"Terminal Number {number}"
            changes.append(f"Terminal: {match.group()} → {result}")
            return result

        text = self.unit_patterns['terminal_number'].sub(replace_terminal, text)

        return text, changes

    def _process_speed_units(self, text: str) -> Tuple[str, List[str]]:
        """Process speed units"""
        changes = []

        # Process mph
        def replace_mph(match):
            number = match.group(1)
            result = f"{number} miles per hour"
            changes.append(f"Speed: {match.group()} → {result}")
            return result

        text = self.unit_patterns['miles_per_hour'].sub(replace_mph, text)

        # Process km/h
        def replace_kmh(match):
            number = match.group(1)
            result = f"{number} kilometers per hour"
            changes.append(f"Speed: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilometers_per_hour'].sub(replace_kmh, text)

        # Process ft/s
        def replace_fts(match):
            number = match.group(1)
            result = f"{number} feet per second"
            changes.append(f"Speed: {match.group()} → {result}")
            return result

        text = self.unit_patterns['feet_per_second'].sub(replace_fts, text)

        # Process m/s
        def replace_ms(match):
            number = match.group(1)
            result = f"{number} meters per second"
            changes.append(f"Speed: {match.group()} → {result}")
            return result

        text = self.unit_patterns['meters_per_second'].sub(replace_ms, text)

        return text, changes

    def _process_weight_units(self, text: str) -> Tuple[str, List[str]]:
        """Process weight and mass units"""
        changes = []

        # Process pounds
        def replace_pounds(match):
            number = match.group(1)
            result = f"{number} pounds"
            changes.append(f"Weight: {match.group()} → {result}")
            return result

        text = self.unit_patterns['pounds'].sub(replace_pounds, text)

        # Process kilograms
        def replace_kg(match):
            number = match.group(1)
            result = f"{number} kilograms"
            changes.append(f"Weight: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilograms'].sub(replace_kg, text)

        # Process grams
        def replace_g(match):
            number = match.group(1)
            result = f"{number} grams"
            changes.append(f"Weight: {match.group()} → {result}")
            return result

        text = self.unit_patterns['grams'].sub(replace_g, text)

        # Process ounces
        def replace_oz(match):
            number = match.group(1)
            result = f"{number} ounces"
            changes.append(f"Weight: {match.group()} → {result}")
            return result

        text = self.unit_patterns['ounces'].sub(replace_oz, text)

        return text, changes

    def _process_volume_units(self, text: str) -> Tuple[str, List[str]]:
        """Process volume units"""
        changes = []

        # Process liters
        def replace_liters(match):
            number = match.group(1)
            result = f"{number} liters"
            changes.append(f"Volume: {match.group()} → {result}")
            return result

        text = self.unit_patterns['liters'].sub(replace_liters, text)

        # Process milliliters
        def replace_ml(match):
            number = match.group(1)
            result = f"{number} milliliters"
            changes.append(f"Volume: {match.group()} → {result}")
            return result

        text = self.unit_patterns['milliliters'].sub(replace_ml, text)

        # Process gallons
        def replace_gallons(match):
            number = match.group(1)
            result = f"{number} gallons"
            changes.append(f"Volume: {match.group()} → {result}")
            return result

        text = self.unit_patterns['gallons'].sub(replace_gallons, text)

        # Process fluid ounces
        def replace_fl_oz(match):
            number = match.group(1)
            result = f"{number} fluid ounces"
            changes.append(f"Volume: {match.group()} → {result}")
            return result

        text = self.unit_patterns['fluid_ounces'].sub(replace_fl_oz, text)

        return text, changes

    def _process_length_units(self, text: str) -> Tuple[str, List[str]]:
        """Process length units"""
        changes = []

        # Process feet
        def replace_feet(match):
            number = match.group(1)
            result = f"{number} feet"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['feet'].sub(replace_feet, text)

        # Process inches
        def replace_inches(match):
            number = match.group(1)
            result = f"{number} inches"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['inches'].sub(replace_inches, text)

        # Process meters
        def replace_meters(match):
            number = match.group(1)
            result = f"{number} meters"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['meters'].sub(replace_meters, text)

        # Process centimeters
        def replace_cm(match):
            number = match.group(1)
            result = f"{number} centimeters"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['centimeters'].sub(replace_cm, text)

        # Process millimeters
        def replace_mm(match):
            number = match.group(1)
            result = f"{number} millimeters"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['millimeters'].sub(replace_mm, text)

        # Process kilometers
        def replace_km(match):
            number = match.group(1)
            result = f"{number} kilometers"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilometers'].sub(replace_km, text)

        # Process miles
        def replace_miles(match):
            number = match.group(1)
            result = f"{number} miles"
            changes.append(f"Length: {match.group()} → {result}")
            return result

        text = self.unit_patterns['miles'].sub(replace_miles, text)

        return text, changes

    def _process_area_units(self, text: str) -> Tuple[str, List[str]]:
        """Process area units"""
        changes = []

        # Process square feet
        def replace_sq_ft(match):
            number = match.group(1)
            result = f"{number} square feet"
            changes.append(f"Area: {match.group()} → {result}")
            return result

        text = self.unit_patterns['square_feet'].sub(replace_sq_ft, text)

        # Process square meters
        def replace_sq_m(match):
            number = match.group(1)
            result = f"{number} square meters"
            changes.append(f"Area: {match.group()} → {result}")
            return result

        text = self.unit_patterns['square_meters'].sub(replace_sq_m, text)

        # Process acres
        def replace_acres(match):
            number = match.group(1)
            result = f"{number} acres"
            changes.append(f"Area: {match.group()} → {result}")
            return result

        text = self.unit_patterns['acres'].sub(replace_acres, text)

        return text, changes

    def _process_pressure_units(self, text: str) -> Tuple[str, List[str]]:
        """Process pressure units"""
        changes = []

        # Process PSI
        def replace_psi(match):
            number = match.group(1)
            result = f"{number} pounds per square inch"
            changes.append(f"Pressure: {match.group()} → {result}")
            return result

        text = self.unit_patterns['psi'].sub(replace_psi, text)

        # Process pascals
        def replace_pa(match):
            number = match.group(1)
            result = f"{number} pascals"
            changes.append(f"Pressure: {match.group()} → {result}")
            return result

        text = self.unit_patterns['pascals'].sub(replace_pa, text)

        # Process atmospheres
        def replace_atm(match):
            number = match.group(1)
            result = f"{number} atmospheres"
            changes.append(f"Pressure: {match.group()} → {result}")
            return result

        text = self.unit_patterns['atmospheres'].sub(replace_atm, text)

        return text, changes

    def _process_frequency_units(self, text: str) -> Tuple[str, List[str]]:
        """Process frequency units"""
        changes = []

        # Process hertz
        def replace_hz(match):
            number = match.group(1)
            result = f"{number} hertz"
            changes.append(f"Frequency: {match.group()} → {result}")
            return result

        text = self.unit_patterns['hertz'].sub(replace_hz, text)

        # Process kilohertz
        def replace_khz(match):
            number = match.group(1)
            result = f"{number} kilohertz"
            changes.append(f"Frequency: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilohertz'].sub(replace_khz, text)

        # Process megahertz
        def replace_mhz(match):
            number = match.group(1)
            result = f"{number} megahertz"
            changes.append(f"Frequency: {match.group()} → {result}")
            return result

        text = self.unit_patterns['megahertz'].sub(replace_mhz, text)

        # Process gigahertz
        def replace_ghz(match):
            number = match.group(1)
            result = f"{number} gigahertz"
            changes.append(f"Frequency: {match.group()} → {result}")
            return result

        text = self.unit_patterns['gigahertz'].sub(replace_ghz, text)

        return text, changes

    def _process_data_storage_units(self, text: str) -> Tuple[str, List[str]]:
        """Process data storage units"""
        changes = []

        # Process bytes
        def replace_bytes(match):
            number = match.group(1)
            result = f"{number} bytes"
            changes.append(f"Data: {match.group()} → {result}")
            return result

        text = self.unit_patterns['bytes'].sub(replace_bytes, text)

        # Process kilobytes
        def replace_kb(match):
            number = match.group(1)
            result = f"{number} kilobytes"
            changes.append(f"Data: {match.group()} → {result}")
            return result

        text = self.unit_patterns['kilobytes'].sub(replace_kb, text)

        # Process megabytes
        def replace_mb(match):
            number = match.group(1)
            result = f"{number} megabytes"
            changes.append(f"Data: {match.group()} → {result}")
            return result

        text = self.unit_patterns['megabytes'].sub(replace_mb, text)

        # Process gigabytes
        def replace_gb(match):
            number = match.group(1)
            result = f"{number} gigabytes"
            changes.append(f"Data: {match.group()} → {result}")
            return result

        text = self.unit_patterns['gigabytes'].sub(replace_gb, text)

        # Process terabytes
        def replace_tb(match):
            number = match.group(1)
            result = f"{number} terabytes"
            changes.append(f"Data: {match.group()} → {result}")
            return result

        text = self.unit_patterns['terabytes'].sub(replace_tb, text)

        return text, changes

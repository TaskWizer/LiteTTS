#!/usr/bin/env python3
"""
Ticker Symbol Processor for TTS
Handles systematic letter-by-letter pronunciation of stock ticker symbols and financial abbreviations
"""

import re
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TickerProcessingResult:
    """Result of ticker symbol processing"""
    processed_text: str
    original_text: str
    tickers_found: List[str]
    changes_made: List[str]
    processing_time: float

class TickerSymbolProcessor:
    """Systematic processor for ticker symbols and financial abbreviations"""
    
    def __init__(self):
        # Load known ticker symbols for explicit processing
        self.known_tickers = self._load_known_tickers()
        
        # Load financial context patterns
        self.financial_contexts = self._load_financial_contexts()
        
        # Load exclusions (words that look like tickers but aren't)
        self.exclusions = self._load_exclusions()
        
        # Configuration
        self.process_known_tickers = True
        self.process_contextual_tickers = True
        self.use_exclusion_list = True
        
    def _load_known_tickers(self) -> Set[str]:
        """Load known ticker symbols for explicit processing"""
        return {
            # Major US stocks
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
            'BRK.A', 'BRK.B', 'UNH', 'JNJ', 'XOM', 'JPM', 'V', 'PG', 'HD',
            'CVX', 'MA', 'BAC', 'ABBV', 'PFE', 'AVGO', 'KO', 'LLY', 'PEP',
            'TMO', 'COST', 'WMT', 'DIS', 'ABT', 'DHR', 'VZ', 'ADBE', 'NFLX',
            'CRM', 'NKE', 'TXN', 'ACN', 'LIN', 'ORCL', 'WFC', 'BMY', 'PM',
            'RTX', 'QCOM', 'NEE', 'UPS', 'T', 'SCHW', 'HON', 'LOW', 'INTU',
            'AMD', 'IBM', 'CAT', 'SPGI', 'GS', 'AMGN', 'DE', 'AXP', 'BLK',
            'ELV', 'BKNG', 'SYK', 'TJX', 'MDLZ', 'ADP', 'GILD', 'MMC', 'CVS',
            'LRCX', 'C', 'TMUS', 'ADI', 'VRTX', 'MO', 'ZTS', 'PYPL', 'SO',
            'ISRG', 'NOW', 'DUK', 'TGT', 'PLD', 'SHW', 'REGN', 'CB', 'CCI',
            
            # Popular growth/tech stocks
            'UBER', 'LYFT', 'SNAP', 'TWTR', 'X', 'SPOT', 'SQ', 'ROKU', 'ZOOM',
            'DOCU', 'SHOP', 'WORK', 'OKTA', 'CRWD', 'ZM', 'PTON', 'PLTR',
            'RBLX', 'COIN', 'HOOD', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
            
            # ETFs and funds
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'BND', 'AGG',
            'GLD', 'SLV', 'USO', 'TLT', 'HYG', 'LQD', 'EEM', 'FXI', 'EWJ',
            'EFA', 'IEFA', 'IEMG', 'VGT', 'XLK', 'XLF', 'XLE', 'XLV', 'XLI',
            'XLP', 'XLY', 'XLU', 'XLRE', 'XLB', 'XME', 'KRE', 'SMH', 'IBB',
            
            # Crypto-related
            'MSTR', 'COIN', 'RIOT', 'MARA', 'BITF', 'HUT', 'BTBT', 'CAN',
            
            # International
            'BABA', 'TSM', 'ASML', 'SAP', 'TM', 'NVO', 'SHEL', 'UL', 'NESN',
            'RHHBY', 'ADYEN', 'SHOP', 'SE', 'GRAB', 'DIDI', 'PDD', 'JD',
            
            # Indices (often referenced)
            'SPX', 'NDX', 'RUT', 'VIX', 'DJI', 'IXIC', 'FTSE', 'DAX', 'CAC',
            'NIKKEI', 'HSI', 'KOSPI', 'ASX', 'TSX', 'IBEX', 'AEX', 'OMX',
        }
    
    def _load_financial_contexts(self) -> List[str]:
        """Load financial context keywords that indicate ticker symbols"""
        return [
            # Stock-related terms
            'stock', 'stocks', 'share', 'shares', 'equity', 'equities',
            'ticker', 'symbol', 'security', 'securities',
            
            # Trading terms
            'trading', 'trade', 'traded', 'buy', 'sell', 'bought', 'sold',
            'long', 'short', 'position', 'positions', 'holding', 'holdings',
            
            # Market movements
            'up', 'down', 'gained', 'lost', 'fell', 'rose', 'climbed', 'dropped',
            'rallied', 'declined', 'surged', 'plunged', 'soared', 'tumbled',
            
            # Financial metrics
            'price', 'prices', 'value', 'valuation', 'market cap', 'volume',
            'earnings', 'revenue', 'profit', 'loss', 'dividend', 'yield',
            
            # Market terms
            'market', 'markets', 'exchange', 'nasdaq', 'nyse', 'otc',
            'ipo', 'spac', 'merger', 'acquisition', 'buyout',
            
            # Analysis terms
            'analyst', 'rating', 'upgrade', 'downgrade', 'target', 'forecast',
            'bullish', 'bearish', 'oversold', 'overbought',
        ]
    
    def _load_exclusions(self) -> Set[str]:
        """Load words that look like tickers but should not be processed"""
        return {
            # Common English words
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN',
            'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM',
            'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO',
            'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO',
            'USE', 'WAY', 'WIN', 'YES', 'YET', 'BIG', 'END', 'FAR', 'FEW',
            'GOT', 'LOT', 'MAN', 'OWN', 'RUN', 'SET', 'TOP', 'TRY', 'ASK',
            'BAD', 'BAG', 'BED', 'BOX', 'CAR', 'CUT', 'DOG', 'EAR', 'EYE',
            'FUN', 'GUN', 'HAD', 'HAT', 'HOT', 'JOB', 'LAW', 'LEG', 'MAP',
            'MOM', 'POP', 'RED', 'SIT', 'SUN', 'TAX', 'TEA', 'TEN', 'TOP',
            'VAN', 'WAR', 'WIN', 'ZIP', 'IS', 'OF', 'TO', 'IN', 'ON', 'AT',
            'BY', 'UP', 'SO', 'NO', 'IF', 'OR', 'MY', 'WE', 'BE', 'DO', 'GO',
            
            # Abbreviations that aren't tickers
            'USA', 'CEO', 'CFO', 'CTO', 'COO', 'CMO', 'CIO', 'HR', 'IT',
            'PR', 'QA', 'RD', 'AI', 'ML', 'AR', 'VR', 'IoT', 'API', 'SDK',
            'URL', 'URI', 'HTTP', 'HTTPS', 'FTP', 'SSH', 'SSL', 'TLS',
            'HTML', 'CSS', 'XML', 'JSON', 'CSV', 'PDF', 'DOC', 'XLS',
            'PPT', 'ZIP', 'RAR', 'TAR', 'GZ', 'MP3', 'MP4', 'AVI', 'MOV',
            'JPG', 'PNG', 'GIF', 'SVG', 'BMP', 'TIFF', 'WEBP',
            
            # Units and measurements
            'KG', 'LB', 'OZ', 'CM', 'MM', 'IN', 'FT', 'YD', 'MI', 'KM',
            'MPH', 'KPH', 'PSI', 'BAR', 'ATM', 'BTU', 'CAL', 'KWH',
            
            # Time zones and locations
            'EST', 'PST', 'CST', 'MST', 'GMT', 'UTC', 'BST', 'CET', 'JST',
            'NYC', 'LA', 'SF', 'DC', 'UK', 'EU', 'US', 'CA', 'AU', 'JP',
            
            # Common acronyms
            'FAQ', 'FYI', 'ASAP', 'ETA', 'EOD', 'COD', 'FOB', 'ROI', 'KPI',
            'SLA', 'NDA', 'IPO', 'M&A', 'B2B', 'B2C', 'P2P', 'SaaS', 'PaaS',
        }
    
    def process_ticker_symbols(self, text: str) -> TickerProcessingResult:
        """Main function to process ticker symbols in text"""
        import time
        start_time = time.perf_counter()
        
        original_text = text
        tickers_found = []
        changes_made = []
        
        logger.debug(f"Processing ticker symbols in: {text[:100]}...")
        
        try:
            # Step 1: Process known ticker symbols explicitly
            if self.process_known_tickers:
                old_text = text
                text, found_tickers = self._process_known_tickers(text)
                if found_tickers:
                    tickers_found.extend(found_tickers)
                    changes_made.append(f"Processed known tickers: {', '.join(found_tickers)}")
            
            # Step 2: Process contextual ticker symbols
            if self.process_contextual_tickers:
                old_text = text
                text, contextual_tickers = self._process_contextual_tickers(text)
                if contextual_tickers:
                    tickers_found.extend(contextual_tickers)
                    changes_made.append(f"Processed contextual tickers: {', '.join(contextual_tickers)}")
            
            processing_time = time.perf_counter() - start_time
            
            logger.debug(f"Ticker processing complete: {text[:100]}...")
            
            return TickerProcessingResult(
                processed_text=text,
                original_text=original_text,
                tickers_found=list(set(tickers_found)),  # Remove duplicates
                changes_made=changes_made,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in ticker processing: {e}")
            processing_time = time.perf_counter() - start_time
            
            return TickerProcessingResult(
                processed_text=original_text,  # Return original on error
                original_text=original_text,
                tickers_found=[],
                changes_made=[f"Error: {e}"],
                processing_time=processing_time
            )
    
    def _process_known_tickers(self, text: str) -> tuple[str, List[str]]:
        """Process explicitly known ticker symbols"""
        found_tickers = []
        
        for ticker in self.known_tickers:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(ticker) + r'\b'
            if re.search(pattern, text):
                # Convert to letter-by-letter spelling
                spelled_out = '-'.join(list(ticker))
                text = re.sub(pattern, spelled_out, text)
                found_tickers.append(ticker)
                logger.debug(f"Processed known ticker: {ticker} → {spelled_out}")
        
        return text, found_tickers
    
    def _process_contextual_tickers(self, text: str) -> tuple[str, List[str]]:
        """Process potential ticker symbols based on financial context"""
        found_tickers = []
        
        # Create pattern for financial contexts
        context_pattern = '|'.join(re.escape(ctx) for ctx in self.financial_contexts)
        
        # Pattern to match potential ticker symbols in financial contexts:
        # - 2-5 uppercase letters
        # - Preceded or followed by financial context words
        # - Not in exclusion list
        ticker_pattern = rf'\b([A-Z]{{2,5}})\b(?=\s+(?:{context_pattern})|\s*[\$\+\-\%]|\s+(?:up|down|gained?|lost?|fell?|rose?|climbed?))'
        
        def spell_out_contextual_ticker(match):
            ticker = match.group(1)

            # Skip if in exclusion list (case-insensitive check)
            if self.use_exclusion_list and ticker.upper() in self.exclusions:
                return ticker

            # Skip if already a known ticker (handled separately)
            if ticker in self.known_tickers:
                return ticker

            # Convert to letter-by-letter spelling
            spelled_out = '-'.join(list(ticker))
            found_tickers.append(ticker)
            logger.debug(f"Processed contextual ticker: {ticker} → {spelled_out}")
            return spelled_out
        
        # Apply contextual ticker processing
        text = re.sub(ticker_pattern, spell_out_contextual_ticker, text, flags=re.IGNORECASE)
        
        return text, found_tickers
    
    def analyze_potential_tickers(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for potential ticker symbols without processing"""
        analysis = {
            'known_tickers': [],
            'contextual_candidates': [],
            'excluded_words': [],
            'ambiguous_cases': []
        }
        
        # Find all uppercase 2-5 letter words
        potential_tickers = re.findall(r'\b[A-Z]{2,5}\b', text)
        
        for candidate in set(potential_tickers):
            if candidate in self.known_tickers:
                analysis['known_tickers'].append(candidate)
            elif candidate in self.exclusions:
                analysis['excluded_words'].append(candidate)
            else:
                # Check if it appears in financial context
                context_pattern = '|'.join(re.escape(ctx) for ctx in self.financial_contexts)
                if re.search(rf'\b{re.escape(candidate)}\b.*?(?:{context_pattern})', text, re.IGNORECASE):
                    analysis['contextual_candidates'].append(candidate)
                else:
                    analysis['ambiguous_cases'].append(candidate)
        
        return analysis

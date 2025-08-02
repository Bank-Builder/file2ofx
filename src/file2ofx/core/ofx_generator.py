"""OFX file generation functionality for file2ofx."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from lxml import etree


class OFXGenerator:
    """Generate OFX-compliant files from transaction data."""

    def __init__(self) -> None:
        """Initialize the OFX generator."""
        self.ofx_version = "102"
        self.fi_org = None
        self.fi_id = None
        self.account_id = None
        self.account_type = "CHECKING"
        self.currency = "USD"
        self.ledger_balance = None
        self.available_balance = None

    def generate_ofx(
        self,
        transactions: List[Dict[str, str]],
        output_path: Path,
        ofx_version: str = "102",
        fi_org: Optional[str] = None,
        fi_id: Optional[str] = None,
        account_id: Optional[str] = None,
        account_type: str = "CHECKING",
        currency: str = "USD",
        ledger_balance: Optional[float] = None,
        available_balance: Optional[float] = None,
    ) -> None:
        """Generate OFX file from transaction data.
        
        Args:
            transactions: List of transaction dictionaries
            output_path: Path to output OFX file
            ofx_version: OFX version (default: "102")
            fi_org: Financial institution organization name
            fi_id: Financial institution ID
            account_id: Account ID
            account_type: Account type (default: "CHECKING")
            currency: Currency code (default: "USD")
            ledger_balance: Ledger balance amount
            available_balance: Available balance amount
            
        Raises:
            ValueError: If transactions are invalid or generation fails
        """
        if not transactions:
            raise ValueError("No transactions to convert")

        try:
            # Store configuration
            self.ofx_version = ofx_version
            self.fi_org = fi_org
            self.fi_id = fi_id
            self.account_id = account_id
            self.account_type = account_type
            self.currency = currency
            self.ledger_balance = ledger_balance
            self.available_balance = available_balance

            # Create OFX document structure
            ofx_root = self._create_ofx_structure()

            # Add transactions to OFX
            self._add_transactions_to_ofx(ofx_root, transactions)

            # Write OFX file
            self._write_ofx_file(ofx_root, output_path)

        except Exception as e:
            raise ValueError(f"Error generating OFX file: {e}")

    def _create_ofx_structure(self) -> etree.Element:
        """Create the basic OFX document structure.
        
        Returns:
            OFX root element
        """
        # Create OFX root element
        ofx_root = etree.Element("OFX")

        # Add OFX header
        header = etree.SubElement(ofx_root, "OFXHEADER")
        header.text = "100"

        # Add data
        data = etree.SubElement(ofx_root, "DATA")
        data.text = "OFXSGML"

        # Add version
        version = etree.SubElement(ofx_root, "VERSION")
        version.text = self.ofx_version

        # Add security
        security = etree.SubElement(ofx_root, "SECURITY")
        security.text = "NONE"

        # Add encoding
        encoding = etree.SubElement(ofx_root, "ENCODING")
        encoding.text = "UTF-8"

        # Add charset
        charset = etree.SubElement(ofx_root, "CHARSET")
        charset.text = "CSUNICODE"

        # Add compression
        compression = etree.SubElement(ofx_root, "COMPRESSION")
        compression.text = "NONE"

        # Add old file UID
        old_file_uid = etree.SubElement(ofx_root, "OLDFILEUID")
        old_file_uid.text = "NONE"

        # Add new file UID
        new_file_uid = etree.SubElement(ofx_root, "NEWFILEUID")
        new_file_uid.text = "NONE"

        # Add SIGNONMSGSRSV1 section
        self._add_signon_section(ofx_root)

        return ofx_root

    def _add_signon_section(self, ofx_root: etree.Element) -> None:
        """Add SIGNONMSGSRSV1 section to OFX document.
        
        Args:
            ofx_root: OFX root element
        """
        # Create SIGNONMSGSRSV1 element
        signon_msgs = etree.SubElement(ofx_root, "SIGNONMSGSRSV1")
        
        # Create SONRS element
        son_rs = etree.SubElement(signon_msgs, "SONRS")
        
        # Add STATUS
        status = etree.SubElement(son_rs, "STATUS")
        code = etree.SubElement(status, "CODE")
        code.text = "0"
        severity = etree.SubElement(status, "SEVERITY")
        severity.text = "INFO"
        
        # Add DTSERVER (current timestamp)
        dt_server = etree.SubElement(son_rs, "DTSERVER")
        dt_server.text = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Add LANGUAGE
        language = etree.SubElement(son_rs, "LANGUAGE")
        language.text = "ENG"
        
        # Add DTPROFUP (same as DTSERVER)
        dt_prof_up = etree.SubElement(son_rs, "DTPROFUP")
        dt_prof_up.text = dt_server.text
        
        # Add DTACCTUP (same as DTSERVER)
        dt_acct_up = etree.SubElement(son_rs, "DTACCTUP")
        dt_acct_up.text = dt_server.text
        
        # Add FI (Financial Institution) if provided
        if self.fi_org or self.fi_id:
            fi = etree.SubElement(son_rs, "FI")
            if self.fi_org:
                org = etree.SubElement(fi, "ORG")
                org.text = self.fi_org
            if self.fi_id:
                fid = etree.SubElement(fi, "FID")
                fid.text = self.fi_id

    def _add_transactions_to_ofx(
        self,
        ofx_root: etree.Element,
        transactions: List[Dict[str, str]],
    ) -> None:
        """Add transactions to OFX document.
        
        Args:
            ofx_root: OFX root element
            transactions: List of transaction dictionaries
        """
        # Create BANKMSGSRSV1 element
        bank_msgs = etree.SubElement(ofx_root, "BANKMSGSRSV1")

        # Create STMTTRNRS element
        stmt_trnrs = etree.SubElement(bank_msgs, "STMTTRNRS")

        # Add TRNUID
        trn_uid = etree.SubElement(stmt_trnrs, "TRNUID")
        trn_uid.text = "0"

        # Add STATUS
        status = etree.SubElement(stmt_trnrs, "STATUS")
        code = etree.SubElement(status, "CODE")
        code.text = "0"
        severity = etree.SubElement(status, "SEVERITY")
        severity.text = "INFO"

        # Create STMTRS element
        stmt_rs = etree.SubElement(stmt_trnrs, "STMTRS")

        # Add CURDEF
        cur_def = etree.SubElement(stmt_rs, "CURDEF")
        cur_def.text = self.currency

        # Create BANKACCTFROM element
        bank_acct_from = etree.SubElement(stmt_rs, "BANKACCTFROM")
        bank_id = etree.SubElement(bank_acct_from, "BANKID")
        bank_id.text = self.fi_id or "000000000"
        acct_id = etree.SubElement(bank_acct_from, "ACCTID")
        acct_id.text = self.account_id or "000000000000"
        acct_type = etree.SubElement(bank_acct_from, "ACCTTYPE")
        acct_type.text = self.account_type

        # Create BANKTRANLIST element
        bank_tran_list = etree.SubElement(stmt_rs, "BANKTRANLIST")

        # Add date range
        dt_start = etree.SubElement(bank_tran_list, "DTSTART")
        if transactions:
            start_date = self._get_earliest_date(transactions)
            dt_start.text = self._format_ofx_date(start_date)

        dt_end = etree.SubElement(bank_tran_list, "DTEND")
        if transactions:
            end_date = self._get_latest_date(transactions)
            dt_end.text = self._format_ofx_date(end_date)

        # Add transactions
        for transaction in transactions:
            self._add_transaction_to_list(bank_tran_list, transaction)

        # Add balance information
        self._add_balance_sections(stmt_rs)

    def _add_transaction_to_list(
        self,
        bank_tran_list: etree.Element,
        transaction: Dict[str, str],
    ) -> None:
        """Add a single transaction to the OFX transaction list.
        
        Args:
            bank_tran_list: BANKTRANLIST element
            transaction: Transaction dictionary
        """
        stmt_trn = etree.SubElement(bank_tran_list, "STMTTRN")

        # Add transaction type
        trn_type = etree.SubElement(stmt_trn, "TRNTYPE")
        trn_type.text = self._determine_transaction_type(transaction)

        # Add date posted
        dt_posted = etree.SubElement(stmt_trn, "DTPOSTED")
        if "date" in transaction:
            dt_posted.text = self._format_ofx_date(transaction["date"])

        # Add user date (same as posted date)
        dt_user = etree.SubElement(stmt_trn, "DTUSER")
        if "date" in transaction:
            dt_user.text = self._format_ofx_date(transaction["date"])

        # Add transaction amount
        trn_amt = etree.SubElement(stmt_trn, "TRNAMT")
        if "amount" in transaction:
            amount = self._normalize_amount(transaction["amount"])
            trn_amt.text = amount

        # Add transaction ID
        fit_id = etree.SubElement(stmt_trn, "FITID")
        if "date" in transaction and "amount" in transaction:
            # Create a unique transaction ID
            date_part = self._format_ofx_date(transaction["date"])
            amount_part = self._normalize_amount(transaction["amount"])
            fit_id.text = f"{date_part}_{amount_part}"
        else:
            fit_id.text = "0"

        # Add memo/description
        if "description" in transaction:
            name = etree.SubElement(stmt_trn, "NAME")
            name.text = self._sanitize_text(transaction["description"])

    def _add_balance_sections(self, stmt_rs: etree.Element) -> None:
        """Add balance sections to OFX document.
        
        Args:
            stmt_rs: STMTRS element
        """
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Add LEDGERBAL if provided
        if self.ledger_balance is not None:
            ledger_bal = etree.SubElement(stmt_rs, "LEDGERBAL")
            bal_amt = etree.SubElement(ledger_bal, "BALAMT")
            bal_amt.text = f"{self.ledger_balance:.2f}"
            dt_asof = etree.SubElement(ledger_bal, "DTASOF")
            dt_asof.text = current_time
        
        # Add AVAILBAL if provided
        if self.available_balance is not None:
            avail_bal = etree.SubElement(stmt_rs, "AVAILBAL")
            bal_amt = etree.SubElement(avail_bal, "BALAMT")
            bal_amt.text = f"{self.available_balance:.2f}"
            dt_asof = etree.SubElement(avail_bal, "DTASOF")
            dt_asof.text = current_time

    def _determine_transaction_type(self, transaction: Dict[str, str]) -> str:
        """Determine OFX transaction type from transaction data.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            OFX transaction type
        """
        # Check if type is explicitly provided
        if "type" in transaction:
            trans_type = transaction["type"].lower()

            # Map common transaction types to OFX types
            type_mapping = {
                "debit": "DEBIT",
                "credit": "CREDIT",
                "deposit": "CREDIT",
                "withdrawal": "DEBIT",
                "transfer": "XFER",
                "payment": "DEBIT",
                "purchase": "DEBIT",
                "refund": "CREDIT",
                "fee": "DEBIT",
                "interest": "CREDIT",
            }

            if trans_type in type_mapping:
                return type_mapping[trans_type]

        # Try to determine from amount
        if "amount" in transaction:
            amount = transaction["amount"]
            # Remove currency symbols and convert to float
            clean_amount = re.sub(r"[$€£¥₹₽₿,]", "", amount)
            try:
                float_amount = float(clean_amount)
                if float_amount < 0:
                    return "DEBIT"
                else:
                    return "CREDIT"
            except ValueError:
                pass

        # Default to DEBIT
        return "DEBIT"

    def _normalize_amount(self, amount: str) -> str:
        """Normalize amount string for OFX format.
        
        Args:
            amount: Amount string
            
        Returns:
            Normalized amount string
        """
        # Remove currency symbols and whitespace
        clean_amount = re.sub(r"[$€£¥₹₽₿\s]", "", amount)

        # Remove thousands separators
        clean_amount = re.sub(r",", "", clean_amount)

        # Ensure proper decimal format
        if "." in clean_amount:
            # Already has decimal
            return clean_amount
        else:
            # Assume cents if no decimal
            return f"{clean_amount}.00"

    def _format_ofx_date(self, date_str: str) -> str:
        """Format date string for OFX format (YYYYMMDDHHMMSS).
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            OFX formatted date string with time
        """
        # Try various date formats
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%Y%m%d",
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y%m%d%H%M%S")
            except ValueError:
                continue

        # If no format works, return original
        return date_str

    def _get_earliest_date(self, transactions: List[Dict[str, str]]) -> str:
        """Get the earliest date from transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Earliest date string
        """
        dates = []
        for transaction in transactions:
            if "date" in transaction:
                dates.append(transaction["date"])

        if not dates:
            return datetime.now().strftime("%Y%m%d")

        # Try to parse and find earliest
        parsed_dates = []
        for date_str in dates:
            try:
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    parsed_dates.append(parsed_date)
            except ValueError:
                continue

        if parsed_dates:
            earliest = min(parsed_dates)
            return earliest.strftime("%Y%m%d")

        return datetime.now().strftime("%Y%m%d")

    def _get_latest_date(self, transactions: List[Dict[str, str]]) -> str:
        """Get the latest date from transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Latest date string
        """
        dates = []
        for transaction in transactions:
            if "date" in transaction:
                dates.append(transaction["date"])

        if not dates:
            return datetime.now().strftime("%Y%m%d")

        # Try to parse and find latest
        parsed_dates = []
        for date_str in dates:
            try:
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    parsed_dates.append(parsed_date)
            except ValueError:
                continue

        if parsed_dates:
            latest = max(parsed_dates)
            return latest.strftime("%Y%m%d")

        return datetime.now().strftime("%Y%m%d")

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object.
        
        Args:
            date_str: Date string
            
        Returns:
            Parsed datetime or None
        """
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%Y%m%d",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for OFX format.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove or replace problematic characters
        sanitized = text.replace("&", "&amp;")
        sanitized = sanitized.replace("<", "&lt;")
        sanitized = sanitized.replace(">", "&gt;")
        sanitized = sanitized.replace('"', "&quot;")
        sanitized = sanitized.replace("'", "&apos;")

        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:252] + "..."

        return sanitized

    def _write_ofx_file(self, ofx_root: etree.Element, output_path: Path) -> None:
        """Write OFX document to file.
        
        Args:
            ofx_root: OFX root element
            output_path: Path to output file
        """
        # Create XML tree
        tree = etree.ElementTree(ofx_root)

        # Write to file with proper formatting
        with open(output_path, "wb") as f:
            tree.write(
                f,
                encoding="utf-8",
                xml_declaration=True,
                pretty_print=True,
            )

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

        # Add transaction amount
        trn_amt = etree.SubElement(stmt_trn, "TRNAMT")
        if "amount" in transaction:
            amount = self._normalize_amount(transaction["amount"])
            trn_amt.text = amount

        # Add transaction ID
        fit_id = etree.SubElement(stmt_trn, "FITID")
        # Generate a proper transaction ID (8 digits like the working file)
        import hashlib
        if "date" in transaction and "amount" in transaction:
            # Create a hash-based ID similar to the working file format
            content = f"{transaction['date']}_{transaction['amount']}"
            if "description" in transaction:
                content += f"_{transaction['description']}"
            hash_obj = hashlib.md5(content.encode())
            # Take first 8 characters of hash and convert to decimal
            hash_hex = hash_obj.hexdigest()[:8]
            fit_id.text = str(int(hash_hex, 16))[:8].zfill(8)
        else:
            fit_id.text = "00000000"

        # Add memo/description
        if "description" in transaction:
            name = etree.SubElement(stmt_trn, "NAME")
            name.text = self._sanitize_text(transaction["description"])



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
        """Write OFX file in SGML format (not XML).
        
        Args:
            ofx_root: OFX root element
            output_path: Path to output file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write SGML header (not XML)
                f.write("OFXHEADER:100\n")
                f.write("DATA:OFXSGML\n")
                f.write(f"VERSION:{self.ofx_version}\n")
                f.write("SECURITY:NONE\n")
                f.write("ENCODING:UTF-8\n")
                f.write("CHARSET:CSUNICODE\n")
                f.write("COMPRESSION:NONE\n")
                f.write("OLDFILEUID:NONE\n")
                f.write("NEWFILEUID:NONE\n\n")
                
                # Write SGML content without closing tags
                f.write("<OFX>\n")
                self._write_sgml_element(f, ofx_root, indent=2)
                f.write("</OFX>\n")
                
        except Exception as e:
            raise ValueError(f"Error writing OFX file: {e}")

    def _write_sgml_element(self, f, element, indent=0):
        """Write SGML element without closing tags.
        
        Args:
            f: File object
            element: XML element
            indent: Indentation level
        """
        spaces = "  " * indent
        
        for child in element:
            if child.tag in ["OFXHEADER", "DATA", "VERSION", "SECURITY", "ENCODING", "CHARSET", "COMPRESSION", "OLDFILEUID", "NEWFILEUID"]:
                # Skip these as they're handled in the header
                continue
                
            if child.text and child.text.strip():
                f.write(f"{spaces}<{child.tag}>{child.text}\n")
            else:
                f.write(f"{spaces}<{child.tag}>\n")
                self._write_sgml_element(f, child, indent + 1)

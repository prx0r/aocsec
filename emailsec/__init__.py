"""Email security checks — SPF/DKIM/DMARC via DNS-over-HTTPS.

Email is the master key (every reset flows through it) and the top
fraud vector (supplier bank-detail changes). These checks use Google's
DoH resolver (free, no key) so there's no dnspython dependency.

Findings are observations with fixes, never exploit attempts.
"""

from .dns import spf_record, dmarc_record, dkim_record
from .invoice_verify import assess_payment_change, verification_checklist

__all__ = ["spf_record", "dmarc_record", "dkim_record",
           "assess_payment_change", "verification_checklist"]

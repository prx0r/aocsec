"""Document vault — content-addressed storage per business.

Certificates, reports, e-manuals, handover docs land here keyed by
SHA-256. Same bytes = same key (dedupe free). Retrieval by hash;
listing by business. The audit chain records issuance, the vault
holds the bytes.
"""

from .vault import get_document, list_documents, store_document

__all__ = ["get_document", "list_documents", "store_document"]

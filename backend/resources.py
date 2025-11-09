"""
Government resources and official links for MCS Act
This module provides relevant government links based on user queries
"""

# Official government websites and resources
GOVERNMENT_RESOURCES = {
    "registration": {
        "title": "Society Registration",
        "links": [
            {
                "name": "Maharashtra State Cooperative Department",
                "url": "https://cooperation.maharashtra.gov.in/",
                "description": "Official portal for cooperative societies registration"
            },
            {
                "name": "Online Registration Portal",
                "url": "https://cooperatives.maharashtra.gov.in/",
                "description": "Apply for new society registration online"
            }
        ]
    },
    "audit": {
        "title": "Audit & Compliance",
        "links": [
            {
                "name": "Audit Guidelines",
                "url": "https://cooperation.maharashtra.gov.in/content/audit",
                "description": "Official audit procedures and requirements"
            }
        ]
    },
    "disputes": {
        "title": "Dispute Resolution",
        "links": [
            {
                "name": "Cooperative Court",
                "url": "https://cooperation.maharashtra.gov.in/content/cooperative-court",
                "description": "File disputes and check case status"
            }
        ]
    },
    "forms": {
        "title": "Forms & Documents",
        "links": [
            {
                "name": "Download Forms",
                "url": "https://cooperation.maharashtra.gov.in/content/forms",
                "description": "All official forms for societies"
            }
        ]
    },
    "general": {
        "title": "General Information",
        "links": [
            {
                "name": "MCS Act Full Text",
                "url": "https://cooperation.maharashtra.gov.in/content/acts",
                "description": "Read the complete MCS Act online"
            },
            {
                "name": "FAQs",
                "url": "https://cooperation.maharashtra.gov.in/content/faqs",
                "description": "Frequently asked questions"
            }
        ]
    }
}


def get_relevant_links(question: str, context: str) -> list:
    """
    Get relevant government links based on the question topic
    
    This function analyzes the user's question and the retrieved context
    to determine which government resources would be most helpful.
    
    Args:
        question: User's question string
        context: Retrieved context from documents
    
    Returns:
        List of relevant resource dictionaries with title and links
    """
    relevant_resources = []
    
    # Convert to lowercase for case-insensitive matching
    question_lower = question.lower()
    context_lower = context.lower()
    combined_text = f"{question_lower} {context_lower}"
    
    # Check for registration-related queries
    # Keywords: register, registration, form society, start society, new society
    if any(word in combined_text for word in ["register", "registration", "form society", "start society", "new society", "forming", "formation"]):
        relevant_resources.append(GOVERNMENT_RESOURCES["registration"])
    
    # Check for audit-related queries
    # Keywords: audit, accounts, financial, auditor, accounting
    if any(word in combined_text for word in ["audit", "accounts", "financial", "auditor", "accounting", "books"]):
        relevant_resources.append(GOVERNMENT_RESOURCES["audit"])
    
    # Check for dispute-related queries
    # Keywords: dispute, conflict, court, case, litigation, arbitration, complaint
    if any(word in combined_text for word in ["dispute", "conflict", "court", "case", "litigation", "arbitration", "complaint", "legal action"]):
        relevant_resources.append(GOVERNMENT_RESOURCES["disputes"])
    
    # Check for forms-related queries
    # Keywords: form, application, document, download, file
    if any(word in combined_text for word in ["form", "application", "document", "download", "file", "submit"]):
        relevant_resources.append(GOVERNMENT_RESOURCES["forms"])
    
    # Always add general resources if no specific match found
    # This ensures users always have access to helpful links
    if not relevant_resources:
        relevant_resources.append(GOVERNMENT_RESOURCES["general"])
    
    return relevant_resources


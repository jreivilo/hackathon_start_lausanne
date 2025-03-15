def get_analysis_schema():
    """
    Returns the JSON schema for structured analysis.
    """
    return {
        "properties": {
            "analysis": {
                "type": "object",
                "description": "Detailed analysis of the request",
                "properties": {
                    "response": {
                        "type": "string",
                        "description": "Main response to the user's request"
                    },
                    "keywords": {
                        "type": "array",
                        "description": "Relevant keywords identified in the request",
                        "items": {
                            "type": "string"
                        }
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level in the response (0-1)"
                    }
                }
            }
        }
    }

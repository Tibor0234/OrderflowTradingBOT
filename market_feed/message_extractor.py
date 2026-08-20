class MessageExtractor:
    """Timestamp és egyéb metaadatok kinyerése üzenetekből."""

    @staticmethod
    def extract_timestamp(item):
        """
        Timestamp kinyerése az üzenetből.
        
        Az üzenet különböző formátumokat támogat.
        """
        return (
            item.get("T")
            or item.get("time")
            or item.get("E")
            or item.get("open_time")
        )

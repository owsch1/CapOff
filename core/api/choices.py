class BannerLocation:
    HEAD = 'head'        # Hero oben
    MIDDLE = 'middle'    # Mittlerer Promo-Bereich
    CATALOG = 'catalog'  # Katalog-Block

    CHOICES = [
        (HEAD, 'Head / Hero'),
        (MIDDLE, 'Middle / Mitte'),
        (CATALOG, 'Catalog / Katalog'),
    ]
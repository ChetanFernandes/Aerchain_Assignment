from src.backend.procurement_models import NormalizedVendorQuote


class VendorQuoteCollection:
    def __init__(self):
        self.quotes: list[NormalizedVendorQuote] = []

    def add(self, quote: NormalizedVendorQuote):
        self.quotes.append(quote)

    def get_all(self):
        return self.quotes
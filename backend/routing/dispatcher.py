ROUTES = {
    "medical": "ambulance",
    "fire": "fire_station",
    "crime": "police",
    "accident": "ambulance",
    "unknown": "operator_review"
}

class Dispatcher:
    def route(self, category: str) -> str:
        return ROUTES.get(category, "operator_review")

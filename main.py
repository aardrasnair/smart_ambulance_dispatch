from src.graph import Graph
from src.dispatch import assign_ambulance


def build_city():
    city = Graph()

    nodes = ["A", "B", "C", "D", "E"]
    for node in nodes:
        city.add_node(node)

    city.add_edge("A", "B", 4)
    city.add_edge("B", "C", 3)
    city.add_edge("A", "D", 2)
    city.add_edge("D", "C", 5)
    city.add_edge("C", "E", 6)
    city.add_edge("B", "E", 10)

    return city


def main():
    print("Program started...")

    city = build_city()
    ambulances = ["A", "B"]
    patient_location = "E"

    ambulance, time, path = assign_ambulance(
        city, ambulances, patient_location
    )

    print("Assigned Ambulance:", ambulance)
    print("Estimated Time:", time)
    print("Route:", " -> ".join(path))


if __name__ == "__main__":
    main()
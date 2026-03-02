from src.routing import dijkstra, reconstruct_path

def assign_ambulance(graph, ambulances, patient_location):
    best_time = float('inf')
    best_ambulance = None
    best_path = []

    for ambulance in ambulances:
        distances, previous = dijkstra(graph, ambulance)

        if distances[patient_location] < best_time:
            best_time = distances[patient_location]
            best_ambulance = ambulance
            best_path = reconstruct_path(previous, ambulance, patient_location)

    return best_ambulance, best_time, best_path
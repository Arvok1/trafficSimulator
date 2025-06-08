from .vehicle import Vehicle
from numpy.random import randint

class VehicleGenerator:
    def __init__(self, config={}):
        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.vehicle_rate = 10
        self.vehicles = [
            (1, {'lane': 0})  # Default to lane 0
        ]
        self.last_added_time = 0

    def init_properties(self):
        self.upcoming_vehicle = self.generate_vehicle()

    def generate_vehicle(self):
        """Returns a random vehicle from self.vehicles with random proportions"""
        total = sum(pair[0] for pair in self.vehicles)
        r = randint(1, total+1)
        for (weight, config) in self.vehicles:
            r -= weight
            if r <= 0:
                return Vehicle(config)

    def update(self, simulation):
        """Add vehicles"""
        if simulation.t - self.last_added_time >= 60 / self.vehicle_rate:
            # If time elapsed after last added vehicle is
            # greater than vehicle_period; generate a vehicle
            segment = simulation.segments[self.upcoming_vehicle.path[0]]
            lane = self.upcoming_vehicle.lane
            
            # Check if the lane exists in the segment
            if lane >= segment.num_lanes:
                self.upcoming_vehicle = self.generate_vehicle()
                return
                
            # Get vehicles in the specific lane
            vehicles_in_lane = segment.get_vehicles_in_lane(lane)
            
            # Check if there's space in the lane
            if len(vehicles_in_lane) == 0 or \
               simulation.vehicles[vehicles_in_lane[-1]].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:
                # If there is space for the generated vehicle; add it
                simulation.add_vehicle(self.upcoming_vehicle)
                # Reset last_added_time and upcoming_vehicle
                self.last_added_time = simulation.t
            self.upcoming_vehicle = self.generate_vehicle()

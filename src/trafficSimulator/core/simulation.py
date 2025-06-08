from .vehicle_generator import VehicleGenerator
from .geometry.quadratic_curve import QuadraticCurve
from .geometry.cubic_curve import CubicCurve
from .geometry.segment import Segment
from .vehicle import Vehicle


class Simulation:
    def __init__(self):
        self.segments = []
        self.vehicles = {}
        self.vehicle_generator = []

        self.t = 0.0
        self.frame_count = 0
        self.dt = 1/60  


    def add_vehicle(self, veh):
        self.vehicles[veh.id] = veh
        if len(veh.path) > 0:
            self.segments[veh.path[0]].add_vehicle(veh, veh.lane)

    def add_segment(self, seg):
        self.segments.append(seg)

    def add_vehicle_generator(self, gen):
        self.vehicle_generator.append(gen)

    
    def create_vehicle(self, **kwargs):
        veh = Vehicle(kwargs)
        self.add_vehicle(veh)

    def create_segment(self, *args, num_lanes=1):
        seg = Segment(args, num_lanes)
        self.add_segment(seg)

    def create_quadratic_bezier_curve(self, start, control, end, num_lanes=1):
        cur = QuadraticCurve(start, control, end)
        cur.num_lanes = num_lanes
        cur.lanes = [deque() for _ in range(num_lanes)]
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, start, control_1, control_2, end, num_lanes=1):
        cur = CubicCurve(start, control_1, control_2, end)
        cur.num_lanes = num_lanes
        cur.lanes = [deque() for _ in range(num_lanes)]
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)


    def run(self, steps):
        for _ in range(steps):
            self.update()

    def update(self):
        # Update vehicles
        for segment in self.segments:
            for lane in range(segment.num_lanes):
                vehicles_in_lane = segment.get_vehicles_in_lane(lane)
                if len(vehicles_in_lane) != 0:
                    self.vehicles[vehicles_in_lane[0]].update(None, self.dt)
                for i in range(1, len(vehicles_in_lane)):
                    self.vehicles[vehicles_in_lane[i]].update(self.vehicles[vehicles_in_lane[i-1]], self.dt)

        # Check roads for out of bounds vehicle
        for segment in self.segments:
            for lane in range(segment.num_lanes):
                vehicles_in_lane = segment.get_vehicles_in_lane(lane)
                # If lane has no vehicles, continue
                if len(vehicles_in_lane) == 0: continue
                # If not
                vehicle_id = vehicles_in_lane[0]
                vehicle = self.vehicles[vehicle_id]
                # If first vehicle is out of road bounds
                if vehicle.x >= segment.get_length():
                    # If vehicle has a next road
                    if vehicle.current_road_index + 1 < len(vehicle.path):
                        # Update current road to next road
                        vehicle.current_road_index += 1
                        # Add it to the next road
                        next_road_index = vehicle.path[vehicle.current_road_index]
                        self.segments[next_road_index].add_vehicle(vehicle, vehicle.lane)
                        # Reset vehicle properties
                        vehicle.x = 0
                    else:
                        # Vehicle has completed its path, remove it from simulation
                        del self.vehicles[vehicle_id]
                    # In all cases, remove it from its current road
                    segment.remove_vehicle(vehicle, lane)

        # Update vehicle generators
        for gen in self.vehicle_generator:
            gen.update(self)
        # Increment time
        self.t += self.dt
        self.frame_count += 1

from trafficSimulator import *

# Create simulation
sim = Simulation()

# Create a straight road with 2 lanes in each direction
# Parameters
lane_width = 3.5  # Standard lane width in meters
road_length = 100  # Length of the road segment

# Create two parallel road segments (one for each direction)
# Northbound road (2 lanes)
sim.create_segment(
    (-lane_width, 0),  # Start point
    (-lane_width, road_length),  # End point
    num_lanes=2  # Two lanes
)

# Southbound road (2 lanes)
sim.create_segment(
    (lane_width, road_length),  # Start point
    (lane_width, 0),  # End point
    num_lanes=2  # Two lanes
)

# Create vehicle generators for both directions
# Northbound vehicles
sim.create_vehicle_generator(
    vehicle_rate=20,  # Vehicles per minute
    vehicles=[
        # Lane 0 (left lane)
        (10, {
            'path': [0],  # Use first segment
            'v': 16.6,    # Speed in m/s (60 km/h)
            'lane': 0     # Left lane
        }),
        # Lane 1 (right lane)
        (10, {
            'path': [0],
            'v': 13.9,    # Slightly slower (50 km/h)
            'lane': 1     # Right lane
        })
    ]
)

# Southbound vehicles
sim.create_vehicle_generator(
    vehicle_rate=20,
    vehicles=[
        # Lane 0 (left lane)
        (10, {
            'path': [1],  # Use second segment
            'v': 16.6,
            'lane': 0
        }),
        # Lane 1 (right lane)
        (10, {
            'path': [1],
            'v': 13.9,
            'lane': 1
        })
    ]
)

# Create window and run simulation
win = Window(sim)
win.run()
win.show() 
import dearpygui.dearpygui as dpg
import numpy as np
import colorsys


class Window:
    def __init__(self, simulation):
        self.simulation = simulation

        self.zoom = 7
        self.offset = (0, 0)
        self.speed = 1

        self.is_running = False
        self.selected_vehicle = None
        self.vehicle_colors = {}  # Store unique colors for each vehicle

        self.is_dragging = False
        self.old_offset = (0, 0)
        self.zoom_speed = 1

        self.setup()
        self.setup_themes()
        self.create_windows()
        self.create_handlers()
        self.resize_windows()

    def setup(self):
        dpg.create_context()
        dpg.create_viewport(title="TrafficSimulator", width=1280, height=720)
        dpg.setup_dearpygui()

    def setup_themes(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
                # dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, (8, 6), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (90, 90, 95))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 91, 140))
            with dpg.theme_component(dpg.mvInputInt):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (90, 90, 95), category=dpg.mvThemeCat_Core)
            #     dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

        dpg.bind_theme(global_theme)

        # dpg.show_style_editor()

        with dpg.theme(tag="RunButtonTheme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (5, 150, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (12, 207, 23))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (2, 120, 10))

        with dpg.theme(tag="StopButtonTheme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (150, 5, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (207, 12, 23))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (120, 2, 10))


    def create_windows(self):
        dpg.add_window(
            tag="MainWindow",
            label="Simulation",
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_move=True
        )
        
        dpg.add_draw_node(tag="OverlayCanvas", parent="MainWindow")
        dpg.add_draw_node(tag="Canvas", parent="MainWindow")

        with dpg.window(
            tag="ControlsWindow",
            label="Controls",
            no_close=True,
            no_collapse=True,
            no_resize=True,
            no_move=True
        ):
            with dpg.collapsing_header(label="Simulation Control", default_open=True):

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Run", tag="RunStopButton", callback=self.toggle)
                    dpg.add_button(label="Next frame", callback=self.simulation.update)

                dpg.add_slider_int(tag="SpeedInput", label="Speed", min_value=1, max_value=100,default_value=1, callback=self.set_speed)
            
            with dpg.collapsing_header(label="Simulation Status", default_open=True):

                with dpg.table(header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    
                    with dpg.table_row():
                        dpg.add_text("Status:")
                        dpg.add_text("_", tag="StatusText")

                    with dpg.table_row():
                        dpg.add_text("Time:")
                        dpg.add_text("_s", tag="TimeStatus")

                    with dpg.table_row():
                        dpg.add_text("Frame:")
                        dpg.add_text("_", tag="FrameStatus")
            
            
            with dpg.collapsing_header(label="Camera Control", default_open=True):
    
                dpg.add_slider_float(tag="ZoomSlider", label="Zoom", min_value=0.1, max_value=100, default_value=self.zoom,callback=self.set_offset_zoom)            
                with dpg.group():
                    dpg.add_slider_float(tag="OffsetXSlider", label="X Offset", min_value=-100, max_value=100, default_value=self.offset[0], callback=self.set_offset_zoom)
                    dpg.add_slider_float(tag="OffsetYSlider", label="Y Offset", min_value=-100, max_value=100, default_value=self.offset[1], callback=self.set_offset_zoom)

            with dpg.collapsing_header(label="Vehicle Info", default_open=True, tag="VehicleInfoHeader"):
                with dpg.table(header_row=False):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    
                    with dpg.table_row():
                        dpg.add_text("Selected Vehicle:")
                        dpg.add_text("None", tag="SelectedVehicleText")

                    with dpg.table_row():
                        dpg.add_text("Speed:")
                        dpg.add_text("_ m/s", tag="VehicleSpeedText")

                    with dpg.table_row():
                        dpg.add_text("Position:")
                        dpg.add_text("_ m", tag="VehiclePositionText")

                    with dpg.table_row():
                        dpg.add_text("Lane:")
                        dpg.add_text("_", tag="VehicleLaneText")

                    with dpg.table_row():
                        dpg.add_text("Acceleration:")
                        dpg.add_text("_ m/s²", tag="VehicleAccelerationText")

            with dpg.collapsing_header(label="All Vehicles", default_open=True):
                dpg.add_text("Vehicle List:", tag="VehicleListText")
                with dpg.table(tag="VehicleTable", header_row=True):
                    dpg.add_table_column(label="ID")
                    dpg.add_table_column(label="Speed")
                    dpg.add_table_column(label="Position")
                    
                    # We'll update the table contents in the render loop
                    dpg.add_table_row(tag="VehicleTableRowTemplate")

    def resize_windows(self):
        width = dpg.get_viewport_width()
        height = dpg.get_viewport_height()

        dpg.set_item_width("ControlsWindow", 300)
        dpg.set_item_height("ControlsWindow", height-38)
        dpg.set_item_pos("ControlsWindow", (0, 0))

        dpg.set_item_width("MainWindow", width-315)
        dpg.set_item_height("MainWindow", height-38)
        dpg.set_item_pos("MainWindow", (300, 0))

    def create_handlers(self):
        with dpg.handler_registry():
            dpg.add_mouse_down_handler(callback=self.mouse_down)
            dpg.add_mouse_drag_handler(callback=self.mouse_drag)
            dpg.add_mouse_release_handler(callback=self.mouse_release)
            dpg.add_mouse_wheel_handler(callback=self.mouse_wheel)
        dpg.set_viewport_resize_callback(self.resize_windows)

    def update_panels(self):
        # Update status text
        if self.is_running:
            dpg.set_value("StatusText", "Running")
            dpg.configure_item("StatusText", color=(0, 255, 0))
        else:
            dpg.set_value("StatusText", "Stopped")
            dpg.configure_item("StatusText", color=(255, 0, 0))
        
        # Update time and frame text
        dpg.set_value("TimeStatus", f"{self.simulation.t:.2f}s")
        dpg.set_value("FrameStatus", self.simulation.frame_count)

        


    def mouse_down(self):
        if not self.is_dragging:
            if dpg.is_item_hovered("MainWindow"):
                # Check for vehicle selection
                mouse_pos = dpg.get_mouse_pos()
                world_pos = self.to_world(mouse_pos[0], mouse_pos[1])
                
                # Reset selection
                self.selected_vehicle = None
                
                # Check each vehicle
                for segment in self.simulation.segments:
                    for lane in range(segment.num_lanes):
                        for vehicle_id in segment.get_vehicles_in_lane(lane):
                            vehicle = self.simulation.vehicles[vehicle_id]
                            
                            # Get vehicle position
                            x, y = segment.get_point(vehicle.x/segment.get_length())
                            heading = segment.get_heading(vehicle.x/segment.get_length())
                            
                            # Calculate lane offset
                            lane_offset = (lane - (segment.num_lanes-1)/2) * 3.5
                            x += lane_offset * np.cos(heading + np.pi/2)
                            y += lane_offset * np.sin(heading + np.pi/2)
                            
                            # Check if click is within vehicle bounds
                            dx = world_pos[0] - x
                            dy = world_pos[1] - y
                            if abs(dx) < vehicle.l/2 and abs(dy) < vehicle.l/4:
                                self.selected_vehicle = vehicle_id
                                break
                        if self.selected_vehicle is not None:
                            break
                    if self.selected_vehicle is not None:
                        break
                
                self.is_dragging = True
                self.old_offset = self.offset
        
    def mouse_drag(self, sender, app_data):
        if self.is_dragging:
            self.offset = (
                self.old_offset[0] + app_data[1]/self.zoom,
                self.old_offset[1] + app_data[2]/self.zoom
            )

    def mouse_release(self):
        self.is_dragging = False

    def mouse_wheel(self, sender, app_data):
        if dpg.is_item_hovered("MainWindow"):
            self.zoom_speed = 1 + 0.01*app_data

    def update_inertial_zoom(self, clip=0.005):
        if self.zoom_speed != 1:
            self.zoom *= self.zoom_speed
            self.zoom_speed = 1 + (self.zoom_speed - 1) / 1.05
        if abs(self.zoom_speed - 1) < clip:
            self.zoom_speed = 1

    def update_offset_zoom_slider(self):
        dpg.set_value("ZoomSlider", self.zoom)
        dpg.set_value("OffsetXSlider", self.offset[0])
        dpg.set_value("OffsetYSlider", self.offset[1])

    def set_offset_zoom(self):
        self.zoom = dpg.get_value("ZoomSlider")
        self.offset = (dpg.get_value("OffsetXSlider"), dpg.get_value("OffsetYSlider"))

    def set_speed(self):
        self.speed = dpg.get_value("SpeedInput")


    def to_screen(self, x, y):
        return (
            self.canvas_width/2 + (x + self.offset[0] ) * self.zoom,
            self.canvas_height/2 + (y + self.offset[1]) * self.zoom
        )

    def to_world(self, x, y):
        return (
            (x - self.canvas_width/2) / self.zoom - self.offset[0],
            (y - self.canvas_height/2) / self.zoom - self.offset[1] 
        )
    
    @property
    def canvas_width(self):
        return dpg.get_item_width("MainWindow")

    @property
    def canvas_height(self):
        return dpg.get_item_height("MainWindow")


    def draw_bg(self, color=(250, 250, 250)):
        dpg.draw_rectangle(
            (0, 0),
            (self.canvas_width, self.canvas_height), 
            thickness=0,
            fill=color,
            parent="OverlayCanvas"
        )

    def draw_axes(self, opacity=80):
        x_center, y_center = self.to_screen(0, 0)
        
        dpg.draw_line(
            (0, y_center),
            (self.canvas_width, y_center),
            thickness=2, 
            color=(0, 0, 0, opacity),
            parent="OverlayCanvas"
        )
        dpg.draw_line(
            (x_center, 0),
            (x_center, self.canvas_height),
            thickness=2,
            color=(0, 0, 0, opacity),
            parent="OverlayCanvas"
        )

    def draw_grid(self, unit=10, opacity=50):
        x_start, y_start = self.to_world(0, 0)
        x_end, y_end = self.to_world(self.canvas_width, self.canvas_height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit)+1
        m_y = int(y_end / unit)+1

        for i in range(n_x, m_x):
            dpg.draw_line(
                self.to_screen(unit*i, y_start),
                self.to_screen(unit*i, y_end),
                thickness=1,
                color=(0, 0, 0, opacity),
                parent="OverlayCanvas"
            )
        for i in range(n_y, m_y):
            dpg.draw_line(
                self.to_screen(x_start, unit*i),
                self.to_screen(x_end, unit*i),
                thickness=1,
                color=(0, 0, 0, opacity),
                parent="OverlayCanvas"
            )

    def draw_segments(self):
        for segment in self.simulation.segments:
            # Calculate total road width
            total_width = segment.num_lanes * 3.5  # 3.5m per lane
            
            # Draw road edges
            for side in [-1, 1]:  # -1 for left edge, 1 for right edge
                edge_points = []
                for point in segment.points:
                    x, y = point
                    heading = segment.get_heading(segment.points.index(point)/(len(segment.points)-1))
                    # Offset by half the total width
                    x += side * (total_width/2) * np.cos(heading + np.pi/2)
                    y += side * (total_width/2) * np.sin(heading + np.pi/2)
                    edge_points.append(self.to_screen(x, y))
                dpg.draw_polyline(edge_points, color=(100, 100, 100), thickness=2, parent="Canvas")
            
            # Draw lane markers
            for lane in range(segment.num_lanes - 1):
                lane_offset = (lane + 0.5 - (segment.num_lanes-1)/2) * 3.5
                lane_points = []
                for point in segment.points:
                    x, y = point
                    heading = segment.get_heading(segment.points.index(point)/(len(segment.points)-1))
                    x += lane_offset * np.cos(heading + np.pi/2)
                    y += lane_offset * np.sin(heading + np.pi/2)
                    lane_points.append(self.to_screen(x, y))
                # Draw dashed lane markers
                for i in range(len(lane_points)-1):
                    if i % 2 == 0:  # Only draw every other segment for dashed effect
                        dpg.draw_line(
                            lane_points[i],
                            lane_points[i+1],
                            color=(255, 255, 0),
                            thickness=1,
                            parent="Canvas"
                        )

    def get_vehicle_color(self, vehicle_id):
        if vehicle_id not in self.vehicle_colors:
            # Generate a unique color using HSV color space
            hue = (len(self.vehicle_colors) * 0.618033988749895) % 1.0
            saturation = 0.8
            value = 0.9
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            self.vehicle_colors[vehicle_id] = (int(r * 255), int(g * 255), int(b * 255))
        return self.vehicle_colors[vehicle_id]

    def draw_vehicles(self):
        for segment in self.simulation.segments:
            for lane in range(segment.num_lanes):
                for vehicle_id in segment.get_vehicles_in_lane(lane):
                    vehicle = self.simulation.vehicles[vehicle_id]
                    
                    # Get vehicle position and heading
                    x, y = segment.get_point(vehicle.x/segment.get_length())
                    heading = segment.get_heading(vehicle.x/segment.get_length())
                    
                    # Calculate vehicle corners
                    l = vehicle.l
                    w = l/2
                    
                    # Calculate lane offset
                    lane_offset = (lane - (segment.num_lanes-1)/2) * 3.5
                    
                    # Apply lane offset perpendicular to road direction
                    x += lane_offset * np.cos(heading + np.pi/2)
                    y += lane_offset * np.sin(heading + np.pi/2)
                    
                    # Calculate corners
                    corners = [
                        (x + l/2*np.cos(heading) + w/2*np.cos(heading + np.pi/2),
                         y + l/2*np.sin(heading) + w/2*np.sin(heading + np.pi/2)),
                        (x + l/2*np.cos(heading) - w/2*np.cos(heading + np.pi/2),
                         y + l/2*np.sin(heading) - w/2*np.sin(heading + np.pi/2)),
                        (x - l/2*np.cos(heading) - w/2*np.cos(heading + np.pi/2),
                         y - l/2*np.sin(heading) - w/2*np.sin(heading + np.pi/2)),
                        (x - l/2*np.cos(heading) + w/2*np.cos(heading + np.pi/2),
                         y - l/2*np.sin(heading) + w/2*np.sin(heading + np.pi/2))
                    ]
                    
                    # Get vehicle color
                    color = self.get_vehicle_color(vehicle_id)
                    if vehicle_id == self.selected_vehicle:
                        # Make selected vehicle brighter
                        color = tuple(min(255, c + 50) for c in color)
                    
                    # Draw vehicle
                    dpg.draw_polygon(
                        [self.to_screen(*corner) for corner in corners],
                        fill=color,
                        parent="Canvas"
                    )
                    
                    # Draw vehicle info above the vehicle
                    info_pos = self.to_screen(x, y - l)
                    dpg.draw_text(
                        info_pos,
                        f"V{vehicle_id} - {vehicle.v:.1f}m/s",
                        color=(0, 0, 0),
                        size=12,
                        parent="Canvas"
                    )

    def apply_transformation(self):
        screen_center = dpg.create_translation_matrix([self.canvas_width/2, self.canvas_height/2, -0.01])
        translate = dpg.create_translation_matrix(self.offset)
        scale = dpg.create_scale_matrix([self.zoom, self.zoom])
        dpg.apply_transform("Canvas", screen_center*scale*translate)

    def update_vehicle_info(self):
        if self.selected_vehicle is not None:
            vehicle = self.simulation.vehicles[self.selected_vehicle]
            dpg.set_value("SelectedVehicleText", f"Vehicle {self.selected_vehicle}")
            dpg.set_value("VehicleSpeedText", f"{vehicle.v:.2f} m/s")
            dpg.set_value("VehiclePositionText", f"{vehicle.x:.2f} m")
            dpg.set_value("VehicleLaneText", f"Lane {vehicle.lane}")
            dpg.set_value("VehicleAccelerationText", f"{vehicle.a:.2f} m/s²")
        else:
            dpg.set_value("SelectedVehicleText", "None")
            dpg.set_value("VehicleSpeedText", "_ m/s")
            dpg.set_value("VehiclePositionText", "_ m")
            dpg.set_value("VehicleLaneText", "_")
            dpg.set_value("VehicleAccelerationText", "_ m/s²")

        # Update vehicle list
        vehicle_list = []
        for segment in self.simulation.segments:
            for lane in range(segment.num_lanes):
                for vehicle_id in segment.get_vehicles_in_lane(lane):
                    vehicle = self.simulation.vehicles[vehicle_id]
                    color = self.get_vehicle_color(vehicle_id)
                    vehicle_list.append(f"Vehicle {vehicle_id} - Lane {vehicle.lane} - Speed: {vehicle.v:.2f} m/s")
        
        dpg.set_value("VehicleListText", "\n".join(vehicle_list))

    def update_vehicle_list(self):
        """Update the vehicle list table with current vehicle information"""
        # Get all active vehicle IDs (vehicles that are in segments)
        active_vehicle_ids = set()
        for segment in self.simulation.segments:
            for lane in range(segment.num_lanes):
                active_vehicle_ids.update(segment.get_vehicles_in_lane(lane))
        
        # Remove rows for vehicles that are no longer active
        for item in dpg.get_item_children("VehicleTable", slot=1):
            if item != "VehicleTableRowTemplate":
                # Get the row's tag
                row_tag = dpg.get_item_alias(item)
                if row_tag and row_tag.startswith("VehicleRow_"):
                    try:
                        vehicle_id = int(row_tag.split('_')[1])
                        if vehicle_id not in active_vehicle_ids:
                            dpg.delete_item(item)
                    except (IndexError, ValueError):
                        continue
        
        # Add or update rows for active vehicles
        for vehicle_id in active_vehicle_ids:
            vehicle = self.simulation.vehicles[vehicle_id]
            row_tag = f"VehicleRow_{vehicle_id}"
            
            # Check if row already exists
            if not dpg.does_item_exist(row_tag):
                # Create new row
                with dpg.table_row(parent="VehicleTable", tag=row_tag):
                    dpg.add_button(
                        label=f"Vehicle {vehicle_id}",
                        callback=lambda s, a, u: self.select_vehicle(u),
                        user_data=vehicle_id,
                        width=-1
                    )
                    dpg.add_text(f"{vehicle.v:.1f} m/s")
                    dpg.add_text(f"{vehicle.x:.1f} m")
            else:
                # Update existing row
                row_children = dpg.get_item_children(row_tag, slot=1)
                if len(row_children) >= 3:
                    dpg.set_value(row_children[1], f"{vehicle.v:.1f} m/s")
                    dpg.set_value(row_children[2], f"{vehicle.x:.1f} m")

    def render_loop(self):
        # Events
        self.update_panels()
        self.update_vehicle_info()
        self.update_vehicle_list()
        self.update_inertial_zoom()
        self.update_offset_zoom_slider()

        # Clear canvas
        dpg.delete_item("Canvas", children_only=True)
        dpg.delete_item("OverlayCanvas", children_only=True)

        # Draw
        self.draw_bg()
        self.draw_grid()
        self.draw_axes()
        self.draw_segments()
        self.draw_vehicles()

        # Update
        if self.is_running:
            for _ in range(self.speed):
                self.simulation.update()

    def show(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            self.render_loop()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

    def run(self):
        self.is_running = True
        dpg.configure_item("RunStopButton", label="Stop")
        dpg.bind_item_theme("RunStopButton", "StopButtonTheme")

    def stop(self):
        self.is_running = False
        dpg.configure_item("RunStopButton", label="Run")
        dpg.bind_item_theme("RunStopButton", "RunButtonTheme")

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.run()

    def select_vehicle(self, vehicle_id):
        """Select a vehicle and center the view on it"""
        self.selected_vehicle = vehicle_id
        # Find the vehicle's position
        for segment in self.simulation.segments:
            for lane in range(segment.num_lanes):
                if vehicle_id in segment.get_vehicles_in_lane(lane):
                    vehicle = self.simulation.vehicles[vehicle_id]
                    x, y = segment.get_point(vehicle.x/segment.get_length())
                    heading = segment.get_heading(vehicle.x/segment.get_length())
                    
                    # Calculate lane offset
                    lane_offset = (lane - (segment.num_lanes-1)/2) * 3.5
                    x += lane_offset * np.cos(heading + np.pi/2)
                    y += lane_offset * np.sin(heading + np.pi/2)
                    
                    # Center the view on the vehicle
                    self.offset = (-x, -y)
                    self.update_offset_zoom_slider()
                    return
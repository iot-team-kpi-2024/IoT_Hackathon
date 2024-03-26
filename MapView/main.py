import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch
from kivy.uix.image import Image
from kivy.clock import Clock
from wind_arrow import WindArrow
from lineMapLayer import LineMapLayer
from temperatureMapLayer import TemperatureMapLayer
from datasource import Datasource
import queue

class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self._datasource = Datasource(user_id=1)
        self._process_queue = queue.Queue()

        self.road_markers = []
        self.wind_markers = []

        self.road_markers_visible = True
        self.wind_markers_visible = True

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        for point in self._datasource.get_new_points():
            self._process_queue.put(point)

        if not self._process_queue.qsize() == 0:
            point = self._process_queue.get()
            coordinates = (point[0], point[1])
            self.lines_layer.add_point(coordinates)
            self.update_car_marker(coordinates)
            self.check_road_quality(coordinates, point[2])
            self.check_humidex_state(coordinates, point[3])
            self.check_anemometer_state(coordinates, point[4], point[5])

    def check_road_quality(self, coordinates, state):
        """
        Аналізує дані акселерометра для подальшого визначення
        та відображення ям та лежачих поліцейських
        """
        if state == "bump":
            self.set_bump_marker(coordinates)
        elif state == "pothole":
            self.set_pothole_marker(coordinates)

    def check_humidex_state(self, coordinates, state):
        if state == "dangerous":
            self.set_humidex_marker(coordinates, [1, 0, 0, 1])
        elif state == "great discomfort":
            self.set_humidex_marker(coordinates, [1, 0.5, 0, 1])
        elif state == "some discomfort":
            self.set_humidex_marker(coordinates, [0, 1, 0, 1])
        elif state == "comfortable":
            self.set_humidex_marker(coordinates, [0, 0, 1, 1])
        else:
            self.set_humidex_marker(coordinates, [0, 0, 1, 1])

    def check_anemometer_state(self, point, state, direction):
        self.wind_direction.rotation_angle = direction

        marker = None

        if state == "strong wind":
            marker = MapMarker(lat=point[0], lon=point[1], source="images/wind.png")
        elif state == "strong chill wind":
            marker = MapMarker(lat=point[0], lon=point[1], source="images/wind.png")

        if marker:
            self.wind_markers.append(marker)
            if self.wind_markers_visible:
                self.mapview.add_widget(marker)

    def update_car_marker(self, coordnates):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.car_marker.lat = coordnates[0]
        self.car_marker.lon = coordnates[1]

        # Force redraw
        self.mapview.remove_widget(self.car_marker)
        self.mapview.add_widget(self.car_marker)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        pothole_marker = MapMarker(lat=point[0], lon=point[1], source="images/pothole.png")
        self.road_markers.append(pothole_marker)

        if self.road_markers_visible:
            self.mapview.add_widget(pothole_marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        bump_marker = MapMarker(lat=point[0], lon=point[1], source="images/bump.png")
        self.road_markers.append(bump_marker)

        if self.road_markers_visible:
            self.mapview.add_widget(bump_marker)

    def set_humidex_marker(self, point, color):
        self.humidex_layer.add_point(point, color)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.main_layout = FloatLayout()

        self.mapview = MapView()

        self.wind_direction = WindArrow(source="images/arrow.png",
                                        size_hint=(None, None),
                                        pos_hint={'x': 0, 'top': 1},
                                        allow_stretch=True,
                                        keep_ratio=True)

        self.lines_layer = LineMapLayer()
        self.mapview.add_layer(self.lines_layer, mode="scatter")

        self.humidex_layer = TemperatureMapLayer()
        self.mapview.add_layer(self.humidex_layer, mode="scatter")

        self.car_marker = MapMarker(lat=0, lon=0, source="images/car.png")
        self.mapview.add_widget(self.car_marker)

        road_switch = Switch(active=True)
        road_switch.bind(active=self.on_road_switch)
        road_switch_layout = BoxLayout(orientation='horizontal')
        road_switch_layout.add_widget(Image(source="images/bump.png"))
        road_switch_layout.add_widget(road_switch)

        humidex_switch = Switch(active=True)
        humidex_switch.bind(active=self.on_humidex_switch)
        humidex_switch_layout = BoxLayout(orientation='horizontal')
        humidex_switch_layout.add_widget(Image(source="images/temperature.png"))
        humidex_switch_layout.add_widget(humidex_switch)

        wind_switch = Switch(active=True)
        wind_switch.bind(active=self.on_wind_switch)
        wind_switch_layout = BoxLayout(orientation='horizontal')
        wind_switch_layout.add_widget(Image(source="images/wind.png"))
        wind_switch_layout.add_widget(wind_switch)

        self.main_layout.add_widget(self.mapview)

        swiches_layout = BoxLayout(size_hint=(0.2, 0.2), pos_hint={'right': 1, 'top': 1}, orientation='vertical', spacing=5)
        swiches_layout.add_widget(road_switch_layout)
        swiches_layout.add_widget(humidex_switch_layout)
        swiches_layout.add_widget(wind_switch_layout)

        self.main_layout.add_widget(swiches_layout)
        self.main_layout.add_widget(self.wind_direction)

        return self.main_layout
    
    def on_road_switch(self, instance, value):
        self.road_markers_visible = value

        if value:
            for marker in self.road_markers:
                self.mapview.add_widget(marker)
        else:
            for marker in self.road_markers:
                self.mapview.remove_widget(marker)
    
    def on_humidex_switch(self, instance, value):
        if value:
            self.mapview.add_layer(self.humidex_layer, mode="scatter")
        else:
            self.mapview.remove_layer(self.humidex_layer)

    def on_wind_switch(self, instance, value):
        self.wind_markers_visible = value

        if value:
            for marker in self.wind_markers:
                self.mapview.add_widget(marker)
        else:
            for marker in self.wind_markers:
                self.mapview.remove_widget(marker)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()

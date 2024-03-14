import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource
from functools import partial

class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self._datasource = Datasource(user_id=1)

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        new_points = self._datasource.get_new_points()
        for idx, point in enumerate(new_points):
            Clock.schedule_once(partial(self.update_couroutine, point), idx * 0.1)

    def update_couroutine(self, point, *args):
        coordinates = (point[0], point[1])
        self.lines_layer.add_point(coordinates)
        self.update_car_marker(coordinates)
        self.check_road_quality(point)

    def check_road_quality(self, point):
        """
        Аналізує дані акселерометра для подальшого визначення
        та відображення ям та лежачих поліцейських
        """
        state = point[2]
        if state == "bump":
            self.set_bump_marker((point[0], point[1]))
        elif state == "pothole":
            self.set_pothole_marker((point[0], point[1]))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.car_marker.lat = point[0]
        self.car_marker.lon = point[1]

        # Force redraw
        self.mapview.remove_widget(self.car_marker)
        self.mapview.add_widget(self.car_marker)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """
        pothole_marker = MapMarker(lat=point[0], lon=point[1], source="images/pothole.png")
        self.pothole_markers.append(pothole_marker)
        self.mapview.add_widget(pothole_marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """
        bump_marker = MapMarker(lat=point[0], lon=point[1], source="images/bump.png")
        self.bump_markers.append(bump_marker)
        self.mapview.add_widget(bump_marker)

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.mapview = MapView()

        self.lines_layer = LineMapLayer()
        self.mapview.add_layer(self.lines_layer, mode="scatter")

        self.car_marker = MapMarker(lat=0, lon=0, source="images/car.png")
        self.mapview.add_widget(self.car_marker)

        self.pothole_markers = []
        self.bump_markers = []

        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()

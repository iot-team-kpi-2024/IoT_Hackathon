from enum import Enum
from csv import DictReader
from datetime import datetime
from marshmallow import Schema
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema
from schema.humidex_schema import HumidexSchema
from schema.anemometer_schema import AnemometerSchema
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.humidex import Humidex
from domain.anemometer import Anemometer
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    class DataKeys(Enum):
        ACCELEROMETER = 0
        GPS = 1
        HUMIDEX = 2
        ANEMOMETER = 3

    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        humidex_filename: str,
        anemometer_filename: str
    ) -> None:
        self.readers = [None] * len(FileDatasource.DataKeys)
        self.readers[FileDatasource.DataKeys.ACCELEROMETER.value] = DatasourceReader(accelerometer_filename, AccelerometerSchema())
        self.readers[FileDatasource.DataKeys.GPS.value] = DatasourceReader(gps_filename, GpsSchema())
        self.readers[FileDatasource.DataKeys.HUMIDEX.value] = DatasourceReader(humidex_filename, HumidexSchema())
        self.readers[FileDatasource.DataKeys.ANEMOMETER.value] = DatasourceReader(anemometer_filename, AnemometerSchema())

    def read(self, batch_size) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""
        for reader in self.readers:
            if not reader.reader:
                raise Exception("CSV Readers not initialized. Call startReading first.")
        
        result = [None] * batch_size

        try:
            for i in range(batch_size):
                accelerometer = Accelerometer(**self.readers[FileDatasource.DataKeys.ACCELEROMETER.value].read())
                gps = Gps(**self.readers[FileDatasource.DataKeys.GPS.value].read())
                humidex = Humidex(**self.readers[FileDatasource.DataKeys.HUMIDEX.value].read())
                anemometer = Anemometer(**self.readers[FileDatasource.DataKeys.ANEMOMETER.value].read())

                result[i] = AggregatedData(accelerometer, gps, humidex, anemometer, datetime.now(), config.USER_ID)

            return result
        except Exception as err:
            print(f"Validation error: {err}")
            return []

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        for reader in self.readers:
            reader.startReading()

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        for reader in self.readers:
            reader.stopReading()

class DatasourceReader:
    filename: str
    reader: DictReader

    def __init__(self, filename, schema: Schema):
        self.filename = filename
        self.schema = schema

    def startReading(self):
        self.file = open(self.filename, 'r')
        self.reader = DictReader(self.file)
    
    def read(self):
        row = next(self.reader, None)

        if row is None:
            self.reset()
            row = next(self.reader, None)

        return self.schema.load(row)
    
    def reset(self):
        self.file.seek(0)
        self.reader = DictReader(self.file)
    
    def stopReading(self):
        if self.file:
            self.file.close()
from csv import DictReader
from enum import Enum
from datetime import datetime
from marshmallow import Schema
from schemas import *

class FileDatasource:
    class DataKeys(Enum):
        ACCELEROMETER = 0
        GPS = 1

    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.readers = [None] * len(FileDatasource.DataKeys)
        self.readers[FileDatasource.DataKeys.ACCELEROMETER.value] = DatasourceReader(accelerometer_filename, AccelerometerSchema())
        self.readers[FileDatasource.DataKeys.GPS.value] = DatasourceReader(gps_filename, GpsSchema()) 

    def read(self, count: int = 1) -> list[AggregatedData]:
        for reader in self.readers:
            if not reader.reader:
                raise Exception("CSV Readers not initialized. Call startReading first.")
        
        result = [None] * count

        try:
            for i in range(count):
                accelerometer = self.readers[FileDatasource.DataKeys.ACCELEROMETER.value].read()
                gps = self.readers[FileDatasource.DataKeys.GPS.value].read()

                timestamp = datetime.now()
                result[i] = AggregatedData(Accelerometer(**accelerometer), Gps(**gps), timestamp)
            
            return result
        except Exception as err:
            print(f"Validation error: {err}")
            return result

    def startReading(self, *args, **kwargs):
        for reader in self.readers:
            reader.startReading()

    def stopReading(self, *args, **kwargs):
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
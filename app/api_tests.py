import unittest
from api import get_stations, get_status


class ApiTestCase(unittest.TestCase):

    def test_get_station_information(self):
        station_names_ids = get_stations()
        self.assertIsInstance(station_names_ids, dict)
        self.assertTrue(len(station_names_ids) > 0)

    def test_get_station_status(self):
        station_bikes_locks = get_status()
        self.assertIsInstance(station_bikes_locks, dict)
        self.assertTrue(len(station_bikes_locks) > 0)


if __name__ == '__main__':
    unittest.main()

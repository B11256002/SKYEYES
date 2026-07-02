import unittest

from boundary.manager import BoundaryManager


class BoundaryManagerTest(unittest.TestCase):

    def test_contains_point_inside_polygon(self):
        boundary = BoundaryManager([
            (0, 0),
            (100, 0),
            (100, 100),
            (0, 100),
        ])

        self.assertTrue(boundary.contains((50, 50)))

    def test_rejects_point_outside_polygon(self):
        boundary = BoundaryManager([
            (0, 0),
            (100, 0),
            (100, 100),
            (0, 100),
        ])

        self.assertFalse(boundary.contains((150, 50)))


if __name__ == "__main__":
    unittest.main()

"""Tests : python3 -m unittest test_core -v  (nécessite opencv et la vidéo d'exemple)."""
import math
import os
import tempfile
import unittest

from core import Calibration, Session, open_video, read_frame

SAMPLE = os.environ.get("AVIMECA_SAMPLE", "")


class TestCalibration(unittest.TestCase):
    def test_scale(self):
        c = Calibration((0, 0), (300, 400), 2.5)  # 500 px -> 2.5 m
        self.assertAlmostEqual(c.m_per_px, 0.005)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            Calibration((1, 1), (1, 1), 1.0).m_per_px
        with self.assertRaises(ValueError):
            Calibration((0, 0), (1, 0), 0).m_per_px


class TestSession(unittest.TestCase):
    def setUp(self):
        self.s = Session(fps=10, width=100, height=50, n_frames=20,
                         calibration=Calibration((0, 0), (10, 0), 1.0))  # 0.1 m/px

    def test_origin_bottom_left_y_up(self):
        x, y = self.s.to_physical(0, 50)
        self.assertEqual((x, y), (0, 0))
        x, y = self.s.to_physical(10, 40)  # 10 px right, 10 px up
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(y, 1.0)

    def test_custom_origin(self):
        self.s.origin_px = (50, 25)
        x, y = self.s.to_physical(50, 25)
        self.assertEqual((x, y), (0, 0))

    def test_rows_and_delete(self):
        self.s.set_point(1, 0, 0, 50)
        self.s.set_point(1, 10, 10, 50)
        self.s.set_point(1, 5, 5, 50)
        rows = self.s.rows(1)
        self.assertEqual([round(r[0], 3) for r in rows], [0.0, 0.5, 1.0])  # trié, t = frame/fps
        self.s.delete_point(1, 5)
        self.assertEqual(len(self.s.rows(1)), 2)

    def test_export(self):
        self.s.set_point(1, 0, 0, 50)
        self.s.set_point(1, 1, 10, 50)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "piste.txt")
            self.assertEqual(self.s.export_track(1, p), 2)
            lines = open(p, encoding="utf-8").read().splitlines()
        self.assertEqual(lines[0], "t(s)\tx(m)\ty(m)")
        self.assertEqual(lines[2].split("\t")[1], "1.00000")  # 10 px * 0.1 m/px

    def test_no_calibration(self):
        s = Session(fps=10, width=1, height=1, n_frames=1)
        with self.assertRaises(ValueError):
            s.to_physical(0, 0)


@unittest.skipUnless(SAMPLE and os.path.exists(SAMPLE), "vidéo d'exemple absente (AVIMECA_SAMPLE)")
class TestVideo(unittest.TestCase):
    def test_open_and_read(self):
        cap, s = open_video(SAMPLE)
        self.assertEqual((s.width, s.height), (1200, 900))
        self.assertAlmostEqual(s.fps, 17.0, places=2)
        self.assertGreater(s.n_frames, 0)
        frame = read_frame(cap, 0)
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape[:2], (900, 1200))
        cap.release()


if __name__ == "__main__":
    unittest.main()

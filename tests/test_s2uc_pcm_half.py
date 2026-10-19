import struct
import unittest
from tools.s2uc_pcm_half_check import half_payload,band_comparison


class PCMHalfTests(unittest.TestCase):
    def test_roundtrip_and_signed_zero(self):
        values=[0.,-0.,.25,-.5]*1200
        half,info=half_payload(struct.pack('<4800f',*values))
        self.assertIsNotNone(half)
        self.assertTrue(info['roundtrip_bit_equal'])
        self.assertEqual(struct.unpack('<4f',half[:16]),(0.,-0.,.125,-.25))

    def test_underflow_no_processing_payload(self):
        half,info=half_payload(struct.pack('<4800f',*([2.**-149]*4800)))
        self.assertIsNone(half)
        self.assertEqual(len(info['underflow_indices']),4800)

    def test_invalid_domain_and_length(self):
        self.assertIsNone(half_payload(b'bad')[0])
        self.assertIsNone(half_payload(struct.pack('<4800f',*([float('nan')]*4800)))[0])
        self.assertIsNone(half_payload(struct.pack('<4800f',*([2.]*4800)))[0])

    def test_numeric_vs_bit_equality(self):
        r=band_comparison(0.,-0.)
        self.assertTrue(r['numeric_equal'])
        self.assertFalse(r['bit_equal'])
        self.assertEqual(r['ulp_distance'],1)

    def test_nonzero_deviation_not_tolerated(self):
        import math
        r=band_comparison(1.,math.nextafter(.5,1.))
        self.assertFalse(r['numeric_equal'])
        self.assertFalse(r['bit_equal'])
        self.assertEqual(r['ulp_distance'],1)


if __name__=='__main__':unittest.main()

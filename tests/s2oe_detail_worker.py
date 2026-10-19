"""Native neutral frames in the existing worker; never opens a media file."""
from fractions import Fraction
from tools import _s2oe_fixed_detail as d


class Neutral(d.DetailDecoder):
    def begin_video(self):
        frames=[]
        for pts in (0,1001,2002):
            f=self.av.VideoFrame(3840,2160,'yuv420p')
            f.pts=pts;f.time_base=Fraction(1,30000);f.colorspace=f.color_range=1
            for plane in f.planes:plane.update(bytes([128])*plane.buffer_size)
            frames.append(f)
        self.vi=iter(frames);self.video_last_time=None
        self.counters['passes']=1


if __name__=='__main__':d.worker.worker_main(Neutral)

"""Read-only runtime binding generator; never opens a media container."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
    import numpy
    from tools._s2oe_media_decoder import load_av
    from tools import _s2nj_private_auditory_output_projection as nj
    from tools import s2uc_pcm_half_check,s2uc_audio_worker,_s2uc_bounded_audio
    av=load_av()
    paths=set()
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.is_file() and (p.is_relative_to(ROOT) or p.suffix in ('.pyd','.dll')):paths.add(p)
    for folder in [Path(av.__file__).parent,Path(av.__file__).parent.parent/'av.libs',Path(numpy.__file__).parent,Path(numpy.__file__).parent.parent/'numpy.libs']:
        if folder.exists():
            paths.update(p.resolve() for p in folder.rglob('*') if p.suffix in ('.pyd','.dll','.py'))
    paths.add(Path(sys.executable).resolve())
    paths.update(Path(sys.base_prefix).glob('*.dll'))
    result=dict(version='s2uc.bounded-audio.binding.v1',python=sys.version,pyav=av.__version__,ffmpeg=av.library_versions,
        numpy=numpy.__version__,raw_profile_digest=nj.RAW_PROFILE_DIGEST,nj_profile_digest=nj.PROFILE_DIGEST,
        source=dict(path=_s2uc_bounded_audio.SOURCE,size=_s2uc_bounded_audio.SOURCE_SIZE,sha256=_s2uc_bounded_audio.SOURCE_SHA),
        files=[dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)])
    path=ROOT/'docs/S2UC_AUDIO_READER_BINDING_20260930.json'
    path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Bound',len(paths),'files; manifest',path.stat().st_size,'bytes')
if __name__=='__main__':build()

"""Download public model weights only. Never uploads a user's image."""
import urllib.request,json,hashlib
from pathlib import Path
root=Path(__file__).parent/'models';root.mkdir(exist_ok=True)
repository='https://huggingface.co/Acly/MobileSAM'
metadata=json.load(urllib.request.urlopen('https://huggingface.co/api/models/Acly/MobileSAM',timeout=30));revision=metadata['sha'];files=[]
for name in ['mobile_sam_image_encoder.onnx','sam_mask_decoder_single.onnx']:
    target=root/name;url=f'{repository}/resolve/{revision}/{name}'
    with urllib.request.urlopen(url,timeout=60) as response,target.open('wb') as output:
        while chunk:=response.read(1024*1024):output.write(chunk)
    files.append(dict(file=name,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),source=url))
    print(name,target.stat().st_size,flush=True)
(root/'model-manifest.json').write_text(json.dumps(dict(repository=repository,revision=revision,files=files),indent=2),encoding='utf-8')
urllib.request.urlretrieve('https://raw.githubusercontent.com/ChaoningZhang/MobileSAM/master/LICENSE',root/'MobileSAM-LICENSE.txt')

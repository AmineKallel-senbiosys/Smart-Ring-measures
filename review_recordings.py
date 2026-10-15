from pathlib import Path
import sys,subprocess,re
ROOT=Path(__file__).parent
sys.path[:0]=[str(ROOT/'.video-tools'),str(ROOT/'ring-sizing/.vision-tools')]
import imageio_ffmpeg
from PIL import Image,ImageDraw
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
out=ROOT/'record-review';out.mkdir(exist_ok=True)
for number,name in enumerate(['record.mp4','record 2.mp4'],1):
    source=Path('C:/Users/AmineKallel/Downloads')/name
    metadata=subprocess.run([ffmpeg,'-i',str(source)],capture_output=True,text=True).stderr
    match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',metadata)
    duration=int(match[1])*3600+int(match[2])*60+float(match[3])
    print(name,duration)
    sheet=Image.new('RGB',(4*240,2*460),'#ddd');draw=ImageDraw.Draw(sheet)
    for i in range(8):
        t=duration*(i+.5)/8;frame=out/f'record-{number}-frame-{i}.png'
        subprocess.run([ffmpeg,'-loglevel','error','-y','-ss',str(t),'-i',str(source),'-frames:v','1',str(frame)],check=True)
        im=Image.open(frame);im.thumbnail((240,435))
        x=(i%4)*240;y=(i//4)*460;sheet.paste(im,(x,y+25));draw.text((x+5,y+5),f'{number}: {t:.1f}s',fill='black')
    sheet.save(out/f'record-{number}-contact.jpg')

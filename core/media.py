import io
from PIL import Image, ImageDraw, ImageFont

class MediaEngine:
    @staticmethod
    async def apply_watermark(session, url, channel_name):
        if not url: return None
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            async with session.get(url, headers=headers, timeout=12) as resp:
                if resp.status != 200: return None
                img_data = await resp.read()
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            draw = ImageDraw.Draw(img); w, h = img.size
            try: font = ImageFont.truetype("arial.ttf", int(w/20))
            except: font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), channel_name, font=font)
            tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text((w-tw-28, h-th-28), channel_name, font=font, fill=(0,0,0))
            draw.text((w-tw-30, h-th-30), channel_name, font=font, fill=(255,255,255))
            out = io.BytesIO(); img.save(out, format="JPEG", quality=85); out.seek(0)
            return out
        except: return None
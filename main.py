import base64
import json
import io
import streamlit as st
from PIL import Image, ImageDraw
from groq import Groq
import config

st.set_page_config(page_title="X-ray Thingy", page_icon="🐥")
client=Groq(api_key="config.GROQ_API_KEY")
st.title("AI X-ray Vision")
st.write("Upload a photo to use it")
file=st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if st.button("Scan Image"):
    if not file:
        st.warning("Upload an image first")
    elif not config.GROQ_API_KEY:
        st.error("API key is missing")
    else:
        try:
            image=Image.open(file).convert("RGB")
            encoded=base64.b64encode(file.getvalue()).decode()
            prompt="""Dtect objects in this image.
            Return JSON only:
            {"scene_title":"title","objects":[
            {"name":"Bottle","box":{"x":20,"y":10,"w":25,"h":40}}]}
            Coordinates are percentages from 0 to 100."""
            response =client.chat.completions.create(
                model=config.GROQ_VISION_MODEL,
                messages=[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:{file.type};base64,{encoded}"}}
                        ]}],
                        response_format={"type":"json_onject"}

            )
            data =json.loads(response.choices[0].message.content)
            draw=ImageDraw.Draw(image)
            w,h=image.size
            
            for obj in data.get("objects", []):
                b = obj["box"]
                if isinstance(b, list):
                    x, y, bw, bh = b
                else:
                    x, y, bw, bh = b["x"], b["y"], b["w"], b["h"]

                x1, y1 = int(x*w/100), int(y*h/100)
                x2, y2 = int((x+bw)*w/100), int((y+bh)*h/100)
                draw.rectangle((x1, y1, x2, y2), outline="lime", width=3)
                draw.text((x1, max(0, y1-20)), obj["name"].upper(), fill="lime")
            st.success("Scan Complete!")
            st.write(data.get("scene_title", "Image Scan"))
            st.image(image)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            st.download_button("📥 Download Image", buffer.getvalue(),
            "scanner.png", "image/png")
        except Exception as e:
            st.error(str(e))
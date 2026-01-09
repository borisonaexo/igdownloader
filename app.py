import streamlit as st
import yt_dlp
import os
from pathlib import Path
import time

st.set_page_config(page_title="IG Reels Downloader", layout="wide")

st.title("📥 Instagram Reels Multiple Downloader")

st.warning("⚠️ Hanya download konten yang Anda punya izin. Patuhi ToS Instagram!")

# Create temp folder for downloads
temp_folder = "downloads"
os.makedirs(temp_folder, exist_ok=True)

# Input area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Masukkan URL Reels")
    urls_input = st.text_area(
        "Paste URL (satu per baris)",
        placeholder="https://www.instagram.com/reels/ABC123/\nhttps://www.instagram.com/reels/DEF456/",
        height=150,
        label_visibility="collapsed"
    )

with col2:
    st.subheader("📊 Info")
    urls_list = [url.strip() for url in urls_input.split('\n') if url.strip()]
    st.metric("Total URL", len(urls_list))

# Download button
if st.button("🚀 Mulai Download", type="primary", use_container_width=True):
    if not urls_list:
        st.error("❌ Masukkan minimal 1 URL!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        output_container = st.container()
        
        results = []
        
        for index, url in enumerate(urls_list):
            current = index + 1
            total = len(urls_list)
            
            status_text.info(f"⏳ [{current}/{total}] Downloading: {url}")
            
            try:
                # Setup yt-dlp options
                filename = f"reel_{int(time.time())}_{index}.mp4"
                filepath = os.path.join(temp_folder, filename)
                
                ydl_opts = {
                    'format': 'best[ext=mp4]',
                    'outtmpl': filepath.replace('.mp4', ''),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                
                results.append({
                    'status': '✅ Berhasil',
                    'url': url,
                    'file': filename
                })
                
                output_container.success(f"✅ [{current}/{total}] Download berhasil!")
                
            except Exception as e:
                results.append({
                    'status': '❌ Gagal',
                    'url': url,
                    'error': str(e)[:100]
                })
                output_container.error(f"❌ [{current}/{total}] Error: {str(e)[:100]}")
            
            # Update progress
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
        
        status_text.success("✅ Download Selesai!")
        
        # Show summary
        st.divider()
        col1, col2, col3 = st.columns(3)
        success_count = sum(1 for r in results if r['status'] == '✅ Berhasil')
        fail_count = sum(1 for r in results if r['status'] == '❌ Gagal')
        
        col1.metric("Berhasil", success_count)
        col2.metric("Gagal", fail_count)
        col3.metric("Total", len(results))
        
        # Download files
        st.subheader("📥 Download Files")
        files_in_folder = [f for f in os.listdir(temp_folder) if f.endswith('.mp4')]
        
        if files_in_folder:
            st.info(f"📁 {len(files_in_folder)} file tersedia untuk download")
            
            for file in files_in_folder[-len(results):]:
                filepath = os.path.join(temp_folder, file)
                with open(filepath, 'rb') as f:
                    st.download_button(
                        label=f"⬇️ {file}",
                        data=f.read(),
                        file_name=file,
                        mime="video/mp4"
                    )

st.divider()

# Info section
with st.expander("ℹ️ Cara Menggunakan", expanded=False):
    st.markdown("""
    ### Langkah-langkah:
    1. **Copy URL** dari Instagram Reels (tekan 3 titik → Copy Link)
    2. **Paste URL** di kotak input (bisa multiple)
    3. **Klik "Mulai Download"** dan tunggu proses selesai
    4. **Download file** dengan tombol yang muncul di bawah
    
    ### Tips:
    - Gunakan untuk konten pribadi atau yang punya izin
    - Satu reels = satu file MP4
    - File akan auto-delete setelah beberapa jam
    """)

with st.expander("⚠️ Disclaimer & Syarat", expanded=False):
    st.markdown("""
    - **Hanya untuk personal use** atau konten dengan izin
    - Patuhi Terms of Service Instagram
    - Patuhi hukum copyright & DMCA
    - Tool ini tidak bertanggung jawab atas penyalahgunaan
    - Instagram mungkin memblokir automated downloads
    """)
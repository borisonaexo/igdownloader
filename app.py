import streamlit as st
import subprocess
import os
import time
from pathlib import Path

st.set_page_config(page_title="IG Reels Downloader", layout="wide")

st.title("📥 Instagram Reels Multiple Downloader")

st.warning("⚠️ Hanya download konten yang Anda punya izin. Patuhi ToS Instagram!")

# Create temp folder
temp_folder = "downloads"
os.makedirs(temp_folder, exist_ok=True)

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Masukkan URL Reels")
    urls_input = st.text_area(
        "Paste URL (satu per baris) - Support /reel/, /reels/, /p/",
        placeholder="https://www.instagram.com/reel/DSpCM98EX-O/\nhttps://www.instagram.com/p/DSpCM98EX-O/",
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
                # Setup filename
                timestamp = int(time.time() * 1000)
                filename = f"reel_{timestamp}_{index}.mp4"
                filepath = os.path.join(temp_folder, filename)
                
                # Download menggunakan yt-dlp dengan custom cookies
                cmd = [
                    "yt-dlp",
                    url,
                    "-o", filepath,
                    "-f", "best[ext=mp4]",
                    "--quiet",
                    "-N", "1",  # Limit connections
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0 and os.path.exists(filepath):
                    file_size = os.path.getsize(filepath) / (1024 * 1024)  # Size in MB
                    results.append({
                        'status': '✅ Berhasil',
                        'url': url,
                        'file': filename,
                        'size': f"{file_size:.1f} MB"
                    })
                    output_container.success(f"✅ [{current}/{total}] Download berhasil! ({file_size:.1f} MB)")
                else:
                    error_msg = result.stderr[:150] if result.stderr else "Unknown error"
                    results.append({
                        'status': '❌ Gagal',
                        'url': url,
                        'error': error_msg
                    })
                    output_container.error(f"❌ [{current}/{total}] Error: {error_msg}")
                    
            except subprocess.TimeoutExpired:
                results.append({
                    'status': '❌ Gagal',
                    'url': url,
                    'error': 'Timeout - file terlalu besar'
                })
                output_container.error(f"❌ [{current}/{total}] Error: Timeout")
            except Exception as e:
                error_msg = str(e)[:150]
                results.append({
                    'status': '❌ Gagal',
                    'url': url,
                    'error': error_msg
                })
                output_container.error(f"❌ [{current}/{total}] Error: {error_msg}")
            
            # Delay untuk hindari rate limit
            time.sleep(3)
            
            # Update progress
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
        
        status_text.success("✅ Semua proses selesai!")
        
        # Summary
        st.divider()
        col1, col2, col3 = st.columns(3)
        success_count = sum(1 for r in results if r['status'] == '✅ Berhasil')
        fail_count = sum(1 for r in results if r['status'] == '❌ Gagal')
        
        col1.metric("Berhasil", success_count)
        col2.metric("Gagal", fail_count)
        col3.metric("Total", len(results))
        
        # Show results detail
        if results:
            st.subheader("📋 Detail Hasil")
            for r in results:
                if r['status'] == '✅ Berhasil':
                    st.success(f"{r['status']} | {r['file']} | {r.get('size', 'N/A')}")
                else:
                    st.error(f"{r['status']} | {r['url']} | Error: {r.get('error', 'Unknown')}")
        
        # Download section
        st.divider()
        st.subheader("📥 Download Files")
        files_in_folder = sorted([f for f in os.listdir(temp_folder) if f.endswith('.mp4')], 
                                reverse=True)
        
        if files_in_folder:
            st.info(f"📁 {len(files_in_folder)} file tersedia untuk didownload")
            
            for file in files_in_folder[:len(results)]:
                filepath = os.path.join(temp_folder, file)
                file_size = os.path.getsize(filepath) / (1024 * 1024)
                
                with open(filepath, 'rb') as f:
                    st.download_button(
                        label=f"⬇️ {file} ({file_size:.1f} MB)",
                        data=f.read(),
                        file_name=file,
                        mime="video/mp4"
                    )
        else:
            st.warning("Tidak ada file tersedia")

st.divider()

# Info
with st.expander("ℹ️ Cara Menggunakan & Troubleshooting", expanded=False):
    st.markdown("""
    ### ✅ Cara Menggunakan:
    1. **Copy link reels** (tekan 3 titik → Share → Copy Link)
    2. **Paste URL** di kotak input (bisa multiple, satu per baris)
    3. **Klik "Mulai Download"** 
    4. **Download** file dengan tombol di bawah
    
    ### ⚠️ Jika Error:
    
    **"Rate limit reached"**
    - Tunggu 1-2 jam sebelum coba lagi
    - Gunakan VPN/IP baru
    - Jangan download terlalu banyak sekaligus
    
    **"Content is not available"**
    - Akun/reels private atau sudah dihapus
    - Cek apakah URL valid
    
    **"timeout"**
    - File terlalu besar (>500MB)
    - Internet koneksi lambat
    - Coba URL lain dulu
    
    ### 💡 Tips:
    - Download maksimal 5-10 URL sekaligus
    - Tunggu beberapa detik antar download
    - Reels Instagram format MP4
    - Ukuran file biasanya 10-100 MB
    """)

with st.expander("⚠️ Disclaimer & Terms", expanded=False):
    st.markdown("""
    - Hanya untuk **konten pribadi atau dengan izin creator**
    - **Patuhi ToS Instagram** dan hukum copyright setempat
    - **DMCA Policy**: Jangan gunakan untuk konten copyrighted
    - Tool ini **tidak bertanggung jawab** atas penyalahgunaan
    - Instagram bisa memblokir IP/akun dari download otomatis
    - Gunakan dengan bijak dan bertanggung jawab ✌️
    """)

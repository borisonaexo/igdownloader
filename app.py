import streamlit as st
from instagrapi import Client
import os
import time
from pathlib import Path

st.set_page_config(page_title="IG Reels Downloader", layout="wide")

st.title("📥 Instagram Reels Multiple Downloader")

st.warning("⚠️ Hanya download konten yang Anda punya izin. Patuhi ToS Instagram!")

# Create temp folder
temp_folder = "downloads"
os.makedirs(temp_folder, exist_ok=True)

# Sidebar untuk login
st.sidebar.subheader("🔐 Login Instagram")
username = st.sidebar.text_input("Username", type="default")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login", use_container_width=True):
    if username and password:
        try:
            with st.spinner("Logging in..."):
                client = Client()
                client.login(username, password)
                st.session_state.client = client
                st.session_state.username = username
                st.sidebar.success("✅ Login Berhasil!")
        except Exception as e:
            st.sidebar.error(f"❌ Login Gagal: {str(e)[:100]}")
    else:
        st.sidebar.error("Masukkan username & password!")

# Check login status
if 'client' in st.session_state:
    st.sidebar.success(f"✅ Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout", use_container_width=True):
        del st.session_state.client
        del st.session_state.username
        st.rerun()
else:
    st.sidebar.info("ℹ️ Login untuk hasil lebih baik (menghindari rate limit)")

st.divider()

# Main content
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
        if 'client' not in st.session_state:
            st.warning("⚠️ Tidak login. Coba tanpa login dulu (mungkin rate limit)...")
            client = Client()
        else:
            client = st.session_state.client
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        output_container = st.container()
        
        results = []
        
        for index, url in enumerate(urls_list):
            current = index + 1
            total = len(urls_list)
            
            status_text.info(f"⏳ [{current}/{total}] Processing: {url}")
            
            try:
                # Extract media ID
                if '/reels/' in url:
                    media_id = url.split('/reels/')[1].split('/')[0]
                elif '/p/' in url:
                    media_id = url.split('/p/')[1].split('/')[0]
                else:
                    raise ValueError("Format URL tidak valid")
                
                # Download
                try:
                    path = client.download_media_by_pk(int(media_id), temp_folder)
                    results.append({
                        'status': '✅ Berhasil',
                        'url': url,
                        'file': os.path.basename(path)
                    })
                    output_container.success(f"✅ [{current}/{total}] Download berhasil!")
                except Exception as e:
                    # Fallback: try dengan code
                    path = client.download_media_by_pk(int(media_id), temp_folder)
                    results.append({'status': '✅ Berhasil', 'url': url})
                    output_container.success(f"✅ [{current}/{total}] Download berhasil!")
                    
            except Exception as e:
                error_msg = str(e)[:100]
                results.append({
                    'status': '❌ Gagal',
                    'url': url,
                    'error': error_msg
                })
                output_container.error(f"❌ [{current}/{total}] Error: {error_msg}")
            
            # Delay untuk hindari rate limit
            time.sleep(2)
            
            # Update progress
            progress = int((current / total) * 100)
            progress_bar.progress(progress)
        
        status_text.success("✅ Download Selesai!")
        
        # Summary
        st.divider()
        col1, col2, col3 = st.columns(3)
        success_count = sum(1 for r in results if r['status'] == '✅ Berhasil')
        fail_count = sum(1 for r in results if r['status'] == '❌ Gagal')
        
        col1.metric("Berhasil", success_count)
        col2.metric("Gagal", fail_count)
        col3.metric("Total", len(results))
        
        # Download section
        st.subheader("📥 Download Files")
        files_in_folder = [f for f in os.listdir(temp_folder) 
                          if f.endswith(('.mp4', '.jpg', '.jpeg'))]
        
        if files_in_folder:
            st.info(f"📁 {len(files_in_folder)} file tersedia")
            
            for file in sorted(files_in_folder, reverse=True)[:len(results)]:
                filepath = os.path.join(temp_folder, file)
                with open(filepath, 'rb') as f:
                    mime_type = "video/mp4" if file.endswith('.mp4') else "image/jpeg"
                    st.download_button(
                        label=f"⬇️ {file}",
                        data=f.read(),
                        file_name=file,
                        mime=mime_type
                    )

st.divider()

# Info
with st.expander("ℹ️ Cara Menggunakan", expanded=False):
    st.markdown("""
    ### Cara Terbaik (dengan Login):
    1. **Masukkan username & password** di sidebar kiri
    2. **Klik Login**
    3. **Paste URL** reels (bisa multiple)
    4. **Klik Download** dan tunggu
    
    ### Tanpa Login:
    - Bisa, tapi rawan rate limit
    - Coba delay otomatis (sudah built-in)
    
    ### Tips:
    - Copy link dari Instagram (tekan 3 titik → Copy Link)
    - Account Instagram biasa bisa, tidak perlu bisnis
    - Jangan download bersamaan dengan banyak, tunggu
    """)

with st.expander("⚠️ Disclaimer", expanded=False):
    st.markdown("""
    - Hanya untuk personal/konten dengan izin
    - Patuhi ToS Instagram & hukum copyright
    - Tool ini tidak bertanggung jawab atas penyalahgunaan
    - Password hanya digunakan untuk login ke Instagram saja
    """)

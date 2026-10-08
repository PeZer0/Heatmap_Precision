# import streamlit as st
# from streamlit_image_coordinates 
import streamlit_image_coordinates
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from PIL import Image

st.set_page_config(layout="centered")
st.title("🎯 Shooting Heatmap Tracker")
st.write("Click anywhere on the target image to record a hit and update the heatmap.")

# 1. Initialize session storage to remember hits and track widget versions
if "shot_history" not in st.session_state:
    st.session_state.shot_history = []
if "tracker_version" not in st.session_state:
    st.session_state.tracker_version = 0

# 2. Setup your target image
try:
    target_img = Image.open("ISSF_25_meter_Precision_and_50_meter_pistol_target500x500.jpg")
except FileNotFoundError:
    target_img = Image.new("RGB", (600, 600), color=(240, 240, 240))
    
width, height = target_img.size

st.subheader("Record Your Hits")

# 3. Display the image with a DYNAMIC KEY that changes on reset
widget_key = f"target_click_v{st.session_state.tracker_version}"
value = streamlit_image_coordinates(target_img, key=widget_key)

# 4. Process new click data
if value is not None:
    new_hit = {"x": value["x"], "y": value["y"]}
    # Prevent duplicate records from the same click event
    if not st.session_state.shot_history or st.session_state.shot_history[-1] != new_hit:
        st.session_state.shot_history.append(new_hit)
        st.rerun()

# 5. Build and display the statistics and heatmap
if st.session_state.shot_history:
    df = pd.DataFrame(st.session_state.shot_history)
    
    # 💡 Add 2 inside the parentheses to define the number of columns
    col1, col2 = st.columns(2) 
    
    with col1:
        st.metric(label="Total Shots Tracked", value=len(df))

        
        # FIXED RESET BUTTON LOGIC:
        if st.button("Reset Tracker", type="primary"):
            st.session_state.shot_history = []          # Clear the history
            st.session_state.tracker_version += 1        # Force a brand new widget instance
            st.rerun()
            
        st.write("Recent coordinates:", df.tail(5))

    with col2:
        st.subheader("Generated Heatmap")
        
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(target_img, extent=[0, width, height, 0]) 
        
        sns.kdeplot(
            data=df, x="x", y="y", 
            fill=True, thresh=0.05, alpha=0.6, cmap="rocket", 
            ax=ax, cbar=False
        )
        
        ax.scatter(df["x"], df["y"], color="cyan", edgecolor="black", s=30, label="Exact Hits")
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        ax.axis("off")
        
        st.pyplot(fig)
else:
    st.info("No shots recorded yet. Click on the image canvas above to start mapping!")

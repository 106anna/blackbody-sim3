import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# 網頁基本設定
st.set_page_config(page_title="黑體輻射與人類視覺模擬器", layout="centered")

# --- 物理常數與基準值 ---
h, c, kB = 6.626e-34, 3.0e8, 1.38e-23
sigma = 5.67e-8  
T_sun = 5773     
P_sun = sigma * (T_sun**4) 

st.title("🌡️ 黑體輻射與人類視覺敏感度模擬")
st.markdown("---")

# 1. 數值輸入框
temp_k = st.number_input("輸入絕對溫度 (Kelvin):", min_value=100, max_value=20000, value=5773, step=100)

# 2. 物理計算
total_intensity = sigma * (temp_k**4)
ratio_to_sun = total_intensity / P_sun
peak_wave_nm = (2.898e-3 / temp_k) * 1e9

# 3. 數據分析 (數據顯示於上方)
st.subheader("📊 實驗數據分析")
col1, col2 = st.columns(2)
with col1:
    st.metric("坡峰波長 (Peak)", f"{peak_wave_nm:.1f} nm")
    st.write(f"**總輻射強度:** \n {total_intensity:.2e} W/m²")
with col2:
    st.metric("相對於太陽比值", f"{ratio_to_sun:.3f} 倍")

# 4. 繪圖準備
waves_nm = np.linspace(300, 2000, 1000) # 聚焦在可見光與近紅外
waves_m = waves_nm * 1e-9
with np.errstate(over='ignore', divide='ignore'):
    intensity = (2 * h * c**2) / (waves_m**5 * (np.exp((h * c) / (waves_m * kB * temp_k)) - 1))

# 🌟 模擬錐狀細胞敏感曲線 (S, M, L)
def cone_sensitivity(x, peak, width):
    return np.exp(-0.5 * ((x - peak) / width)**2)

s_cone = cone_sensitivity(waves_nm, 440, 30) # 藍色
m_cone = cone_sensitivity(waves_nm, 545, 40) # 綠色
l_cone = cone_sensitivity(waves_nm, 570, 45) # 紅色

# 5. 繪製圖表
fig, ax = plt.subplots(figsize=(10, 6))

# 設定背景為深色
ax.set_facecolor('#f0f0f0')

# 繪製彩虹背景 (400-700nm)
vis_min, vis_max = 400, 700
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))
ax.imshow(gradient, aspect='auto', cmap=cm.rainbow, alpha=0.15,
          extent=[vis_min, vis_max, 0, np.max(intensity) * 1.2], zorder=0)

# 繪製黑體輻射曲線
ax.plot(waves_nm, intensity, color='black', lw=3, label='Blackbody Spectrum', zorder=10)

# 繪製錐狀細胞敏感曲線 (次座標軸，讓形狀更明顯)
ax2 = ax.twinx()
ax2.plot(waves_nm, l_cone, color='red', lw=1.5, ls='--', alpha=0.5, label='L-Cone (Red)')
ax2.plot(waves_nm, m_cone, color='green', lw=1.5, ls='--', alpha=0.5, label='M-Cone (Green)')
ax2.plot(waves_nm, s_cone, color='blue', lw=1.5, ls='--', alpha=0.5, label='S-Cone (Blue)')
ax2.set_ylabel("Cone Cell Sensitivity", color='gray')
ax2.set_ylim(0, 1.5)

# 標註坡峰
ax.axvline(peak_wave_nm, color='darkred', linestyle=':', alpha=0.7, zorder=11)

# 圖表美化
ax.set_xlabel("Wavelength (nm)", fontsize=12)
ax.set_ylabel("Spectral Radiance", fontsize=12)
ax.set_title(f"Blackbody vs. Human Eye Sensitivity ({temp_k} K)", fontsize=14)
ax.set_xlim(350, 1500)
ax.set_ylim(0, np.max(intensity) * 1.2)
ax.grid(True, linestyle=':', alpha=0.5)

# 組合圖例
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines + lines2, labels + labels2, loc='upper right', fontsize='small')

st.pyplot(fig)

st.info("💡 **教學觀察點：** 太陽溫度約為 5773 K。觀察黑體曲線的峰值如何與三種錐狀細胞的敏感區域重疊，這就是為什麼我們演化出能看見此範圍『可見光』的原因。")

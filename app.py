import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 網頁基本設定
st.set_page_config(page_title="黑體輻射與人類視覺模擬", layout="centered")

# --- 物理常數與基準值 ---
h, c, kB = 6.626e-34, 3.0e8, 1.38e-23
sigma = 5.67e-8  
T_sun = 5773     
P_sun = sigma * (T_sun**4) 

st.title("🌡️ 黑體輻射與人類視覺敏感度模擬")
st.markdown("---")

# 1. 數值輸入框
temp_k = st.number_input("請輸入絕對溫度 (Kelvin):", min_value=100, max_value=20000, value=5773, step=100)

# 2. 物理計算
total_intensity = sigma * (temp_k**4)
ratio_to_sun = total_intensity / P_sun
peak_wave_nm = (2.898e-3 / temp_k) * 1e9

# 3. 數據分析顯示 (顯示於上方)
st.subheader("📊 模擬結果")
col1, col2 = st.columns(2)
with col1:
    st.metric("波峰波長 (Peak)", f"{peak_wave_nm:.1f} nm")
    st.write(f"**總輻射強度:** \n {total_intensity:.2e} W/m²")
with col2:
    st.metric("相對於太陽光度比值", f"{ratio_to_sun:.3f} L☉")

# 4. 繪圖準備
waves_nm = np.linspace(300, 2000, 1000)
waves_m = waves_nm * 1e-9
with np.errstate(over='ignore', divide='ignore'):
    intensity = (2 * h * c**2) / (waves_m**5 * (np.exp((h * c) / (waves_m * kB * temp_k)) - 1))

# 模擬錐狀細胞敏感曲線公式
def cone_sensitivity(x, peak, width):
    return np.exp(-0.5 * ((x - peak) / width)**2)

# 5. 繪製圖表
fig, ax1 = plt.subplots(figsize=(10, 6))

# --- 左側 Y 軸：輻射強度 ---
ax1.set_xlabel("Wavelength (nm)", fontsize=12)
ax1.set_ylabel("Radiant Intensity (W/m²/m)", fontsize=12, color='black')
ax1.plot(waves_nm, intensity, color='black', lw=3, label='Blackbody Spectrum', zorder=10)
ax1.tick_params(axis='y', labelcolor='black')

# 🌈 繪製彩虹背景 (400-700nm)
vis_min, vis_max = 400, 700
for w in range(vis_min, vis_max):
    color = plt.cm.rainbow((w - vis_min) / (vis_max - vis_min))
    ax1.axvspan(w, w+1, color=color, alpha=0.15, lw=0)

# 📍 垂直虛線指出目前的坡峰位置
ax1.axvline(peak_wave_nm, color='darkred', linestyle=':', lw=2, alpha=0.8, label=f'Peak ({peak_wave_nm:.1f}nm)')

# --- 右側 Y 軸：SML 相對敏感度 ---
ax2 = ax1.twinx()
ax2.set_ylabel("Relative Sensitivity (0 to 1)", fontsize=12, color='gray')
ax2.plot(waves_nm, cone_sensitivity(waves_nm, 570, 45), color='red', lw=1.5, ls='--', alpha=0.6)
ax2.plot(waves_nm, cone_sensitivity(waves_nm, 545, 40), color='green', lw=1.5, ls='--', alpha=0.6)
ax2.plot(waves_nm, cone_sensitivity(waves_nm, 440, 30), color='blue', lw=1.5, ls='--', alpha=0.6)
ax2.tick_params(axis='y', labelcolor='gray')

# 🌟 SML 標籤位置：懸浮於各自波峰上方 (1.02 處)，不碰到線
label_y_pos = 1.02
ax2.text(570, label_y_pos, 'L', color='red', fontweight='bold', fontsize=15, ha='center', va='bottom')
ax2.text(545, label_y_pos, 'M', color='green', fontweight='bold', fontsize=15, ha='center', va='bottom')
ax2.text(440, label_y_pos, 'S', color='blue', fontweight='bold', fontsize=15, ha='center', va='bottom')

# 設定軸範圍與美化
ax1.set_xlim(350, 1500)
ax1.set_ylim(0, np.max(intensity) * 1.25) # 預留空間給標籤
ax2.set_ylim(0, 1.2) # 敏感度上限設為 1.2 以騰出標籤空間
ax1.grid(True, linestyle=':', alpha=0.5)

# 合併圖例
lines1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(lines1, labels1, loc='upper right', fontsize='small')

st.pyplot(fig)

# 6. 教學重點觀察 (依您的要求修改)
st.markdown(f"""
### 💡 教學重點觀察：
1. **人類視覺錐狀細胞 (Cone Cells) 說明：**
* **S (Short-wave)**：短波長敏感，峰值約 **440 nm**，對應 **藍光**。
* **M (Medium-wave)**：中波長敏感，峰值約 **545 nm**，對應 **綠光**。
* **L (Long-wave)**：長波長敏感，峰值約 **570 nm**，對應 **紅光**。。
2. **當溫度設為 **5773 K** (太陽) 時**：請注意黑色輻射曲線的最強峰值位置。你會發現它精準地落在 **M** 與 **L** 錐狀細胞最敏感的區域之間，這體現了生物演化對太陽光環境的適應。
3. **若低色溫的暖黃光燈泡，溫度為 **2773 K****：能量分佈會如何變化？
""")

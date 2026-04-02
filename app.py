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

# 3. 數據分析顯示
st.subheader("📊 實驗數據分析")
col1, col2 = st.columns(2)
with col1:
    st.metric("坡峰波長 (Peak)", f"{peak_wave_nm:.1f} nm")
    st.write(f"**總輻射強度:** \n {total_intensity:.2e} W/m²")
with col2:
    st.metric("相對於太陽比值", f"{ratio_to_sun:.3f} 倍")

# 4. 繪圖準備
waves_nm = np.linspace(300, 2000, 1000)
waves_m = waves_nm * 1e-9
with np.errstate(over='ignore', divide='ignore'):
    intensity = (2 * h * c**2) / (waves_m**5 * (np.exp((h * c) / (waves_m * kB * temp_k)) - 1))

# 模擬錐狀細胞敏感曲線公式
def cone_sensitivity(x, peak, width):
    return np.exp(-0.5 * ((x - peak) / width)**2)

# 5. 繪製圖表
fig, ax = plt.subplots(figsize=(10, 6))

# 繪製彩虹背景 (400-700nm)
vis_min, vis_max = 400, 700
for w in range(vis_min, vis_max):
    color = plt.cm.rainbow((w - vis_min) / (vis_max - vis_min))
    ax.axvspan(w, w+1, color=color, alpha=0.15, lw=0)

# 繪製黑體輻射曲線
ax.plot(waves_nm, intensity, color='black', lw=3, label='Blackbody Spectrum', zorder=10)

# 使用次座標軸標繪 S, M, L 錐狀細胞
ax2 = ax.twinx()
# L: Long-wave (Red)
ax2.plot(waves_nm, cone_sensitivity(waves_nm, 570, 45), color='red', lw=1.5, ls='--', alpha=0.6, label='L-Cone (Red)')
# M: Medium-wave (Green)
ax2.plot(waves_nm, cone_sensitivity(waves_nm, 545, 40), color='green', lw=1.5, ls='--', alpha=0.6, label='M-Cone (Green)')
# S: Short-wave (Blue)
ax2.plot(waves_nm, cone_sensitivity(waves_nm, 440, 30), color='blue', lw=1.5, ls='--', alpha=0.6, label='S-Cone (Blue)')

# 加上文字標籤 (S, M, L)
ax2.text(585, 0.95, 'L', color='red', fontweight='bold', fontsize=12)
ax2.text(540, 0.95, 'M', color='green', fontweight='bold', fontsize=12)
ax2.text(430, 0.95, 'S', color='blue', fontweight='bold', fontsize=12)

ax2.set_ylim(0, 1.5)
ax2.set_yticks([]) # 隱藏數值，純看形狀

# 圖表美化
ax.set_xlabel("Wavelength (nm)", fontsize=12)
ax.set_ylabel("Spectral Radiance", fontsize=12)
ax.set_xlim(350, 1500)
ax.set_ylim(0, np.max(intensity) * 1.1)
ax.grid(True, linestyle=':', alpha=0.5)
ax.legend(loc='upper right', fontsize='small')

st.pyplot(fig)

st.markdown("""
### 💡 教學重點觀察：
1. **S-M-L 錐狀細胞**：分別對應短、中、長波長，這是人類感受色彩的基礎。
2. **當溫度設為 **5773 K** (太陽) 時：請注意黑體輻射的最強峰值位置與**Ｓ,M和L** 細胞最敏感的區域相對位置
3. **若低色溫的暖黃光燈泡，溫度為 **2773 K**：則能量有何變化？
""")

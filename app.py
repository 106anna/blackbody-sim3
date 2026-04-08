import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 網頁基本設定：增加頁面快取與效能優化
st.set_page_config(page_title="黑體輻射與色彩模擬器", layout="centered")

# --- 1. 物理常數與緩存計算 ---
# 使用緩存：這些基礎曲線（SML）對所有人都是一樣的，算一次就好
@st.cache_data
def get_base_curves():
    waves_nm = np.linspace(380, 780, 400)
    # 預先計算 SML 細胞敏感度
    s_sens = np.exp(-0.5 * ((waves_nm - 440) / 30)**2)
    m_sens = np.exp(-0.5 * ((waves_nm - 545) / 40)**2)
    l_sens = np.exp(-0.5 * ((waves_nm - 570) / 45)**2)
    return waves_nm, s_sens, m_sens, l_sens

# 緩存普朗克定律計算
@st.cache_data
def calculate_planck(temp_k, waves_nm):
    h, c, kB = 6.626e-34, 3.0e8, 1.38e-23
    waves_m = waves_nm * 1e-9
    with np.errstate(over='ignore', divide='ignore'):
        intensity = (2 * h * c**2) / (waves_m**5 * (np.exp((h * c) / (waves_m * kB * temp_k)) - 1))
    return intensity

# --- 2. 啟動計算 ---
waves_nm, s_sens, m_sens, l_sens = get_base_curves()

st.title("🌡️ 黑體輻射與視覺顏色")
st.markdown("---")

# 數值輸入
temp_k = st.number_input("請輸入絕對溫度 (Kelvin):", min_value=100, max_value=20000, value=5773, step=100)

# 取得黑體輻射強度
intensity_vis = calculate_planck(temp_k, waves_nm)

# --- 3. 核心邏輯：計算重疊總面積 (積分) ---
def get_integral(y, x):
    if hasattr(np, 'trapezoid'):
        return np.trapezoid(y, x)
    return np.trapz(y, x)

S_val = get_integral(intensity_vis * s_sens, waves_nm)
M_val = get_integral(intensity_vis * m_sens, waves_nm)
L_val = get_integral(intensity_vis * l_sens, waves_nm)

# 正規化
max_val = max(S_val, M_val, L_val, 1e-10)
S_norm, M_norm, L_norm = S_val/max_val, M_val/max_val, L_val/max_val

# 顏色模擬
r, g, b = min(L_norm * 1.1, 1.0), min(M_norm * 1.0, 1.0), min(S_norm * 0.9, 1.0)
hex_color = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

# --- 4. 介面顯示 ---
c1, c2, c3 = st.columns(3)
c1.metric("S 響應 (藍)", f"{S_norm:.3f}")
c2.metric("M 響應 (綠)", f"{M_norm:.3f}")
c3.metric("L 響應 (紅)", f"{L_norm:.3f}")

st.markdown(f"""
<div style="background-color: {hex_color}; height: 80px; border-radius: 10px; 
            display: flex; align-items: center; justify-content: center;
            border: 2px solid #333; color: {'black' if (r+g+b)>1.5 else 'white'}; font-weight: bold; font-size: 20px;">
    模擬黑體輻射與視覺ＳＭＬ錐狀細胞 (T={temp_k}K)
</div>
""", unsafe_allow_html=True)

# --- 5. 繪製圖表 (確保多人使用不卡頓) ---
# 使用具備 thread-safe 的方式建立 fig
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.set_xlabel("Wavelength (nm)")
ax1.set_ylabel("Radiant Intensity", color='black')
ax1.plot(waves_nm, intensity_vis, color='black', lw=3, label='Blackbody Spectrum')

peak_nm = (2.898e-3 / temp_k) * 1e9
ax1.axvline(peak_nm, color='darkred', ls=':', lw=2, label=f'Peak: {peak_nm:.1f}nm')

ax2 = ax1.twinx()
ax2.set_ylabel("Relative Sensitivity", color='gray')
ax2.plot(waves_nm, l_sens, color='red', ls='--', alpha=0.5)
ax2.plot(waves_nm, m_sens, color='green', ls='--', alpha=0.5)
ax2.plot(waves_nm, s_sens, color='blue', ls='--', alpha=0.5)

# 標籤偏移
ax2.text(570 + 12, 1.0, 'L', color='red', fontweight='bold', ha='left', va='center')
ax2.text(545 - 12, 1.0, 'M', color='green', fontweight='bold', ha='right', va='center')
ax2.text(440 + 12, 1.0, 'S', color='blue', fontweight='bold', ha='left', va='center')

ax2.set_ylim(0, 1.2)
ax1.set_ylim(0, np.max(intensity_vis) * 1.35)
ax1.set_xlim(350, 850)
ax1.legend(loc='upper right')

st.pyplot(fig)
plt.close(fig) # 重要：釋放記憶體，確保多人連線不崩潰

# --- 6. 教學資訊 ---
st.info("💡 **科學原理：** SML 響應值代表黑色能量曲線與 SML 曲線重疊部分的**總面積**。")
st.markdown("### 🎓 思考練習：\n1. 太陽 (5773K) 的波峰在綠色，為何 L 響應卻最強？\n2. 當溫度降低，重疊面積發生了什麼變化？")

# --- 6. 教學資訊區 ---
st.info("""
**💡 數據背後的科學原理：**
* **SML 響應值**：並非直接對應圖上的「點」，而是**計算了黑色輻射能量曲線與 SML 虛線重疊部分的總面積**（即積分）。這代表了視覺細胞接收到的總刺激能量。
* **色彩判定**：大腦根據 S:M:L 的**面積比例**來解碼色彩。
* **S (Short-wave)**：短波長敏感，峰值約 **440 nm**，對應 **藍光**。
* **M (Medium-wave)**：中波長敏感，峰值約 **545 nm**，對應 **綠光**。
* **L (Long-wave)**：長波長敏感，峰值約 **570 nm**，對應 **紅光**。。
""")

st.markdown(f"""
### 🎓 思考練習：
1. **觀察黑體輻射曲線的形狀**：雖然太陽 (5773K) 的坡峰在綠色區域，但請對比黑色曲線在「短波長(左)」與「長波長(右)」的衰減速度，這如何影響了 **L 響應** 的總面積？
2. **觀察能量偏移**：當溫度調低至燈泡 (2773K) 時，黑色輻射曲線與 **S、M、L** 三條虛線的重疊面積分別發生了什麼變化？這與我們看到的橘黃色有什麼關聯？
""")

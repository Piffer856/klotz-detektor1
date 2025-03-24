import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Benutzerdefinierte Graustufen-Colormap
def get_custom_colormap():
    return mcolors.LinearSegmentedColormap.from_list("custom_gray", ["#eeeeee", "#000000"])

# Schattenberechnung basierend auf Klotzpositionen und Winkeln
def berechne_shadow_score(cubes, angles):
    board_x = np.zeros((5, 5))
    origin_offset = 12.5

    for angle in angles:
        angle_neu = angle + 45 if angle <= 90 else angle - 45
        d = np.sqrt(2) * 5
        halb_schattenbreite = np.sqrt((d - d / 2 * (1 + np.cos(np.radians(angle_neu)))) *
                                      (d / 2 * (1 + np.cos(np.radians(angle_neu))))) - 0.1

        if angle == 0:
            intervals = [(x - halb_schattenbreite, x + halb_schattenbreite) for x, y in cubes]
        elif angle == 90:
            intervals = [(y - halb_schattenbreite, y + halb_schattenbreite) for x, y in cubes]
        else:
            projections = [x * np.cos(np.radians(angle)) + y * np.sin(np.radians(angle)) for x, y in cubes]
            intervals = [(p - halb_schattenbreite, p + halb_schattenbreite) for p in projections]

        temp_board = np.zeros((5, 5))
        for min_val, max_val in intervals:
            for i in range(5):
                for j in range(5):
                    x_center = (i * 5 + 2.5) - origin_offset
                    y_center = origin_offset - (j * 5 + 2.5)
                    if angle == 0 and min_val <= x_center <= max_val:
                        temp_board[j, i] = 1
                    elif angle == 90 and min_val <= y_center <= max_val:
                        temp_board[j, i] = 1
                    elif angle not in [0, 90]:
                        projection = x_center * np.cos(np.radians(angle)) + y_center * np.sin(np.radians(angle))
                        if min_val <= projection <= max_val:
                            temp_board[j, i] = 1
        board_x += temp_board

    shadow_score = board_x / len(angles)
    return shadow_score

# Visualisierung der Rückprojektion mit erkannten Klötzen
def zeige_plot(shadow_score, threshold):
    fig, ax = plt.subplots(figsize=(6, 6))
    cmap = get_custom_colormap()

    ax.imshow(shadow_score[::-1], cmap=cmap, origin="lower",
              extent=[-12.5, 12.5, -12.5, 12.5], vmin=0, vmax=1)

    for i in range(6):
        ax.axhline(-12.5 + i * 5, color="black", linewidth=1)
        ax.axvline(-12.5 + i * 5, color="black", linewidth=1)

    ax.set_xticks(np.linspace(-10, 10, 5))
    ax.set_xticklabels(["A", "B", "C", "D", "E"])
    ax.set_yticks(np.linspace(-10, 10, 5))
    ax.set_yticklabels(["1", "2", "3", "4", "5"])
    ax.set_title("Schattenrückprojektion & erkannte Klötze")

    for i in range(5):
        for j in range(5):
            if shadow_score[j, i] >= threshold:
                x = i * 5 - 10
                y = -(j * 5 - 10)
                ax.plot(x, y, 'ro', markersize=12)

    st.pyplot(fig)

# Streamlit App
def main():
    st.title("Rückprojektion & Klotz-Erkennung")
    st.markdown("Diese App berechnet die Rückprojektion von Schatten auf einem 5x5-Brett und erkennt automatisch die wahrscheinlichen Klotzpositionen.")

    # Auswahl der Standard-Würfelpositionen
    use_standard = st.checkbox("Standard-Würfelpositionen verwenden (C2, C3, D2)?", value=True)
    cubes = []
    if use_standard:
        cubes = [(3 * 5 - 15, 2 * 5 - 15), (2 * 5 - 10, 3 * 5 - 15), (3 * 5 - 10, 2 * 5 - 15)]
    else:
        st.info("Benutzerdefinierte Eingabe ist aktuell nicht aktiviert in dieser Version.")

    # Winkel-Auswahl
    angles = st.multiselect("Wähle Messwinkel (Grad):", options=list(range(0, 181, 10)), default=[0, 45, 90, 135])

    # Schwellwert-Slider
    threshold = st.slider("Schwellwert für Klotz-Erkennung", min_value=0.1, max_value=1.0, value=0.8, step=0.01)

    if angles:
        shadow_score = berechne_shadow_score(cubes, angles)
        zeige_plot(shadow_score, threshold)
    else:
        st.warning("Bitte mindestens einen Winkel auswählen.")

if __name__ == "__main__":
    main()

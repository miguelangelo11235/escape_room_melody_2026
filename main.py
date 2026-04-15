# main.py
import tkinter as tk
import numpy as np
import sounddevice as sd
import hashlib

from config import NOTES, MELODY, TIMING
from frames import FRAMES_DATA

# Hashes de solución para validación interna:
HASH_FREQUENCY = "77cd246edf61e041c086f04c4c304fcbb94f5ec9c53a1f02bd9b73d3fd2a8043"
HASH_PATTERN = "84154970c18bf59af4c4456196764cff20cfc0e87ed7b490b850f8d76f61bf92"
HASH_TIMING_08 = "1e9d7c27c8bbc8ddf0055c93e064a62fa995d177fee28cc8fa949bc8a4db06f4"
HASH_TIMING_080 = "97ef31b3437e4070a2ea9c2bfb19fc63941d3ae6a0bb731ab4abdb6c1e55139a"


def validate_state():
    """Valida los acertijos enfocándose en los errores específicos."""
    missing = []
    incorrect = []

    # Puzzle 1: Frequency
    val_note = NOTES.get('note_unknown')
    if val_note is None:
        missing.append("Frecuencia")
    else:
        if hashlib.sha256(str(val_note).encode('utf-8')).hexdigest() != HASH_FREQUENCY:
            incorrect.append("Frecuencia")

    # Puzzle 2: Melody Pattern
    if len(MELODY) == 16:
        missing.append("Melodía")
    else:
        current_pattern = ",".join(MELODY)
        if hashlib.sha256(current_pattern.encode('utf-8')).hexdigest() != HASH_PATTERN:
            incorrect.append("Melodía")

    # Puzzle 3: Timing
    if None in TIMING or len(TIMING) < 17:
        missing.append("Ritmo")
    else:
        val_time = str(TIMING[-1])
        thash = hashlib.sha256(val_time.encode('utf-8')).hexdigest()
        if thash not in [HASH_TIMING_08, HASH_TIMING_080]:
            incorrect.append("Ritmo")

    # Determine Global State based on SPECIFIC errors
    if incorrect:
        msg = "¡INCORRECTO en:\n" + "\n".join(f"- {i}" for i in incorrect) + "!"
        return "ERROR", msg, False

    if missing:
        if len(missing) == 3:
            return "TRISTE", "¡Comienza a\nresolver los 3\nacertijos!", False
        else:
            msg = "¡Vas bien!\nTe falta:\n" + "\n".join(f"- {m}" for m in missing)
            return "ESPERA", msg, False

    return "VICTORIA", "¡VICTORY!", True


def generate_note(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * max(0, duration)), False)
    if not freq or freq == 0.0: return np.zeros_like(t)
    wave = 0.3 * np.sign(np.sin(2 * np.pi * freq * t))
    attack_time, release_time = 0.015, 0.05
    attack_samples = int(attack_time * sample_rate)
    release_samples = int(release_time * sample_rate)
    envelope = np.ones_like(t)
    if len(t) > attack_samples + release_samples:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    return wave * envelope


def play_error_sound():
    sample_rate = 44100
    t = np.linspace(0, 1.0, sample_rate, False)
    wave = 0.1 * (np.sin(2 * np.pi * 300 * t) + np.sin(2 * np.pi * 315 * t) + np.sin(2 * np.pi * 330 * t))
    sd.play(wave, samplerate=sample_rate)


def play_success_sound():
    sample_rate = 44100
    audio_buffer = []
    # Play safely by zipping through internally provided definitions
    for m, t in zip(MELODY, TIMING):
        freq = NOTES.get(m, 0.0) or 0.0
        audio_buffer.append(generate_note(freq, float(t) if t is not None else 0.0, sample_rate))

    if audio_buffer:
        sd.play(np.concatenate(audio_buffer), samplerate=sample_rate)


def start_audio(state_id):
    if state_id == "ERROR":
        play_error_sound()
    elif state_id == "VICTORIA":
        play_success_sound()


def launch_ui(state_id, message):
    root = tk.Tk()
    root.title("Escape Room Melody")
    root.geometry("600x450")
    root.configure(bg="black")
    root.resizable(False, False)

    color_titulo = "gold" if state_id == "VICTORIA" else ("red" if state_id == "ERROR" else "white")

    title_label = tk.Label(root, text=message, font=("Courier", 18, "bold"), fg=color_titulo, bg="black")
    title_label.pack(pady=20)

    canvas = tk.Canvas(root, width=200, height=200, bg="black", highlightthickness=0)
    canvas.pack(pady=10)

    # Load from external frames.py
    colors, frame_1, frame_2, delay = FRAMES_DATA[state_id]

    frames = [frame_1, frame_2]
    current_frame = [0]
    cell_size = 20

    def draw_frame():
        canvas.delete("all")
        for y, row in enumerate(frames[current_frame[0]]):
            for x, val in enumerate(row):
                if val != 0:
                    x0, y0 = x * cell_size, y * cell_size
                    canvas.create_rectangle(x0, y0, x0 + cell_size, y0 + cell_size, fill=colors[val], outline="")
        current_frame[0] = (current_frame[0] + 1) % len(frames)
        root.after(delay, draw_frame)

    draw_frame()
    root.mainloop()


if __name__ == "__main__":
    state_id, message, is_success = validate_state()
    start_audio(state_id)
    launch_ui(state_id, message)

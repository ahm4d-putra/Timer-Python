import sys
import tkinter as tk
from tkinter import ttk, messagebox


def is_windows() -> bool:
    return sys.platform.startswith("win")


class StudyTimerApp(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.title("Waktu Belajar")
        self.geometry("420x260")
        self.minsize(380, 240)
        self.configure(padx=16, pady=16)

        # Variabel Timer
        self.total_seconds: int = 0
        self.remaining_seconds: int = 0
        self.is_running: bool = False
        self._after_job: str | None = None

        # Variabel UI
        self.duration_var = tk.StringVar(value="25:00")
        self.time_display_var = tk.StringVar(value="00:00:00")

        self._build_ui()
        self._update_buttons_state()

    # --------------------------- TAMPILAN USER --------------------------- #
    def _build_ui(self) -> None:
        header = ttk.Label(self, text="Timer Belajar", font=("Segoe UI", 14, "bold"))
        header.pack(anchor="w", pady=(0, 8))

        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x")

        duration_label = ttk.Label(form_frame, text="Durasi (dalam jumlah menit atau format mm:ss, hh:mm:ss):")
        duration_label.grid(row=0, column=0, sticky="w")

        duration_entry = ttk.Entry(form_frame, textvariable=self.duration_var)
        duration_entry.grid(row=1, column=0, sticky="ew")
        form_frame.columnconfigure(0, weight=1)

        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill="x", pady=10)

        self.start_button = ttk.Button(buttons_frame, text="Start", command=self.start_timer)
        self.pause_button = ttk.Button(buttons_frame, text="Pause", command=self.pause_timer)
        self.reset_button = ttk.Button(buttons_frame, text="Reset", command=self.reset_timer)

        self.start_button.grid(row=0, column=0, padx=(0, 8))
        self.pause_button.grid(row=0, column=1, padx=8)
        self.reset_button.grid(row=0, column=2, padx=(8, 0))

        display_frame = ttk.Frame(self)
        display_frame.pack(fill="x", pady=(4, 10))

        time_label = ttk.Label(
            display_frame,
            textvariable=self.time_display_var,
            anchor="center",
            font=("Consolas", 28, "bold"),
        )
        time_label.pack(fill="x")

        self.progress = ttk.Progressbar(self, maximum=1, value=0)
        self.progress.pack(fill="x")

        

    # ------------------------ Logika Timer ----------------------- #
    def start_timer(self) -> None:
        """Mulai atau lanjutkan timer."""
        if self.is_running:
            return

        # Jika belum ada waktu total (baru akan mulai), parse dari input
        if self.remaining_seconds == 0:
            parsed = self._parse_duration_to_seconds(self.duration_var.get().strip())
            if parsed <= 0:
                messagebox.showwarning("Durasi tidak valid", "Masukkan durasi lebih dari 0 detik.")
                return
            self.total_seconds = parsed
            self.remaining_seconds = parsed
            self.progress.configure(maximum=self.total_seconds, value=0)
            self._update_time_display(self.remaining_seconds)

        self.is_running = True
        self._update_buttons_state()
        self._schedule_tick()

    def pause_timer(self) -> None:
        if not self.is_running:
            return
        self.is_running = False
        if self._after_job is not None:
            self.after_cancel(self._after_job)
            self._after_job = None
        self._update_buttons_state()

    def reset_timer(self) -> None:
        self.is_running = False
        if self._after_job is not None:
            self.after_cancel(self._after_job)
            self._after_job = None
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.progress.configure(value=0)
        self._update_time_display(0)
        self._update_buttons_state()

    def _schedule_tick(self) -> None:
        self._after_job = self.after(1000, self._tick)

    def _tick(self) -> None:
        if not self.is_running:
            return

        if self.remaining_seconds <= 0:
            # Selesai
            self.is_running = False
            self._update_buttons_state()
            self._on_finished()
            return

        self.remaining_seconds -= 1
        self._update_time_display(self.remaining_seconds)
        self.progress.configure(value=(self.total_seconds - self.remaining_seconds))
        self._schedule_tick()

    # -------------------------- Utils ------------------------- #
    def _update_time_display(self, seconds: int) -> None:
        self.time_display_var.set(self._format_seconds(seconds))

    def _update_buttons_state(self) -> None:
        self.start_button.state(("!disabled",)) if not self.is_running else self.start_button.state(("disabled",))
        self.pause_button.state(("!disabled",)) if self.is_running else self.pause_button.state(("disabled",))
        # Reset aktif jika ada sisa/total waktu
        if self.total_seconds > 0 or self.remaining_seconds > 0:
            self.reset_button.state(("!disabled",))
        else:
            self.reset_button.state(("disabled",))

    def _on_finished(self) -> None:
        self.progress.configure(value=self.total_seconds)
        self._update_time_display(0)
        self._play_alarm()
        messagebox.showinfo("Selesai", "Waktu belajar selesai! Bagus kerja kerasnya.")

    def _play_alarm(self) -> None:
        """Mainkan suara peringatan. Di Windows gunakan winsound; fallback ke bell."""
        if is_windows():
            try:
                import winsound  # type: ignore

                # Jadwalkan beberapa beep agar tidak memblok UI
                for i in range(5):
                    self.after(i * 350, lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION))
                return
            except Exception:
                pass
        # Fallback
        for i in range(5):
            self.after(i * 350, self.bell)

    @staticmethod
    def _parse_duration_to_seconds(text: str) -> int:
        if not text:
            return 0

        parts = text.split(":")
        try:
            if len(parts) == 1:
                minutes = int(parts[0])
                return max(0, minutes * 60)
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                return max(0, minutes * 60 + seconds)
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return max(0, hours * 3600 + minutes * 60 + seconds)
        except ValueError:
            return 0
        return 0

    @staticmethod
    def _format_seconds(total_seconds: int) -> str:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    app = StudyTimerApp()
    app.mainloop()

